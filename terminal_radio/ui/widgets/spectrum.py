from textual.widgets import Sparkline
import numpy as np


class SpectrumVisualizer(Sparkline):
    """Widget showing audio frequency spectrum."""

    _FFT_SIZE = 4096
    _RESAMPLE_SIZE = 9

    def __init__(self, *args, **kwargs):
        self.plug = np.zeros(self._RESAMPLE_SIZE + 1).tolist()
        # Calculate logarithmic frequency bands
        self.freq_bands = np.logspace(
            np.log10(20),  # Start from 20Hz
            np.log10(20000),  # Up to 20kHz
            self._RESAMPLE_SIZE + 1,
        ).astype(int)
        super().__init__(
            data=self.plug,
            *args,
            **kwargs,
        )

    def update_spectrum(self, audio_data: np.ndarray) -> None:
        """Update spectrum visualization from audio data."""
        _audio_data = audio_data.copy()
        if len(_audio_data) == 0:
            return self.plug

        # Convert stereo to mono if needed
        if len(_audio_data.shape) > 1:
            _audio_data = _audio_data.mean(axis=1)

        # Apply window function to reduce spectral leakage
        window = np.hanning(len(_audio_data[: self._FFT_SIZE]))
        _audio_data = _audio_data[: self._FFT_SIZE] * window

        # Calculate FFT
        fft_data = np.fft.fft(_audio_data[: self._FFT_SIZE])
        # Get magnitude spectrum
        magnitude = np.abs(fft_data[: self._FFT_SIZE // 2])

        # Calculate frequency bins
        freqs = np.linspace(0, 44100 // 2, len(magnitude))

        # Group frequencies into logarithmic bands
        spectrum = []
        for i in range(len(self.freq_bands) - 1):
            start = np.searchsorted(freqs, self.freq_bands[i])
            end = np.searchsorted(freqs, self.freq_bands[i + 1])
            spectrum.append(float(np.mean(magnitude[start:end])))

        # Apply log scaling to compress dynamic range
        spectrum = np.log10(np.array(spectrum) + 1)
        # Normalize
        max_val = max(spectrum) if max(spectrum) > 0 else 1
        spectrum = [min(s / max_val, 1.0) for s in spectrum]

        self.data = spectrum
