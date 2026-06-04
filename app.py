"""Tkinter GUI for the scientific and graphing calculator."""

from __future__ import annotations

from collections.abc import Callable, Iterable
import itertools
from pathlib import Path
import sys
import tkinter as tk
from typing import Any
from tkinter import messagebox

from calculator import Calculator, CalculatorError
from graph_renderer import create_figure
from graphing import GraphSeries, default_graph_x_values, sample_graph_series


class ToolTip:
    """Small hover tooltip used for calculator buttons."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.window: tk.Toplevel | None = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event: Any = None) -> None:
        if self.window or not self.text:
            return
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.geometry(f"+{x}+{y}")
        label = tk.Label(
            self.window,
            text=self.text,
            bg="#222222",
            fg="white",
            relief=tk.SOLID,
            borderwidth=1,
            padx=6,
            pady=3,
            font=("arial", 9),
        )
        label.pack()

    def hide(self, _event: Any = None) -> None:
        if self.window:
            self.window.destroy()
            self.window = None


class CalculatorApp:
    """Owns all Tkinter widgets and coordinates them with Calculator."""

    def __init__(self, root: tk.Tk | None = None) -> None:
        self.root = root or tk.Tk()
        self.root.title("Calculadora")
        self.root.configure(background="white")
        self.root.resizable(width=False, height=False)
        self.root.geometry("480x568+0+0")
        self._icon_image = None
        self._set_window_icon()

        self.engine = Calculator()
        self.memory_list: list[float] = []
        self.buttons: list[tk.Button] = []
        self.scientific_widgets: list[tk.Widget] = []
        self.tooltips: list[ToolTip] = []
        self.history_window: tk.Toplevel | None = None
        self.history_listbox: tk.Listbox | None = None
        self.history_panel_listbox: tk.Listbox | None = None
        self.memory_panel_listbox: tk.Listbox | None = None
        self.graph_window: tk.Toplevel | None = None
        self.graph_canvas: Any | None = None
        self.help_window: tk.Toplevel | None = None
        self.angle_var = tk.StringVar(value=self.engine.angle_mode)
        self.graph_angle_var = tk.StringVar(value=Calculator.ANGLE_RADIANS)
        self.dark_mode = tk.BooleanVar(value=False)
        self.expression_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value="")
        self.status_is_error = False

        self.calc = tk.Frame(self.root)
        self.calc.grid()

        self._build_display()
        self._build_standard_buttons()
        self._build_scientific_buttons()
        self._build_side_panel()
        self._build_menu()
        self._bind_keyboard()
        self._apply_theme()
        self.set_standard_mode()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_calculator)

    def run(self) -> None:
        self.root.mainloop()

    def destroy(self) -> None:
        self.root.destroy()

    def number_enter(self, num: object) -> None:
        self._run_engine(lambda: self.engine.number_enter(num))

    def expression_enter(self, value: object) -> None:
        self._run_engine(lambda: self.engine.expression_enter(value))

    def sum_of_total(self) -> None:
        expression = self.expression_var.get().strip()
        if expression and expression != self.engine.display:
            self.evaluate_expression_entry()
            return
        self._run_engine(self.engine.sum_of_total)

    def operation(self, op: str) -> None:
        self._run_engine(lambda: self.engine.operation(op))

    def clear_entry(self) -> None:
        self._run_engine(self.engine.clear_entry)

    def all_clear_entry(self) -> None:
        self._run_engine(self.engine.all_clear_entry)

    def backspace(self) -> None:
        self._run_engine(self.engine.backspace)

    def squared(self) -> None:
        self._run_engine(self.engine.squared)

    def maths_pm(self) -> None:
        self._run_engine(self.engine.toggle_sign)

    def pi(self) -> None:
        self._run_engine(self.engine.pi)

    def e(self) -> None:
        self._run_engine(self.engine.e)

    def log(self) -> None:
        self._run_engine(self.engine.log)

    def sin(self) -> None:
        self._run_engine(self.engine.sin)

    def cos(self) -> None:
        self._run_engine(self.engine.cos)

    def tan(self) -> None:
        self._run_engine(self.engine.tan)

    def sinh(self) -> None:
        self._run_engine(self.engine.sinh)

    def cosh(self) -> None:
        self._run_engine(self.engine.cosh)

    def tanh(self) -> None:
        self._run_engine(self.engine.tanh)

    def power(self) -> None:
        self._run_engine(self.engine.power)

    def square(self) -> None:
        self._run_engine(self.engine.square)

    def cube(self) -> None:
        self._run_engine(self.engine.cube)

    def reciprocal(self) -> None:
        self._run_engine(self.engine.reciprocal)

    def percent(self) -> None:
        self._run_engine(self.engine.percent)

    def factorial(self) -> None:
        self._run_engine(self.engine.factorial)

    def absolute(self) -> None:
        self._run_engine(self.engine.absolute)

    def asin(self) -> None:
        self._run_engine(self.engine.asin)

    def acos(self) -> None:
        self._run_engine(self.engine.acos)

    def atan(self) -> None:
        self._run_engine(self.engine.atan)

    def phi(self) -> None:
        self.expression_enter("phi")

    def tau(self) -> None:
        self.expression_enter("tau")

    def graph(self) -> None:
        function = self.expression_var.get().strip() or str(self.txt_display.get()).strip()
        if not function or function == "Error":
            messagebox.showwarning(
                "Graph", "Ingresa una función válida, por ejemplo: x^2 + 2*x"
            )
            return

        x_values = default_graph_x_values(-10, 10, 401)
        series = sample_graph_series(
            function,
            x_values,
            trig_mode=self.graph_angle_var.get(),
            variables=self.engine.variables,
        )

        if not any(point is not None for point in series.points):
            messagebox.showerror("Graph", "No se pudo graficar la función.")
            return

        self._show_graph_window(function, series)

    def set_standard_mode(self) -> None:
        self._hide_scientific_widgets()
        self.root.geometry("480x568+0+0")
        self.root.resizable(width=False, height=False)

    def set_scientific_mode(self) -> None:
        self._show_scientific_widgets()
        self.root.geometry("944x568+0+0")
        self.root.resizable(width=False, height=False)

    def set_angle_mode(self, angle_mode: str) -> None:
        try:
            self.engine.set_angle_mode(angle_mode)
        except ValueError as exc:
            messagebox.showerror("Calculadora", str(exc))
            return
        self.angle_var.set(angle_mode)

    def set_graph_angle_mode(self, angle_mode: str) -> None:
        if angle_mode not in {Calculator.ANGLE_DEGREES, Calculator.ANGLE_RADIANS}:
            messagebox.showerror("Graph", f"Modo angular inválido: {angle_mode}")
            return
        self.graph_angle_var.set(angle_mode)

    def save_to_memory(self, show_window: bool = False) -> None:
        try:
            value = float(self.txt_display.get())
        except ValueError:
            self._set_status("Solo se pueden guardar números.", is_error=True)
            return

        self.memory_list.insert(0, value)
        self._refresh_memory_panel()
        self._set_status("Resultado guardado en memoria.")

        if show_window:
            self._show_memory_window(value)

    def recall_memory(self) -> None:
        if not self.memory_list:
            self._set_status("No hay ningún valor guardado.", is_error=True)
            return
        index = self._selected_memory_index()
        self.number_enter(str(self.memory_list[index]))

    def show_history(self) -> None:
        if self.history_window and self.history_window.winfo_exists():
            self._refresh_history_window()
            self.history_window.lift()
            return

        self.history_window = tk.Toplevel(self.root)
        self.history_window.title("Historial")
        self.history_window.configure(background="white")
        self.history_window.resizable(width=False, height=False)
        self.history_window.geometry("520x280+0+120")
        self.history_window.protocol("WM_DELETE_WINDOW", self._close_history_window)

        frame = tk.Frame(self.history_window, bg="white")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        scrollbar = tk.Scrollbar(frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.history_listbox = tk.Listbox(
            frame,
            width=58,
            height=9,
            font=("arial", 11),
            yscrollcommand=scrollbar.set,
        )
        self.history_listbox.grid(row=0, column=0, sticky="nsew")
        self.history_listbox.bind("<Double-Button-1>", lambda _event: self.recall_history_result())
        scrollbar.config(command=self.history_listbox.yview)

        button_frame = tk.Frame(self.history_window, bg="white")
        button_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        tk.Button(button_frame, text="Usar resultado", command=self.recall_history_result).grid(row=0, column=0, padx=4)
        tk.Button(button_frame, text="Usar expresión", command=self.recall_history_expression).grid(row=0, column=1, padx=4)
        tk.Button(button_frame, text="Limpiar", command=self.clear_history).grid(row=0, column=2, padx=4)
        tk.Button(button_frame, text="Cerrar", command=self._close_history_window).grid(row=0, column=3, padx=4)

        self._refresh_history_window()

    def clear_history(self) -> None:
        self.engine.clear_history()
        self._refresh_history_views()

    def recall_history_result(self) -> None:
        index = self._selected_history_index()
        if index is None:
            return
        self._run_engine(lambda: self.engine.recall_history_result(index))

    def recall_history_expression(self) -> None:
        index = self._selected_history_index()
        if index is None:
            return
        self._run_engine(lambda: self.engine.recall_history_expression(index))

    def exit_calculator(self) -> None:
        if messagebox.askyesno("Calculadora", "¿Seguro que deseas cerrar?"):
            self.root.destroy()

    def handle_key(self, event: Any) -> str | None:
        key = event.keysym
        char = event.char
        widget = getattr(event, "widget", None)

        if self._is_control_pressed(event):
            shortcut = key.lower()
            if shortcut in {"c", "insert"}:
                self.copy_to_clipboard()
                return "break"
            if shortcut == "v":
                self.paste_from_clipboard()
                return "break"
            if shortcut == "a":
                self.select_expression()
                return "break"
            if shortcut == "z":
                self.undo()
                return "break"
            if shortcut == "y":
                self.redo()
                return "break"

        if widget is self.expression_entry:
            if key in {"Return", "KP_Enter"}:
                self.evaluate_expression_entry()
                return "break"
            if key == "Escape":
                self.all_clear_entry()
                return "break"
            return None

        if key in {"Return", "KP_Enter"}:
            self.sum_of_total()
            return "break"
        if key == "Escape":
            self.all_clear_entry()
            return "break"
        if key == "BackSpace":
            self.backspace()
            return "break"
        if key == "Delete":
            self.clear_entry()
            return "break"

        if char in "0123456789.":
            self.number_enter(char)
            return "break"
        if char.isalpha():
            self.expression_enter(char.lower())
            return "break"
        if char in {"(", ")", ","}:
            self.expression_enter(char)
            return "break"

        if char in "+-*/%^=":
            self.expression_enter(char)
            return "break"

        return None

    def evaluate_expression_entry(self) -> None:
        expression = self.expression_var.get().strip()
        if not expression:
            self.all_clear_entry()
            return

        def action() -> None:
            self.engine.set_expression(expression)
            self.engine.sum_of_total()

        self._run_engine(action, expression_text=expression)

    def copy_to_clipboard(self) -> None:
        try:
            value = self.expression_entry.selection_get()
        except tk.TclError:
            value = self.txt_display.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self._set_status("Copiado.")

    def paste_from_clipboard(self) -> None:
        try:
            value = self.root.clipboard_get()
        except tk.TclError:
            self._set_status("El portapapeles está vacío.", is_error=True)
            return
        self.expression_entry.focus_set()
        self.expression_entry.insert(tk.INSERT, value)
        self._set_status("Pegado en la expresión.")

    def select_expression(self) -> None:
        self.expression_entry.focus_set()
        self.expression_entry.selection_range(0, tk.END)

    def undo(self) -> None:
        self.engine.undo()
        self.display(self.engine.display)
        self._refresh_history_views()
        self._set_status("Deshacer.")

    def redo(self) -> None:
        self.engine.redo()
        self.display(self.engine.display)
        self._refresh_history_views()
        self._set_status("Rehacer.")

    def display(
        self,
        value: str,
        expression_text: str | None = None,
        update_expression: bool = True,
    ) -> None:
        self.result_var.set(value)
        self.txt_display.configure(state="normal")
        self.txt_display.delete(0, tk.END)
        self.txt_display.insert(0, value)
        self.txt_display.configure(state="readonly")
        if update_expression:
            self.expression_var.set(
                expression_text
                if expression_text is not None
                else self._current_expression_text()
            )

    def _run_engine(
        self,
        action: Callable[[], object],
        expression_text: str | None = None,
    ) -> None:
        try:
            action()
        except CalculatorError as exc:
            self.display(self.engine.display, update_expression=False)
            self._set_status(str(exc), is_error=True)
            return
        self.display(self.engine.display, expression_text=expression_text)
        self._set_status("")
        self._refresh_history_views()

    def _build_display(self) -> None:
        self.display_frame = tk.Frame(self.calc, bg="white")
        self.display_frame.grid(row=0, column=0, columnspan=4, pady=1, sticky="ew")

        self.expression_entry = tk.Entry(
            self.display_frame,
            textvariable=self.expression_var,
            font=("arial", 12),
            bg="white",
            bd=4,
            width=42,
            justify=tk.RIGHT,
        )
        self.expression_entry.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 0))

        self.txt_display = tk.Entry(
            self.display_frame,
            textvariable=self.result_var,
            font=("arial", 20, "bold"),
            bg="white",
            readonlybackground="white",
            bd=12,
            width=28,
            justify=tk.RIGHT,
            state="readonly",
        )
        self.txt_display.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 0))

        self.status_label = tk.Label(
            self.display_frame,
            textvariable=self.status_var,
            font=("arial", 9),
            bg="white",
            fg="#555555",
            anchor="e",
        )
        self.status_label.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 2))
        self.display_frame.columnconfigure(0, weight=1)
        self.display("0")

    def _build_standard_buttons(self) -> None:
        number_pad = "789456123"
        for i, (row, col) in enumerate(itertools.product(range(2, 5), range(3))):
            button = tk.Button(
                self.calc,
                width=6,
                height=2,
                font=("arial", 20, "bold"),
                bd=4,
                text=number_pad[i],
                command=lambda x=number_pad[i]: self.number_enter(x),
            )
            button.grid(row=row, column=col, pady=1)
            self.buttons.append(button)
            tooltip = ToolTip(button, self._tooltip_for_button(number_pad[i]))
            button.tooltip = tooltip
            self.tooltips.append(tooltip)

        self._button("C", 1, 0, "orange", self.clear_entry)
        self._button("CE", 1, 1, "orange", self.all_clear_entry)
        self._button("√", 1, 2, "antique white", self.squared)
        self._button("+", 1, 3, "antique white", lambda: self.operation("add"))
        self._button("-", 2, 3, "antique white", lambda: self.operation("sub"))
        self._button("*", 3, 3, "antique white", lambda: self.operation("multi"))
        self._button(chr(247), 4, 3, "antique white", lambda: self.operation("divide"))
        self._button("0", 5, 0, "antique white", lambda: self.number_enter(0))
        self._button(".", 5, 1, "antique white", lambda: self.number_enter("."))
        self._button("Ans", 5, 2, "orange", self.recall_memory)
        self._button("=", 5, 3, "orange", self.sum_of_total)

    def _build_scientific_buttons(self) -> None:
        self._scientific_button("Graph", 1, 4, "orange", self.graph)
        self._scientific_button("cos", 1, 5, "grey", self.cos)
        self._scientific_button("tan", 1, 6, "grey", self.tan)
        self._scientific_button("sin", 1, 7, "grey", self.sin)

        self._scientific_button("π", 2, 4, "grey", self.pi)
        self._scientific_button("arccos", 2, 5, "grey", self.acos)
        self._scientific_button("arctan", 2, 6, "grey", self.atan)
        self._scientific_button("arcsin", 2, 7, "grey", self.asin)

        self._scientific_button("log", 3, 4, "white", self.log)
        self._scientific_button("Mod", 3, 5, "white", lambda: self.operation("mod"))
        self._scientific_button("^", 3, 6, "white", self.power)
        self._scientific_button("e", 3, 7, "white", self.e)

        self._scientific_button("x", 4, 4, "white", lambda: self.number_enter("x"))
        self._scientific_button("(", 4, 5, "white", lambda: self.number_enter("("))
        self._scientific_button(")", 4, 6, "white", lambda: self.number_enter(")"))
        self._scientific_button(chr(177), 4, 7, "white", self.maths_pm)

        self.lbl_display = tk.Label(
            self.calc,
            text="Scientific Calculator",
            font=("arial", 30, "bold"),
            justify=tk.CENTER,
        )
        self.lbl_display.grid(row=0, column=4, columnspan=4)
        self.scientific_widgets.append(self.lbl_display)

    def _build_side_panel(self) -> None:
        self.side_panel = tk.Frame(self.calc, bg="white", bd=1, relief=tk.GROOVE)
        self.side_panel.grid(row=5, column=4, columnspan=4, sticky="nsew", padx=2, pady=2)
        self.scientific_widgets.append(self.side_panel)

        history_frame = tk.Frame(self.side_panel, bg="white")
        history_frame.grid(row=0, column=0, sticky="nsew", padx=(4, 2), pady=3)
        tk.Label(
            history_frame,
            text="Historial",
            font=("arial", 9, "bold"),
            bg="white",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")
        self.history_panel_listbox = tk.Listbox(
            history_frame,
            width=32,
            height=2,
            font=("arial", 8),
            activestyle="dotbox",
        )
        self.history_panel_listbox.grid(row=1, column=0, sticky="nsew")
        self.history_panel_listbox.bind(
            "<Double-Button-1>", lambda _event: self.recall_history_result()
        )

        memory_frame = tk.Frame(self.side_panel, bg="white")
        memory_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 4), pady=3)
        tk.Label(
            memory_frame,
            text="Memoria",
            font=("arial", 9, "bold"),
            bg="white",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")
        self.memory_panel_listbox = tk.Listbox(
            memory_frame,
            width=15,
            height=2,
            font=("arial", 8),
            activestyle="dotbox",
        )
        self.memory_panel_listbox.grid(row=1, column=0, sticky="nsew")
        self.memory_panel_listbox.bind(
            "<Double-Button-1>", lambda _event: self.recall_memory()
        )

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.exit_calculator)
        menu_bar.add_cascade(label="Archivo", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Deshacer", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rehacer", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copiar", command=self.copy_to_clipboard, accelerator="Ctrl+C")
        edit_menu.add_command(label="Pegar", command=self.paste_from_clipboard, accelerator="Ctrl+V")
        menu_bar.add_cascade(label="Editar", menu=edit_menu)

        mode_menu = tk.Menu(menu_bar, tearoff=0)
        mode_menu.add_command(label="Estándar", command=self.set_standard_mode)
        mode_menu.add_command(label="Científica", command=self.set_scientific_mode)
        mode_menu.add_separator()
        mode_menu.add_radiobutton(
            label="Grados",
            variable=self.angle_var,
            value=Calculator.ANGLE_DEGREES,
            command=lambda: self.set_angle_mode(Calculator.ANGLE_DEGREES),
        )
        mode_menu.add_radiobutton(
            label="Radianes",
            variable=self.angle_var,
            value=Calculator.ANGLE_RADIANS,
            command=lambda: self.set_angle_mode(Calculator.ANGLE_RADIANS),
        )
        mode_menu.add_separator()
        mode_menu.add_radiobutton(
            label="Graph en radianes",
            variable=self.graph_angle_var,
            value=Calculator.ANGLE_RADIANS,
            command=lambda: self.set_graph_angle_mode(Calculator.ANGLE_RADIANS),
        )
        mode_menu.add_radiobutton(
            label="Graph en grados",
            variable=self.graph_angle_var,
            value=Calculator.ANGLE_DEGREES,
            command=lambda: self.set_graph_angle_mode(Calculator.ANGLE_DEGREES),
        )
        menu_bar.add_cascade(label="Modo", menu=mode_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_checkbutton(
            label="Modo oscuro",
            variable=self.dark_mode,
            command=self._apply_theme,
        )
        menu_bar.add_cascade(label="Ver", menu=view_menu)

        memory_menu = tk.Menu(menu_bar, tearoff=0)
        memory_menu.add_command(label="Guardar resultado", command=self.save_to_memory)
        memory_menu.add_command(label="Usar Ans", command=self.recall_memory)
        menu_bar.add_cascade(label="Memoria", menu=memory_menu)

        history_menu = tk.Menu(menu_bar, tearoff=0)
        history_menu.add_command(label="Mostrar historial", command=self.show_history)
        history_menu.add_command(label="Limpiar historial", command=self.clear_history)
        menu_bar.add_cascade(label="Historial", menu=history_menu)

        advanced_menu = tk.Menu(menu_bar, tearoff=0)
        advanced_menu.add_command(label="x²", command=self.square)
        advanced_menu.add_command(label="x³", command=self.cube)
        advanced_menu.add_command(label="1/x", command=self.reciprocal)
        advanced_menu.add_command(label="%", command=self.percent)
        advanced_menu.add_command(label="n!", command=self.factorial)
        advanced_menu.add_command(label="abs", command=self.absolute)
        advanced_menu.add_separator()
        advanced_menu.add_command(label="sinh", command=self.sinh)
        advanced_menu.add_command(label="cosh", command=self.cosh)
        advanced_menu.add_command(label="tanh", command=self.tanh)
        advanced_menu.add_separator()
        advanced_menu.add_command(label="phi", command=self.phi)
        advanced_menu.add_command(label="tau", command=self.tau)
        menu_bar.add_cascade(label="Avanzado", menu=advanced_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Ayuda", command=self.show_help)
        menu_bar.add_cascade(label="Ayuda", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _bind_keyboard(self) -> None:
        self.root.bind("<Key>", self.handle_key)
        self.txt_display.bind("<Key>", self.handle_key)
        self.expression_entry.bind("<Key>", self.handle_key)
        self.root.focus_set()

    def _button(
        self,
        text: str,
        row: int,
        column: int,
        bg: str,
        command: Callable[[], object],
    ) -> tk.Button:
        button = tk.Button(
            self.calc,
            text=text,
            width=6,
            height=2,
            font=("arial", 20, "bold"),
            bd=4,
            bg=bg,
            command=command,
        )
        button.grid(row=row, column=column, pady=1)
        button.light_bg = bg
        self.buttons.append(button)
        tooltip = ToolTip(button, self._tooltip_for_button(text))
        button.tooltip = tooltip
        self.tooltips.append(tooltip)
        return button

    def _scientific_button(
        self,
        text: str,
        row: int,
        column: int,
        bg: str,
        command: Callable[[], object],
    ) -> tk.Button:
        button = self._button(text, row, column, bg, command)
        self.scientific_widgets.append(button)
        return button

    def _hide_scientific_widgets(self) -> None:
        for widget in self.scientific_widgets:
            widget.grid_remove()

    def _show_scientific_widgets(self) -> None:
        for widget in self.scientific_widgets:
            widget.grid()

    def _show_memory_window(self, value: float) -> None:
        memory = tk.Toplevel(self.root)
        memory.title("Memoria")
        if self._icon_image:
            memory.iconphoto(False, self._icon_image)
        memory.configure(background="white")
        memory.resizable(width=False, height=False)
        memory.geometry("480x100+0+0")
        memo_frame = tk.Frame(memory)
        memo_frame.grid()
        memory_display = tk.Entry(
            memo_frame,
            font=("arial", 20, "bold"),
            bg="white",
            bd=30,
            width=28,
            justify=tk.RIGHT,
        )
        memory_display.grid(row=0, column=0, columnspan=4, pady=1)
        memory_display.insert(0, value)

    def show_help(self) -> None:
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.lift()
            return

        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("Ayuda")
        if self._icon_image:
            self.help_window.iconphoto(False, self._icon_image)
        self.help_window.geometry("520x300+120+120")
        self.help_window.resizable(width=False, height=False)
        self.help_window.protocol("WM_DELETE_WINDOW", self._close_help_window)

        frame = tk.Frame(self.help_window, bg="white", padx=14, pady=14)
        frame.pack(fill=tk.BOTH, expand=True)
        help_text = (
            "Escribe expresiones en la línea superior y presiona Enter.\n\n"
            "Atajos: Ctrl+C copia, Ctrl+V pega, Ctrl+Z deshace, Ctrl+Y rehace.\n"
            "Usa Modo para cambiar grados/radianes. Graph usa radianes por defecto.\n"
            "Usa Ver para activar modo oscuro.\n\n"
            "El panel integrado muestra historial y memoria. Doble clic recupera un valor."
        )
        tk.Label(
            frame,
            text=help_text,
            justify=tk.LEFT,
            anchor="nw",
            bg="white",
            font=("arial", 11),
            wraplength=480,
        ).pack(fill=tk.BOTH, expand=True)
        tk.Button(frame, text="Cerrar", command=self._close_help_window).pack(anchor="e")
        self._apply_theme()

    def _close_help_window(self) -> None:
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.destroy()
        self.help_window = None

    def _current_expression_text(self) -> str:
        if (
            self.engine.history
            and self.engine.input_value
            and self.engine.display == self.engine.history[0].result
        ):
            return self.engine.history[0].expression
        if self.engine.display == "0" and self.engine.input_value:
            return ""
        return self.engine.display

    def _set_status(self, message: str, is_error: bool = False) -> None:
        self.status_is_error = is_error
        self.status_var.set(message)
        if hasattr(self, "status_label"):
            color = "#b3261e" if is_error else self._theme_colors()["muted"]
            self.status_label.configure(fg=color)

    def _is_control_pressed(self, event: Any) -> bool:
        return bool(getattr(event, "state", 0) & 0x0004)

    def _refresh_history_views(self) -> None:
        self._refresh_history_window()
        self._refresh_history_panel()

    def _refresh_history_window(self) -> None:
        if not self.history_listbox:
            return
        if not self.history_window or not self.history_window.winfo_exists():
            return

        self.history_listbox.delete(0, tk.END)
        for entry in self.engine.history:
            self.history_listbox.insert(tk.END, entry.as_text())
        if self.engine.history:
            self.history_listbox.selection_set(0)

    def _refresh_history_panel(self) -> None:
        if not self.history_panel_listbox:
            return

        self.history_panel_listbox.delete(0, tk.END)
        for entry in self.engine.history:
            self.history_panel_listbox.insert(tk.END, entry.as_text())
        if self.engine.history:
            self.history_panel_listbox.selection_set(0)

    def _refresh_memory_panel(self) -> None:
        if not self.memory_panel_listbox:
            return

        self.memory_panel_listbox.delete(0, tk.END)
        for value in self.memory_list:
            self.memory_panel_listbox.insert(tk.END, Calculator.format_result(value))
        if self.memory_list:
            self.memory_panel_listbox.selection_set(0)

    def _selected_history_index(self) -> int | None:
        if not self.engine.history:
            self._set_status("No hay cálculos en el historial.", is_error=True)
            return None
        listbox = self.history_listbox
        if not listbox or not self.history_window or not self.history_window.winfo_exists():
            listbox = self.history_panel_listbox
        if not listbox:
            return 0

        selection = listbox.curselection()
        if not selection:
            return 0
        return selection[0]

    def _selected_memory_index(self) -> int:
        if not self.memory_panel_listbox:
            return 0
        selection = self.memory_panel_listbox.curselection()
        if not selection:
            return 0
        return selection[0]

    def _close_history_window(self) -> None:
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.destroy()
        self.history_window = None
        self.history_listbox = None

    def _tooltip_for_button(self, text: str) -> str:
        tips = {
            "C": "Borra la entrada actual",
            "CE": "Reinicia la calculadora",
            "Graph": "Grafica la expresión con x",
            "Ans": "Recupera la memoria más reciente",
            "=": "Calcula la expresión",
            "√": "Raíz cuadrada",
            chr(177): "Cambia el signo",
        }
        return tips.get(text, f"Insertar {text}")

    def _theme_colors(self) -> dict[str, str | None]:
        if self.dark_mode.get():
            return {
                "bg": "#171717",
                "panel": "#222222",
                "entry": "#101010",
                "fg": "#f4f4f4",
                "muted": "#b8b8b8",
                "button": "#303030",
                "select": "#3f5f7f",
            }
        return {
            "bg": "white",
            "panel": "white",
            "entry": "white",
            "fg": "black",
            "muted": "#555555",
            "button": None,
            "select": "#cce8ff",
        }

    def _apply_theme(self) -> None:
        colors = self._theme_colors()
        for widget in self._iter_widgets(self.root):
            try:
                if isinstance(widget, (tk.Tk, tk.Toplevel, tk.Frame)):
                    widget.configure(bg=colors["bg"])
                elif isinstance(widget, tk.Label):
                    fg = "#b3261e" if widget is self.status_label and self.status_is_error else colors["fg"]
                    if widget is self.status_label and not self.status_is_error:
                        fg = colors["muted"]
                    widget.configure(bg=colors["bg"], fg=fg)
                elif isinstance(widget, tk.Entry):
                    widget.configure(
                        bg=colors["entry"],
                        fg=colors["fg"],
                        insertbackground=colors["fg"],
                        readonlybackground=colors["entry"],
                    )
                elif isinstance(widget, tk.Listbox):
                    widget.configure(
                        bg=colors["entry"],
                        fg=colors["fg"],
                        selectbackground=colors["select"],
                    )
                elif isinstance(widget, tk.Button):
                    bg = colors["button"] or getattr(widget, "light_bg", "SystemButtonFace")
                    widget.configure(bg=bg, fg=colors["fg"], activebackground=colors["panel"])
            except tk.TclError:
                continue

    def _set_window_icon(self) -> None:
        icon_path = Path(__file__).resolve().parent / "assets" / "app_icon.png"
        if not icon_path.exists():
            return
        try:
            self._icon_image = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self._icon_image)
        except tk.TclError:
            self._icon_image = None

    def _iter_widgets(self, widget: tk.Widget) -> Iterable[tk.Widget]:
        yield widget
        for child in widget.winfo_children():
            yield from self._iter_widgets(child)

    def _show_graph_window(self, function: str, series: GraphSeries) -> None:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        if self.graph_window and self.graph_window.winfo_exists():
            for child in self.graph_window.winfo_children():
                child.destroy()
            self.graph_window.lift()
        else:
            self.graph_window = tk.Toplevel(self.root)
            self.graph_window.title("Graph")
            if self._icon_image:
                self.graph_window.iconphoto(False, self._icon_image)
            self.graph_window.geometry("720x520+80+80")
            self.graph_window.protocol("WM_DELETE_WINDOW", self._close_graph_window)

        figure = create_figure(series, title=function)
        self.graph_canvas = FigureCanvasTkAgg(figure, master=self.graph_window)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.graph_canvas, self.graph_window)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _close_graph_window(self) -> None:
        if self.graph_window and self.graph_window.winfo_exists():
            self.graph_window.destroy()
        self.graph_window = None
        self.graph_canvas = None


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]
    if "--smoke-test" in argv:
        raise SystemExit(
            "Run GUI smoke tests with: python tests/smoke_gui.py"
        )
    CalculatorApp().run()


if __name__ == "__main__":
    main()
