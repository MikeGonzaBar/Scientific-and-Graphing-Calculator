import itertools
from tkinter import *
import math
import tkinter.messagebox
import turtle


# ==============================================CREACIÓN DE VENTANA PRINCIPAL============================================
root = Tk()
root.title("Calculadora")
root.configure(background="white")
root.resizable(width=False, height=False)
root.geometry("480x568+0+0")

calc = Frame(root)
calc.grid()

memory_list = []


class Calc():
    def __init__(self):
        self.total = 0
        self.current = ""
        self.input_value = True
        self.check_sum = False
        self.op = ""
        self.result = False

    def numberEnter(self, num):
        self.result = False
        firstnum = txt_display.get()
        secondnum = str(num)

        if self.input_value:
            if secondnum == "." and "." in firstnum:
                return
            self.current = secondnum
            self.input_value = False
        else:
            self.current = firstnum + secondnum

        self.display(self.current)

    def sum_of_total(self):
        self.result = True
        self.current = float(self.current)
        if self.check_sum:
            self.valid_function()
        else:
            self.total = float(txt_display.get())

    def display(self, value):
        txt_display.delete(0, END)
        txt_display.insert(0, value)

    def valid_function(self):
        if self.op == "add":
            self.total += self.current
        elif self.op == "divide":
            self.total /= self.current
        elif self.op == "mod":
            self.total %= self.current
        elif self.op == "multi":
            self.total *= self.current
        elif self.op == "sub":
            self.total -= self.current
        self._restart_status()

    def operation(self, op):
        self.current = float(self.current)
        if not self.input_value:
            self.total = self.current
            self.input_value = True
        elif self.check_sum:
            self.valid_function()

        self.check_sum = True
        self.op = op
        self.result = False

    def clear_entry(self):
        self.current = "0"
        self.input_value = True
        self.result = False
        self.display(0)

    def all_clear_entry(self):
        self.clear_entry()
        self.total = 0

    def _calculate(self, operation):
        self.result = False
        self.current = operation(float(txt_display.get()))
        self.display(self.current)

    def squared(self):
        self._calculate(math.sqrt)

    def mathsPM(self):
        self._calculate(lambda x: -x)

    def pi(self):
        self._calculate(lambda x: math.pi)

    def e(self):
        self._calculate(lambda x: math.e)

    def log(self):
        self._calculate(math.log)

    def sin(self):
        self._calculate(lambda x: math.degrees(math.sin(x)))

    def cos(self):
        self._calculate(lambda x: math.degrees(math.cos(x)))

    def tan(self):
        self._calculate(lambda x: math.degrees(math.tan(x)))

    def poten(self):
        self.result = False
        self.total **= float(self.current)
        self.input_value = True
        self.check_sum = False
        self.display(self.total)

    def asin(self):
        self._calculate(lambda x: math.degrees(math.asin(x)))

    def acos(self):
        self._calculate(lambda x: math.degrees(math.acos(x)))

    def atan(self):
        self._calculate(lambda x: math.degrees(math.atan(x)))

    def graph(self):
        graph = turtle.Screen()
        graph.title("Graph")

        function = str(txt_display.get())
        turtle.clear()
        turtle.speed(3)
        turtle.color('red')

        x_values = range(-10, 11)
        y_values = [eval(function.replace(
            "x", f"*{str(x)}")) * 10 for x in x_values]

        turtle.up()
        turtle.goto(0, 0)
        turtle.down()

        for i in range(len(x_values)):
            turtle.color('black')
            turtle.up() if i == 0 else turtle.down()

            x = x_values[i] * 10
            y = y_values[i]
            turtle.goto(x, y)

        turtle.goto(0, 0)


calc_instance = Calc()
# ===================================DISPLAY Y NÚMEROS===================================================================
txt_display = Entry(calc, font=("arial", 20, "bold"),
                    bg="white", bd=30, width=28, justify=RIGHT)
txt_display.grid(row=0, column=0, columnspan=4, pady=1)
txt_display.insert(0, "0")

number_pad = "789456123"
buttons = []
for i, (row, col) in enumerate(itertools.product(range(2, 5), range(3))):
    buttons.append(Button(calc, width=6, height=2, font=(
        "arial", 20, "bold"), bd=4, text=number_pad[i]))
    buttons[i].grid(row=row, column=col, pady=1)
    buttons[i]["command"] = lambda x=number_pad[i]: calc_instance.numberEnter(
        x)
# ===================================== BUTTONS==========================================================================
btnClear = Button(calc, text="C", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="orange",
                  command=calc_instance.clear_entry).grid(row=1, column=0, pady=1)
btnAllClear = Button(calc, text="CE", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="orange",
                     command=calc_instance.all_clear_entry).grid(row=1, column=1, pady=1)
