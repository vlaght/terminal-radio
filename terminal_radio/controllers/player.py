import threading
import time
import subprocess
import sounddevice as sd
import numpy as np
from queue import Queue


class AudioStreamingError(Exception):
    pass


class AudioStreamer:
    """Audio streamer using ffmpeg and sounddevice."""

    def __init__(self):
        self._process = None
        self._volume = 1.0
        self._is_playing = False
        self._thread = None
        self._last_chunk_time = 0
        self._error_queue = Queue()
        self._current_audio_data = np.ndarray([0] * 32)

    @property
    def current_audio_data(self) -> np.ndarray | None:
        """Get current audio data for visualization."""
        return self._current_audio_data

    def play(self, url: str) -> None:
        """Start streaming audio from the given URL."""
        if self._is_playing:
            self.stop()
            # Wait for previous thread to finish
            if self._thread and self._thread.is_alive():
                self._thread.join()

        try:
            self._process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i",
                    url,
                    "-acodec",
                    "pcm_s16le",
                    "-f",
                    "s16le",
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    "-bufsize",
                    "4096",
                    "pipe:1",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Changed to PIPE to capture errors
            )
        except Exception as e:
            raise AudioStreamingError(f"Failed to start ffmpeg process: {str(e)}")

        self._is_playing = True
        self._thread = threading.Thread(target=self._stream_audio)
        self._thread.daemon = True
        self._thread.start()

        # Check if thread started successfully
        time.sleep(0.1)  # Give the thread a moment to start
        if not self._thread.is_alive():
            self._is_playing = False
            if not self._error_queue.empty():
                error = self._error_queue.get()
                raise AudioStreamingError(f"Streaming thread failed to start: {error}")

    def stop(self) -> None:
        """Stop streaming audio."""
        self._is_playing = False  # Signal thread to stop
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)  # Wait for thread to finish
        if self._process:
            self._process.terminate()
            self._process = None
        self._current_audio_data = None

    def set_volume(self, volume: float) -> None:
        """Set the volume (0-1 range)."""
        self._volume = max(0.0, min(1.0, volume))

    def check_streaming_thread(self) -> bool:
        """Check if streaming thread is alive and no errors occurred."""
        if not self._error_queue.empty():
            error = self._error_queue.get()
            self._is_playing = False
            raise AudioStreamingError(f"Streaming error occurred: {error}")
        return self._thread.is_alive() if self._thread else False

    def _stream_audio(self) -> None:
        """Stream audio data to sounddevice."""
        try:
            with sd.OutputStream(
                channels=2, samplerate=44100, dtype="float32", blocksize=4096
            ) as stream:
                while self._is_playing and self._process:
                    # Check process status
                    if self._process.poll() is not None:
                        stderr = self._process.stderr.read().decode(
                            "utf-8", errors="ignore"
                        )
                        raise AudioStreamingError(
                            f"FFmpeg process terminated unexpectedly: {stderr}"
                        )

                    data = self._process.stdout.read(
                        4096 * 4
                    )  # Reading 16-bit PCM data

                    if not data:
                        if self._process.poll() is not None:
                            stderr = self._process.stderr.read().decode(
                                "utf-8", errors="ignore"
                            )
                            raise AudioStreamingError(
                                f"Stream ended unexpectedly: {stderr}"
                            )
                        break

                    try:
                        buffer = bytearray(data)
                        # Convert from 16-bit PCM to float32
                        audio_data = np.frombuffer(buffer, dtype=np.int16)
                        audio_data = (
                            audio_data.astype(np.float32) / 32768.0 * self._volume
                        )
                        audio_data = audio_data.reshape(-1, 2)

                        # Store current audio data for visualization
                        self._current_audio_data = audio_data

                        stream.write(audio_data)
                    except Exception as e:
                        raise AudioStreamingError(f"Audio processing error: {str(e)}")

        except Exception as e:
            self._error_queue.put(str(e))
        finally:
            self._is_playing = False
            if self._process:
                self._process.terminate()

    def cleanup(self) -> None:
        """Clean up resources before shutdown."""
        self.stop()
        if hasattr(self, "_process") and self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=1)  # Wait for process to terminate
            except:  # noqa: E722
                self._process.kill()  # Force kill if terminate fails


class PlayerController:
    """Controls audio playback using ffmpeg and sounddevice."""

    def __init__(self):
        self._streamer = AudioStreamer()
        self._volume = 50  # Initial volume (0-100)
        self._pre_mute_volume = self._volume
        self._is_muted = False
        self._streamer.set_volume(self._volume / 100.0)
        self._is_playing = False
        self._current_url = None

    @property
    def is_playing(self) -> bool:
        """Get current playback state."""
        return self._is_playing

    @property
    def volume(self) -> int:
        """Get current volume level."""
        return 0 if self._is_muted else self._volume

    @property
    def is_muted(self) -> bool:
        """Get mute state."""
        return self._is_muted

    async def toggle_mute(self) -> bool:
        """Toggle mute state."""
        if not self._is_muted:
            self._pre_mute_volume = self._volume
            self._is_muted = True
            self._streamer.set_volume(0)
        else:
            self._is_muted = False
            self._streamer.set_volume(self._pre_mute_volume / 100.0)
        return self._is_muted

    async def set_volume(self, volume: int) -> None:
        """Set volume to specific value."""
        self._volume = max(0, min(100, volume))
        if not self._is_muted:
            self._streamer.set_volume(self._volume / 100.0)

    async def change_volume(self, delta: int) -> None:
        """Change volume by delta amount."""
        if self._is_muted and delta > 0:
            # Unmute when increasing volume
            self._is_muted = False
        new_volume = max(0, min(100, self._volume + delta))
        if new_volume != self._volume:
            self._volume = new_volume
            if not self._is_muted:
                self._streamer.set_volume(self._volume / 100.0)

    async def start_playback(self, url: str) -> bool:
        """Start playback of the current or specified URL."""
        try:
            if self._is_playing:
                await self.stop_playback()
            if url:
                self._current_url = url
            if self._current_url:
                self._streamer.set_volume(self._volume / 100.0)
                self._streamer.play(self._current_url)
                self._is_playing = True
                # Verify streaming started successfully
                self._streamer.check_streaming_thread()
                return True
            return False
        except AudioStreamingError:
            self._is_playing = False
            raise  # Re-raise the error to be handled by the UI layer

    async def stop_playback(self) -> None:
        """Stop playback."""
        if self._is_playing:
            self._streamer.stop()
            self._is_playing = False

    async def cleanup(self) -> None:
        """Clean up resources before shutting down."""
        if self._is_playing:
            await self.stop_playback()
        self._streamer.cleanup()

    def get_current_audio_data(self) -> np.ndarray | None:
        """Get current audio data for visualization."""
        return self._streamer.current_audio_data
