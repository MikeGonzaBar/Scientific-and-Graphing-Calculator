# Release Notes

## 0.5.0

This release turns the original Tkinter calculator into a fuller scientific and graphing calculator.

- Added a tested calculator engine module with central result formatting, history records, undo/redo snapshots, variables, and explicit degree/radian mode.
- Added a safe expression parser for typed expressions and graph expressions.
- Added Matplotlib graph windows with gap-aware plotting and Agg-backed renderer tests.
- Added scientific depth: factorial, reciprocal, percent, square, cube, absolute value, scientific notation, hyperbolic trig, log-base support, constants, and calculator variables.
- Added a two-line editable expression/result display, inline status errors, copy/paste, help, tooltips, dark mode, and integrated history/memory panels.
- Added CI metadata, packaging documentation, release notes, changelog, and app icon assets.

## Known Notes

- Calculator expressions default to degrees.
- Graph expressions use an independent graph angle mode and default to radians.
- `%` remains modulo in typed expressions; percent is a unary calculator operation.
