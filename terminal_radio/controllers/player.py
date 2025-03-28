import os
import sys
import platform
from pathlib import Path
import vlc


class PlayerController:
    """Controls the VLC media player instance."""

    def __init__(self):
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()
        self._volume = 50
        self._is_playing = False
        self._is_muted = False
        self._pre_mute_volume = self._volume
        self._player.audio_set_volume(self._volume)
        self._current_url = None

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    async def start_playback(self, url: str = None) -> None:
        """Start playback of the current or specified URL."""
        if url:
            self._current_url = url
        if self._current_url:
            media = self._instance.media_new(self._current_url)
            self._player.set_media(media)
            self._player.play()
            self._is_playing = True

    async def stop_playback(self) -> None:
        """Stop playback."""
        self._player.stop()
        self._is_playing = False

    async def change_volume(self, delta: int) -> None:
        """Change volume by delta amount."""
        new_volume = max(0, min(100, self._volume + delta))
        self._volume = new_volume
        self._player.audio_set_volume(new_volume)

    async def toggle_mute(self) -> None:
        """Toggle mute state."""
        if not self._is_muted:
            self._pre_mute_volume = self._volume
            self._volume = 0
            self._player.audio_set_volume(0)
            self._is_muted = True
        else:
            self._volume = self._pre_mute_volume
            self._player.audio_set_volume(self._pre_mute_volume)
            self._is_muted = False

    def __del__(self):
        """Clean up VLC instance."""
        if hasattr(self, "_player"):
            self._player.release()
        if hasattr(self, "_instance"):
            self._instance.release()
