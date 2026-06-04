import math
import os
from pathlib import Path
from types import SimpleNamespace
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import CalculatorApp
import app as app_module
from graphing import evaluate_expression


exit_code = 0


def check_close(checks, name, actual, expected, tolerance=0.000001):
    passed = abs(float(actual) - expected) <= tolerance
    checks.append((name, passed, actual, expected))


def check_true(checks, name, condition, actual):
    checks.append((name, bool(condition), actual, True))


CONTROL_MASK = 0x0004


def send_key(application, keysym, char="", state=0, widget=None):
    application.handle_key(
        SimpleNamespace(keysym=keysym, char=char, state=state, widget=widget)
    )


def capture_root(application, filename):
    from PIL import ImageGrab

    artifact_dir = PROJECT_ROOT / "test-artifacts"
    os.makedirs(artifact_dir, exist_ok=True)
    screenshot_path = artifact_dir / filename
    application.root.lift()
    application.root.attributes("-topmost", True)
    application.root.update()
    ImageGrab.grab(window=application.root.winfo_id()).save(screenshot_path)
    print(f"SCREENSHOT {screenshot_path}")


def run_smoke_test(application):
    global exit_code

    checks = []
    try:
        application.root.update_idletasks()

        application.all_clear_entry()
        application.number_enter(7)
        application.operation("add")
        application.number_enter(5)
        application.sum_of_total()
        check_close(checks, "7 + 5", application.txt_display.get(), 12.0)

        application.all_clear_entry()
        application.number_enter(9)
        application.operation("divide")
        application.number_enter(3)
        application.sum_of_total()
        check_close(checks, "9 / 3", application.txt_display.get(), 3.0)

        application.all_clear_entry()
        application.number_enter(2)
        application.power()
        application.number_enter(3)
        application.sum_of_total()
        check_close(checks, "2 ^ 3", application.txt_display.get(), 8.0)

        application.all_clear_entry()
        application.number_enter(30)
        application.sin()
        check_close(checks, "sin(30)", application.txt_display.get(), 0.5)

        application.set_angle_mode("radians")
        application.all_clear_entry()
        for char in "sin(pi/2)":
            send_key(application, char, char)
        send_key(application, "Return", "\r")
        check_close(checks, "angle mode radians expression", application.txt_display.get(), 1.0)
        application.set_angle_mode("degrees")

        application.all_clear_entry()
        application.number_enter(5)
        application.factorial()
        check_close(checks, "factorial menu action", application.txt_display.get(), 120.0)

        application.all_clear_entry()
        for char in "a=5":
            send_key(application, char, char)
        send_key(application, "Return", "\r")
        application.all_clear_entry()
        for char in "a*2":
            send_key(application, char, char)
        send_key(application, "Return", "\r")
        check_close(checks, "variable assignment expression", application.txt_display.get(), 10.0)

        application.all_clear_entry()
        for char in "logb(8,2)":
            send_key(application, char, char)
        send_key(application, "Return", "\r")
        check_close(checks, "keyboard comma in logb expression", application.txt_display.get(), 3.0)

        application.all_clear_entry()
        application.expression_entry.focus_set()
        application.expression_entry.delete(0, "end")
        application.expression_entry.insert(0, "2+2")
        send_key(application, "Return", "\r", widget=application.expression_entry)
        check_close(checks, "editable expression entry", application.txt_display.get(), 4.0)
        check_true(
            checks,
            "editable expression remains visible",
            application.expression_entry.get() == "2+2",
            application.expression_entry.get(),
        )

        application.expression_entry.selection_range(0, "end")
        send_key(application, "c", "c", state=CONTROL_MASK, widget=application.expression_entry)
        application.all_clear_entry()
        send_key(application, "v", "v", state=CONTROL_MASK, widget=application.expression_entry)
        check_true(
            checks,
            "paste restores copied expression",
            application.expression_entry.get() == "2+2",
            application.expression_entry.get(),
        )
        send_key(application, "Return", "\r", widget=application.expression_entry)
        check_close(checks, "pasted expression evaluates", application.txt_display.get(), 4.0)

        send_key(application, "z", "z", state=CONTROL_MASK)
        check_true(
            checks,
            "undo restores expression",
            application.expression_entry.get() == "2+2",
            application.expression_entry.get(),
        )
        send_key(application, "y", "y", state=CONTROL_MASK)
        check_close(checks, "redo restores result", application.txt_display.get(), 4.0)

        application.expression_entry.delete(0, "end")
        application.expression_entry.insert(0, "logb(8)")
        send_key(application, "Return", "\r", widget=application.expression_entry)
        check_true(
            checks,
            "inline error is shown",
            application.status_is_error and bool(application.status_var.get()),
            application.status_var.get(),
        )
        application.all_clear_entry()
        for char in "1+1":
            send_key(application, char, char)
        send_key(application, "Return", "\r")
        check_true(
            checks,
            "inline error clears after valid input",
            not application.status_is_error and application.status_var.get() == "",
            application.status_var.get(),
        )

        application.memory_list.clear()
        application.all_clear_entry()
        application.number_enter(42)
        application.save_to_memory()
        check_true(
            checks,
            "memory panel records value",
            application.memory_panel_listbox.size() > 0,
            application.memory_panel_listbox.size(),
        )
        application.all_clear_entry()
        application.recall_memory()
        check_close(checks, "memory recall", application.txt_display.get(), 42.0)

        for window in application.root.winfo_children():
            if window.winfo_class() == "Toplevel":
                window.destroy()

        application.all_clear_entry()
        send_key(application, "7", "7")
        send_key(application, "plus", "+")
        send_key(application, "5", "5")
        send_key(application, "Return", "\r")
        check_close(checks, "keyboard 7 + 5", application.txt_display.get(), 12.0)

        application.all_clear_entry()
        for char in "sin(30)+cos(60)":
            send_key(application, char, char)
        send_key(application, "Return", "\r")
        check_close(
            checks,
            "keyboard expression sin(30)+cos(60)",
            application.txt_display.get(),
            1.0,
        )

        application.show_history()
        check_true(
            checks,
            "history window has entries",
            application.history_listbox.size() > 0,
            application.history_listbox.size(),
        )
        check_true(
            checks,
            "built-in history panel has entries",
            application.history_panel_listbox.size() > 0,
            application.history_panel_listbox.size(),
        )
        application.recall_history_expression()
        check_true(
            checks,
            "history recalls expression",
            application.txt_display.get() == "sin(30)+cos(60)",
            application.txt_display.get(),
        )
        send_key(application, "Return", "\r")
        check_close(
            checks,
            "history expression recalculates",
            application.txt_display.get(),
            1.0,
        )
        application.recall_history_result()
        check_close(
            checks,
            "history recalls result",
            application.txt_display.get(),
            1.0,
        )
        application.clear_history()
        check_true(
            checks,
            "history clear empties list",
            application.history_listbox.size() == 0,
            application.history_listbox.size(),
        )
        check_true(
            checks,
            "history panel clear empties list",
            application.history_panel_listbox.size() == 0,
            application.history_panel_listbox.size(),
        )
        application._close_history_window()

        application.dark_mode.set(True)
        application._apply_theme()
        check_true(
            checks,
            "dark mode changes root background",
            application.root.cget("bg") != "white",
            application.root.cget("bg"),
        )
        application.dark_mode.set(False)
        application._apply_theme()
        check_true(
            checks,
            "light mode restores root background",
            application.root.cget("bg") == "white",
            application.root.cget("bg"),
        )

        application.show_help()
        check_true(
            checks,
            "help window opens",
            application.help_window is not None and application.help_window.winfo_exists(),
            application.help_window,
        )
        application._close_help_window()
        check_true(
            checks,
            "button tooltip exists",
            hasattr(application.buttons[0], "tooltip"),
            application.buttons[0],
        )

        application.all_clear_entry()
        send_key(application, "1", "1")
        send_key(application, "2", "2")
        send_key(application, "BackSpace")
        check_close(checks, "keyboard backspace", application.txt_display.get(), 1.0)
        send_key(application, "Escape")
        check_close(checks, "keyboard escape", application.txt_display.get(), 0.0)

        original_geometry = application.root.winfo_geometry()
        application.all_clear_entry()
        for char in "x^2+2*x":
            send_key(application, char, char)
        application.graph()
        application.root.update_idletasks()
        check_true(
            checks,
            "graph window opens",
            application.graph_window is not None and application.graph_window.winfo_exists(),
            application.graph_window,
        )
        check_true(
            checks,
            "graph canvas exists",
            application.graph_canvas is not None,
            application.graph_canvas,
        )
        check_true(
            checks,
            "graph keeps root geometry",
            application.root.winfo_geometry() == original_geometry,
            application.root.winfo_geometry(),
        )
        application._close_graph_window()

        captured_graph_modes = []
        original_sampler = app_module.sample_graph_series

        def capture_graph_mode(expression, x_values, trig_mode="radians", variables=None):
            captured_graph_modes.append(trig_mode)
            return original_sampler(
                expression,
                x_values,
                trig_mode=trig_mode,
                variables=variables,
            )

        app_module.sample_graph_series = capture_graph_mode
        try:
            application.set_angle_mode("degrees")
            application.set_graph_angle_mode("radians")
            application.all_clear_entry()
            for char in "sin(x)":
                send_key(application, char, char)
            application.graph()
            application._close_graph_window()
            application.set_graph_angle_mode("degrees")
            application.graph()
            application._close_graph_window()
        finally:
            app_module.sample_graph_series = original_sampler
        check_true(
            checks,
            "graph angle mode is independent",
            captured_graph_modes == ["radians", "degrees"],
            captured_graph_modes,
        )

        captured_errors = []
        original_showerror = app_module.messagebox.showerror
        app_module.messagebox.showerror = lambda title, message: captured_errors.append((title, message))
        try:
            application.all_clear_entry()
            for char in "1/0":
                send_key(application, char, char)
            application.graph()
        finally:
            app_module.messagebox.showerror = original_showerror
        check_true(
            checks,
            "invalid graph reports error",
            bool(captured_errors),
            captured_errors,
        )

        check_close(
            checks,
            "graph expression x^2 + 2*x at x=3",
            evaluate_expression("x^2 + 2*x", 3),
            15.0,
        )
        check_close(
            checks,
            "graph expression 2x at x=3",
            evaluate_expression("2x", 3),
            6.0,
        )
        check_close(
            checks,
            "graph expression exp(x) at x=1",
            evaluate_expression("exp(x)", 1),
            math.e,
        )
        check_close(
            checks,
            "graph expression log10(100)",
            evaluate_expression("log10(100)", 0),
            2.0,
        )

        application.set_standard_mode()
        application.root.update_idletasks()
        check_true(
            checks,
            "standard mode geometry",
            application.root.winfo_geometry().startswith("480x568"),
            application.root.winfo_geometry(),
        )
        check_true(
            checks,
            "standard mode hides scientific widgets",
            not any(widget.winfo_ismapped() for widget in application.scientific_widgets),
            [widget.winfo_ismapped() for widget in application.scientific_widgets],
        )
        capture_root(application, "calculator_standard.png")

        application.set_scientific_mode()
        application.root.update_idletasks()
        check_true(
            checks,
            "scientific mode geometry",
            application.root.winfo_geometry().startswith("944x568"),
            application.root.winfo_geometry(),
        )
        check_true(
            checks,
            "scientific mode shows scientific widgets",
            all(widget.winfo_ismapped() for widget in application.scientific_widgets),
            [widget.winfo_ismapped() for widget in application.scientific_widgets],
        )

        try:
            capture_root(application, "calculator_smoke.png")
        except Exception as exc:
            exit_code = 1
            print(f"SCREENSHOT FAILED: {exc}")

        for name, passed, actual, expected in checks:
            status = "PASS" if passed else "FAIL"
            print(f"{status} {name}: actual={actual} expected={expected}")
            if not passed:
                exit_code = 1
    except Exception as exc:
        exit_code = 1
        print(f"SMOKE TEST ERROR: {exc}")
    finally:
        application.root.after(100, application.destroy)


def main():
    application = CalculatorApp()
    application.root.after(100, lambda: run_smoke_test(application))
    application.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
