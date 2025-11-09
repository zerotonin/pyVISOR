# pyVISOR

pyVISOR is a desktop toolkit for manual ethology scoring. It allows researchers to play back image sequences or movies, annotate behaviours with configurable key bindings or game controllers, and export structured ethograms for downstream analysis. The project bundles a PyQt-based GUI, reusable data models, and automation helpers aimed at behavioural neuroscience and related disciplines.

## Supported platforms

pyVISOR is built on cross-platform Python tooling and is expected to run on:

- **Windows 10/11** (x86_64)
- **macOS 12+** (Apple Silicon or Intel)
- **Linux** distributions with glibc 2.28+ (x86_64)

The GUI requires a working OpenGL-capable display stack. Xbox-compatible gamepads are optional but supported.

## Quick start

1. Install the published package:
   ```bash
   pip install pyvisor
   ```
2. Launch the graphical scorer:
   ```bash
   pyvisor-gui
   ```
3. Open a video or image sequence, configure animals and behaviours, then begin annotating.

### From source

If you are working from a source checkout, install the project in editable mode:

```bash
pip install -e .[dev]
```

Then start the GUI as described above.

### Create a local conda environment

Use the provided `environment.yml` to create an isolated workspace with all
runtime dependencies pinned to known-good versions:

```bash
conda env create -f environment.yml
conda activate pyvisor
pip install -e .
```

The final `pip install -e .` step installs the project in editable mode so that
changes to the source tree are picked up immediately.

## Contributing

We welcome contributions of bug reports, feature ideas, and pull requests.

1. Fork the repository and create a feature branch.
2. Install development dependencies with `pip install -e .[dev]`.
3. Run the unit tests with `pytest` before opening a pull request.
4. Follow the existing code style and include documentation or tests where relevant.

Please open an issue if you plan significant changes so the community can discuss the design upfront.

## Troubleshooting

- **GUI does not start** – verify that PyQt dependencies are installed for your platform and that you are using Python 3.9 or newer.
- **Video playback is blank or stutters** – ensure you have hardware-accelerated OpenGL drivers and install the optional multimedia dependencies listed in `pyproject` extras (e.g., `PyAV`, `opencv-python`).
- **Controller input is not detected** – confirm that the operating system recognises your gamepad. On Linux you may need the `xpad` or `xboxdrv` kernel modules.
- **Configuration files** – pyVISOR stores temporary GUI state in `~/.pyvisor/`. Deleting this directory resets layouts and cached icons.

If you encounter an issue that is not covered here, please file a bug report with logs (`~/.pyvisor/*.log`) and steps to reproduce.

## License

This project is distributed under the terms specified in the `LICENSE` file.
