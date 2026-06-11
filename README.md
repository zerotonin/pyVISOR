# GameThogram
[![Tests](https://github.com/zerotonin/GameThogram/actions/workflows/tests.yml/badge.svg)](https://github.com/zerotonin/GameThogram/actions/workflows/tests.yml)
[![Lint](https://github.com/zerotonin/GameThogram/actions/workflows/lint.yml/badge.svg)](https://github.com/zerotonin/GameThogram/actions/workflows/lint.yml)
[![Documentation](https://github.com/zerotonin/GameThogram/actions/workflows/docs.yml/badge.svg)](https://zerotonin.github.io/GameThogram)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/725059593.svg)](https://doi.org/10.5281/zenodo.19324275)

**Gamepad-driven ethogram annotation for animal behaviour research.**

GameThogram is a desktop application for manually scoring animal behaviours in video recordings using a gamepad (Xbox, PlayStation) or keyboard. It is designed for ethologists and behavioural neuroscientists who need frame-accurate behavioural coding with real-time visual feedback.

> Formerly known as pyMovScorer / pyVISOR.

## Download

**No Python required.** Pre-built binaries for Windows, macOS, and Linux are available on the [Releases page](https://github.com/zerotonin/GameThogram/releases/latest). Download the archive for your platform, unzip, and double-click `GameThogram` to launch.

| Platform | Download | Notes |
|---|---|---|
| Windows | `GameThogram-Windows.zip` | Unzip, run `GameThogram.exe` |
| macOS | `GameThogram-macOS.zip` | Unzip, right-click → Open on first launch (Gatekeeper) |
| Linux | `GameThogram-Linux.tar.gz` | Extract, run `./GameThogram` |

If you prefer to install from source (e.g. for development), see [Installation](#installation) below.

## Features

- **Video playback** with frame-by-frame stepping, variable-speed forward/reverse, and FPS control
- **Gamepad support** — Xbox, PlayStation, and generic controllers via pygame; keyboard fallback always available
- **Multi-animal scoring** — define independent behaviour sets per animal with colour-coded icons
- **Behaviour compatibility** — mark which behaviours can co-occur on the same frame
- **Visual feedback** — recorded annotations shown semi-transparent, active annotations highlighted with golden border; F1-toggleable key binding overlay
- **Session persistence** — resume files (`.gamethogram.pkl`) saved automatically next to the video; re-running the scorer on the same video restores all previous annotations seamlessly
- **Autosave** — periodic background snapshots (enabled by default, every 5 minutes)
- **Built-in analysis** — behaviour percentages, bout durations (mean ± SD), and transition probability matrices (pseudo-log colour scale) per animal and globally
- **Export** — annotation data as text, Excel, MATLAB, or pickle; analysis plots as CSV, PNG, or SVG (text as text in SVG); scored video overlay as MP4 or image sequence
- **Portable settings** — save/load all animals, behaviours, colours, icons, and key bindings as a single JSON file

## Installation

### Prerequisites

- Python 3.9 or later
- A working display (GameThogram uses PyQt5 for the configuration GUI and pygame for the scoring window)

### Install from source

```bash
git clone https://github.com/zerotonin/GameThogram.git
cd GameThogram
pip install -e .
```

> **Tip:** Use a virtual environment:
> ```bash
> python -m venv .venv
> source .venv/bin/activate   # Linux/macOS
> .venv\Scripts\activate      # Windows
> pip install -e .
> ```

### Conda environment

```bash
conda env create -f environment.yml
conda activate pyvisor
pip install -e .
```

## Quick start

```bash
gamethogram       # launch from anywhere after install
```

### Workflow

1. **Behaviours tab** — define animals and their behaviours; pick icons, colours, and compatibility
2. **Button Assignment tab** — select your input device from the dropdown; assign gamepad buttons to behaviours and movie controls (or use "Set default movie bindings")
3. **Analysis tab** — load a video file, then click **Run Scorer**
4. **Score** — the scorer window opens with your video; press gamepad buttons to toggle behaviours; F1 shows/hides the key binding overlay; close the window when done
5. **Export** — choose a format and click **Export Data**; or switch to the **Results Overview** tab for plots and CSV/PNG/SVG export

## Gamepad setup

GameThogram works with any gamepad that pygame/SDL can detect. Plug in your controller **before** launching so that pygame picks it up at startup.

The **"Set default movie bindings"** button provides one-click presets for **Xbox and PlayStation layouts only**. All other controllers (8BitDo, generic USB pads, Nintendo-style controllers, etc.) work perfectly well — you simply assign each button manually using the "assign button" dialog, which detects any button press, stick movement, or trigger pull on any recognised controller.

### Tested controllers (25 March 2026)

| Controller | Connection | OS | Status |
|---|---|---|---|
| Xbox 360 | USB | Linux | ✅ Works out of the box |
| Xbox One | USB | Linux | ✅ Works out of the box |
| Xbox Elite Series 2 | USB | Linux | ✅ Works out of the box; paddles register as extra buttons |
| Sony PS5 DualSense | USB | Linux | ✅ Works out of the box |
| CSL PS2-style clone | USB | Linux | ✅ Works out of the box |
| 8BitDo Pro 3 | Bluetooth (S mode) | Linux | ✅ Works after Bluetooth pairing |
| 8BitDo Pro 3 | USB cable | Linux | ❓ Not yet tested reliably |

### 8BitDo Pro 3 via Bluetooth

The 8BitDo Pro 3 works over Bluetooth after a standard pairing procedure:

1. Set the switch on the back of the controller to **S**
2. Pair via your system's Bluetooth settings or `bluetoothctl`:
   ```bash
   bluetoothctl
   power on
   scan on
   # Hold the pairing button on the controller until the LED flashes
   pair XX:XX:XX:XX:XX:XX
   trust XX:XX:XX:XX:XX:XX
   connect XX:XX:XX:XX:XX:XX
   ```
3. Launch GameThogram — the controller appears as "Pro Controller" in the device dropdown
4. Assign buttons manually (no default preset for this layout)

USB dongle support (S/X and D modes) has not been tested reliably and may depend on your kernel and SDL versions.

### Platform-specific notes

- **Linux:** Most USB gamepads work out of the box. If a controller is not detected, try installing `xboxdrv` or `xpad`. For Bluetooth controllers, ensure the device is paired before launching.
- **macOS:** Xbox controllers may require [360Controller](https://github.com/360Controller/360Controller) or Bluetooth pairing.
- **Windows:** Xbox controllers work natively. PlayStation controllers may need [DS4Windows](https://ds4-windows.com/).

## Supported video formats

GameThogram uses [pims](https://github.com/soft-matter/pims) + [PyAV](https://github.com/PyAV-Org/PyAV) for video I/O: AVI, MP4, MOV, MKV, MPG, WMV, FLV, WebM, M4V, and Norpix SEQ files. Image sequences (JPEG, PNG, TIFF) are also supported.

## Project structure

```
GameThogram/
├── pyvisor/                    # Main package (internal name kept for compatibility)
│   ├── GUI/                    # PyQt5 interface
│   │   ├── model/              # Data model (Animal, Behaviour, KeyBindings, …)
│   │   ├── tab_behaviours/     # Behaviour definition tab
│   │   ├── tab_buttons/        # Button assignment tab
│   │   ├── icon_gallery/       # Icon selection dialogs
│   │   ├── tab_analysis.py     # Video loading, scorer control, export
│   │   ├── tab_results.py      # Analysis plots (matplotlib embedded in Qt)
│   │   ├── main_gui.py         # Main window
│   │   └── run_gui.py          # Entry point
│   ├── analysis/               # Offline and online analysis modules
│   ├── resources/              # Bundled icons and logo
│   ├── manual_ethology_scorer_2.py  # Scorer engine (pygame)
│   ├── MediaHandler.py         # Video playback via pims
│   ├── ethogram.py             # Ethogram data structure
│   ├── animal_ethogram_2.py    # Per-animal frame-level data (pandas)
│   ├── dataIO.py               # Save/load/export
│   └── user_input_control.py   # Input dispatch
├── docs/                       # Sphinx documentation source
├── tests/                      # Unit and integration tests
├── pyproject.toml              # Packaging, dependencies, ruff + pytest config
├── CITATION.cff                # How to cite (Zenodo DOI)
└── environment.yml             # Conda environment specification
```

## Contributing

1. Fork and create a feature branch
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Lint: `ruff check .`
4. Run tests: `pytest`
5. Open a pull request

## Troubleshooting

- **GUI does not start** — verify PyQt5 is installed and you are using Python 3.9+
- **Controller not detected** — confirm the OS recognises the gamepad (`jstest-gtk` on Linux); plug in before launching
- **Video won't load** — ensure PyAV is installed: `pip install av`
- **Reset settings** — delete `~/.local/share/pyVISOR/` (Linux) or equivalent on your platform

## Authors

Bart Geurten, Ilyas Kuhlemann

## License

GPL-3.0-or-later
