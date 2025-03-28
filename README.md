# README.md

# Terminal Radio Player

A cross-platform terminal-based internet radio player.

## Features

- **Station Lists Management**: Full CRUD functionality for managing radio stations.
- **Playback Control**: Start and stop playback using visual buttons and hotkeys.
- **Volume Control**: Adjust volume through visual sliders and hotkeys.
- **User Space Installation**: Easily installable as an application for distribution.

## Installation

### Prerequisites

First, install MPV for your platform:

#### macOS
```bash
brew install mpv
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install mpv libmpv-dev
```

#### Linux (Fedora)
```bash
sudo dnf install mpv mpv-devel
```

#### Windows
```bash
choco install mpv
```
Or download MPV from: https://sourceforge.net/projects/mpv-player-windows/files/

### Installing the Radio Player

```bash
# Using pip
pip install terminal-radio

# Or using Poetry
poetry install
```

## Usage

```bash
# Using pip installation
terminal-radio

# Or using Poetry
poetry run radio
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
