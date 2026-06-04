# Packaging

This project is packaged as a small Tkinter application with a stable import entrypoint:

```bash
python app.py
```

The project metadata also exposes the same entrypoint as:

```bash
scientific-calculator
```

after installing the project in an environment.

## Build A Windows Executable

From a clean virtual environment:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python tools/create_icon.py
python -m PyInstaller --noconfirm --onefile --windowed --name ScientificCalculator --icon assets/app_icon.ico app.py
```

The executable is written to `dist/ScientificCalculator.exe`.

## Verification Checklist

Before publishing a packaged build:

- Run `python -B -m unittest discover -s tests -v`.
- Run `python -B tests/smoke_gui.py` on a display-capable machine.
- Launch `dist/ScientificCalculator.exe`.
- Verify typed expressions, scientific buttons, history recall, memory recall, dark mode, and graphing.
- Confirm graph expressions use radians by default and only switch to degrees through the graph angle mode control.

## Notes

- Calculator expressions default to degrees.
- Graph expressions default to radians.
- `%` is modulo in typed expressions; use the percent button or `percent(x)` for percentage conversion.
- Variables are calculator-owned and cannot shadow built-in names such as `sin`, `sqrt`, `pi`, `e`, or graph variable `x`.