btnSq = Button(calc, text="√", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
               command=calc_instance.squared).grid(row=1, column=2, pady=1)
btnAdd = Button(calc, text="+", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
                command=lambda: calc_instance.operation("add")).grid(row=1, column=3, pady=1)
btnSub = Button(calc, text="-", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
                command=lambda: calc_instance.operation("sub")).grid(row=2, column=3, pady=1)
btnMul = Button(calc, text="*", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
                command=lambda: calc_instance.operation("multi")).grid(row=3, column=3, pady=1)
btnDiv = Button(calc, text=chr(247), width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
                command=lambda: calc_instance.operation("divide")).grid(row=4, column=3, pady=1)
btnZero = Button(calc, text="0", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
                 command=lambda: calc_instance.numberEnter(0)).grid(row=5, column=0, pady=1)
btnAns = Button(calc, text="Ans", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="orange",
                command=lambda: calc_instance.numberEnter(str(memory_list[0]))).grid(row=5, column=2, pady=1)
btnDot = Button(calc, text=".", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="antique white",
                command=lambda: calc_instance.numberEnter(".")).grid(row=5, column=1, pady=1)
btnEquals = Button(calc, text="=", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="orange",
                   command=calc_instance.sum_of_total).grid(row=5, column=3, pady=1)

# =====================================SCIENTIFIC CALCULATOR=============================================================

btnGraph = Button(calc, text="Graph", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="orange",
                  command=calc_instance.graph).grid(row=1, column=4, pady=1)
btnCos = Button(calc, text="cos", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
                command=calc_instance.cos).grid(row=1, column=5, pady=1)
btnTan = Button(calc, text="tan", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
                command=calc_instance.tan).grid(row=1, column=6, pady=1)
btnSin = Button(calc, text="sin", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
                command=calc_instance.sin).grid(row=1, column=7, pady=1)

btnPi = Button(calc, text="π", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
               command=calc_instance.pi).grid(row=2, column=4, pady=1)
btnArcCos = Button(calc, text="arccos", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
                   command=calc_instance.acos).grid(row=2, column=5, pady=1)
btnArcTan = Button(calc, text="arctan", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
                   command=calc_instance.atan).grid(row=2, column=6, pady=1)
btnArcSin = Button(calc, text="arcsin", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="grey",
                   command=calc_instance.asin).grid(row=2, column=7, pady=1)

btnlog = Button(calc, text="log", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
                command=calc_instance.log).grid(row=3, column=4, pady=1)
btnMod = Button(calc, text="Mod", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
                command=lambda: calc_instance.operation("mod")).grid(row=3, column=5, pady=1)
btnPotencia = Button(calc, text="^", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
                     command=calc_instance.poten).grid(row=3, column=6, pady=1)
btnEuller = Button(calc, text="e", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
                   command=calc_instance.e).grid(row=3, column=7, pady=1)

btnx = Button(calc, text="x", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
              command=lambda: calc_instance.numberEnter("x")).grid(row=4, column=4, pady=1)
btnParentesis1 = Button(calc, text="(", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
                        command=lambda: calc_instance.numberEnter("(")).grid(row=4, column=5, pady=1)
btnParentesis2 = Button(calc, text=")", width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
                        command=lambda: calc_instance.numberEnter(")")).grid(row=4, column=6, pady=1)
btnPM = Button(calc, text=chr(177), width=6, height=2, font=("arial", 20, "bold"), bd=4, bg="white",
               command=calc_instance.mathsPM).grid(row=4, column=7, pady=1)


lblDisplay = Label(calc, text="Scientific Calculator",
                   font=("arial", 30, "bold"), justify=CENTER)
lblDisplay.grid(row=0, column=4, columnspan=4)

# ===================================== MENÚ=============================================================================


def exit_calculator():
    if tkinter.messagebox.askyesno(
        "Calculadora", "¿Seguro que deseas cerrar?"
    ):
        root.destroy()


def set_standard_mode():
    root.geometry("480x568+0+0")
    root.resizable(width=False, height=False)
    return


def set_scientific_mode():
    root.geometry("944x568+0+0")
    root.resizable(width=False, height=False)
    return


def save_to_memory():
    memory = Tk()
    memory.title("Memoria")
    memory.configure(background="white")
    memory.resizable(width=False, height=False)
    memory.geometry("480x100+0+0")
    memo_frame = Frame(memory)
    memo_frame.grid()
    memory_display = Entry(memo_frame, font=("arial", 20, "bold"),
                           bg="white", bd=30, width=28, justify=RIGHT)
    memory_display.grid(row=0, column=0, columnspan=4, pady=1)
    memory_display.insert(0, float(txt_display.get()))
    memory_list.insert(0, float(txt_display.get()))
