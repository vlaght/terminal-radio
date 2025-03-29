# README.md

# Terminal Radio Player

A terminal-based internet radio player with station management and volume control, written by copilot slop mostly
<img width="840" alt="screenshot" src="https://github.com/user-attachments/assets/c9a231b5-8da6-414b-911f-a1fc7a56b216" />

## Installation

### Using Nix

If you have Nix with flakes enabled:

```bash
# Install directly
nix profile install github:vlaght/terminal-radio

# Or try without installing
nix run github:vlaght/terminal-radio
```

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/vlaght/terminal-radio.git
cd terminal-radio
```

2. Using Nix:
```bash
# Enter development shell
nix develop

# Run the application
poetry install
poetry run terminal-radio
```

3. Without Nix (requires Python 3.10+):
```bash
# Install system dependencies
# macOS
brew install ffmpeg portaudio

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg portaudio19-dev

# Install Python dependencies and run
poetry install
poetry run terminal-radio
```

## Usage

- Use up & down arrow keys to navigate stations
- Enter to select and play station
- Space to start/stop playback
- right & left arrows to control volume
- M to mute/unmute
- Q to quit
- A to add stations
- E to edit station
- R to remove station

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
