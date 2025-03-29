import threading
import time
import torch
import subprocess
import sounddevice as sd


class AudioStreamer:
    """Audio streamer using ffmpeg and sounddevice."""

    def __init__(self):
        self._process = None
        self._volume = 1.0
        self._is_playing = False
        self._thread = None
        self._latency = 0.0
        self._last_chunk_time = 0

    def play(self, url: str) -> None:
        """Start streaming audio from the given URL."""
        if self._is_playing:
            self.stop()
            # Wait for previous thread to finish
            if self._thread and self._thread.is_alive():
                self._thread.join()

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
            stderr=subprocess.DEVNULL,
        )
        self._is_playing = True
        self._thread = threading.Thread(target=self._stream_audio)
        self._thread.daemon = True
        self._thread.start()

    def stop(self) -> None:
        """Stop streaming audio."""
        self._is_playing = False  # Signal thread to stop
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)  # Wait for thread to finish
        if self._process:
            self._process.terminate()
            self._process = None

    def set_volume(self, volume: float) -> None:
        """Set the volume (0-1 range)."""
        self._volume = max(0.0, min(1.0, volume))

    def get_latency(self) -> float:
        """Get current streaming latency in milliseconds."""
        return self._latency

    def _stream_audio(self) -> None:
        """Stream audio data to sounddevice."""

        try:
            with sd.OutputStream(
                channels=2, samplerate=44100, dtype="float32", blocksize=4096
            ) as stream:
                while self._is_playing and self._process and self._process.stdout:
                    data = self._process.stdout.read(4096 * 4)  # Read larger chunks
                    if not data:
                        break

                    self._last_chunk_time = time.time()
                    buffer = bytearray(data)
                    audio_data = torch.frombuffer(buffer, dtype=torch.int16).clone()
                    audio_data = audio_data.float() / 32768.0
                    audio_data = audio_data * self._volume

                    # Reshape for stereo
                    audio_data = audio_data.view(-1, 2)
                    stream.write(audio_data.numpy())

                    # Calculate latency
                    current_time = time.time()
                    self._latency = (
                        current_time - self._last_chunk_time
                    ) * 1000  # in ms

        except Exception as e:
            print(f"Audio streaming error: {e}")
            self._latency = 0
        finally:
            self._is_playing = False

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

    @property
    def latency(self) -> float:
        """Get current playback latency in milliseconds."""
        return self._streamer.get_latency() if self._is_playing else 0.0

    async def toggle_mute(self) -> None:
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

    async def start_playback(self, url: str = None) -> bool:
        """Start playback of the current or specified URL."""
        if self._is_playing:
            await self.stop_playback()

        try:
            if url:
                self._current_url = url
            if self._current_url:
                self._streamer.set_volume(self._volume / 100.0)  # Convert to 0-1 range
                self._streamer.play(self._current_url)
                self._is_playing = True
                return True
            return False
        except Exception as e:
            print(f"Playback error: {e}")
            return False

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
