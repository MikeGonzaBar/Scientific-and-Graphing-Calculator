from tkinter import*
import math
import tkinter.messagebox
import turtle




#==============================================CREACIÓN DE VENTANA PRINCIPAL============================================
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
        firstnum = txtDisplay.get()
        secondnum = str(num)
        if self.input_value:
            self.current = secondnum
            self.input_value = False
        elif secondnum == "." and secondnum in firstnum:
            return
        else:
            self.current = firstnum + secondnum
        self.display(self.current)

    def sum_of_total(self):
        self.result = True
        self.current = float(self.current)
        if self.check_sum is True:
            self.valid_function()
        else:
            self.total = float(txtDisplay.get())


    def display(self, value):
        txtDisplay.delete(0, END)
        txtDisplay.insert(0, value)

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
        self.input_value = True
        self.check_sum = False
        self.display(self.total)

    def operation (self, op):
        self.current = float(self.current)
        if self.check_sum:
            self.valid.function()
        elif not self.result:
            self.total = self.current
            self.input_value = True
        self.check_sum = True
        self.op = op
        self.result = False

    def Clear_Entry(self):
        self.result = False
        self.current = "0"
        self.display(0)
        self.input_value = True


    def all_Clear_Entry(self):
        self.Clear_Entry()
        self.total = 0

    def squared(self):
        self.result = False
        self.current = math.sqrt(float(txtDisplay.get()))
        self.display(self.current)

    def mathsPM(self):
        self.result = False
        self.current = -(float(txtDisplay.get()))
        self.display(self.current)

    def pi(self):
        self.result = False
        self.current = math.pi
        self.display(self.current)

    def e(self):
        self.result = False
        self.current = math.e
        self.display(self.current)

    def log(self):
        self.result = False
        self.current = math.log(float(txtDisplay.get()))
        self.display(self.current)

    def sin(self):
        self.result = False
        self.current = math.degrees(math.sin(float(txtDisplay.get())))
        self.display(self.current)

    def cos(self):
        self.result = False
        self.current = math.degrees(math.cos(float(txtDisplay.get())))
        self.display(self.current)

    def tan(self):
        self.result = False
        self.current = math.degrees(math.tan(float(txtDisplay.get())))
        self.display(self.current)

    def poten(self):
        self.result = False
        self.total **= float(self.current)
        self.input_value = True
        self.check_sum = False
        self.display(self.total)

    def asin(self):
        self.result = False
        self.current = math.degrees(math.asin(float(txtDisplay.get())))
        self.display(self.current)

    def acos(self):
        self.result = False
        self.current = math.degrees(math.acos(float(txtDisplay.get())))
        self.display(self.current)

    def atan(self):
        self.result = False
        self.current = math.degrees(math.atan(float(txtDisplay.get())))
        self.display(self.current)

    def graph(self):
        graph = turtle.Screen()
        graph.title("Gráfica")
        function = str(txtDisplay.get())
        turtle.speed(3)
        turtle.forward(100)
        turtle.left(180)
        turtle.forward(200)
        turtle.left(180)
        turtle.forward(100)
        turtle.left(90)
        turtle.forward(100)
        turtle.left(180)
        turtle.forward(200)
        turtle.goto(0, 0)
        for i in range(-10, 10):
            funcion_replace = function.replace("x", f"*{str(i)}")
            y = eval(funcion_replace)
            y *= 10
            i_new = i * 10
            turtle.goto(i_new, y)

added_value = Calc()

#===================================DISPLAY Y NÚMEROS===================================================================
txtDisplay = Entry(calc, font=("arial", 20, "bold"), bg="white", bd=30, width=28, justify=RIGHT)
txtDisplay.grid(row=0,column=0, columnspan=4, pady=1)
txtDisplay.insert(0, "0")

numberpad = "789456123"
i=0
btn = []
for j in range(2,5):
    for k in range(3):
        btn.append(Button(calc, width=6, height=2, font=("arial", 20, "bold"), bd=4, text=numberpad[i]))
        btn[i].grid(row=j, column=k, pady=1)
        btn[i]["command"]=lambda x=numberpad[i]: added_value.numberEnter(x)
        i+= 1

#===================================== BUTTONS==========================================================================
btnClear = Button(calc, text="C", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="orange",
                  command=added_value.Clear_Entry).grid(row=1, column=0, pady=1)
btnAllClear = Button(calc, text="CE", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="orange",
                     command=added_value.all_Clear_Entry).grid(row=1, column=1, pady=1)
btnSq = Button(calc, text="√", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
               command = added_value.squared).grid(row=1, column=2, pady=1)
btnAdd = Button(calc, text="+", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
                command=lambda: added_value.operation("add")).grid(row=1, column=3, pady=1)
btnSub = Button(calc, text="-", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
                command=lambda: added_value.operation("sub")).grid(row=2, column=3, pady=1)
btnMul = Button(calc, text="*", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
                command=lambda: added_value.operation("multi")).grid(row=3, column=3, pady=1)
btnDiv = Button(calc, text=chr(247), width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
                command=lambda: added_value.operation("divide")).grid(row=4, column=3, pady=1)
btnZero = Button(calc, text="0", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
                 command=lambda: added_value.numberEnter(0)).grid(row=5, column=0, pady=1)
btnAns = Button(calc, text="Ans", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="orange",
                command=lambda: added_value.numberEnter(str(memory_list[0]))).grid(row=5, column=2, pady=1)
btnDot = Button(calc, text=".", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="antique white",
                command=lambda: added_value.numberEnter(".")).grid(row=5, column=1, pady=1)
btnEquals = Button(calc, text="=", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="orange",
                   command=added_value.sum_of_total).grid(row=5, column=3, pady=1)

#=====================================SCIENTIFIC CALCULATOR=============================================================

btnGraph = Button(calc, text="Graph", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="orange",
                  command = added_value.graph).grid(row=1, column=4, pady=1)
btnCos = Button(calc, text="cos", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
                command = added_value.cos).grid(row=1, column=5, pady=1)
btnTan = Button(calc, text="tan", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
                command = added_value.tan).grid(row=1, column=6, pady=1)
btnSin = Button(calc, text="sin", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
                command = added_value.sin).grid(row=1, column=7, pady=1)

btnPi = Button(calc, text="π", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
               command=added_value.pi).grid(row=2, column=4, pady=1)
btnArcCos = Button(calc, text="arccos", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
                   command = added_value.acos).grid(row=2, column=5, pady=1)
btnArcTan = Button(calc, text="arctan", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
                   command=added_value.atan).grid(row=2, column=6, pady=1)
btnArcSin = Button(calc, text="arcsin", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="grey",
                   command=added_value.asin).grid(row=2, column=7, pady=1)

btnlog = Button(calc, text="log", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
                command = added_value.log).grid(row=3, column=4, pady=1)
btnMod = Button(calc, text="Mod", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
                command=lambda: added_value.operation("mod")).grid(row=3, column=5, pady=1)
btnPotencia = Button(calc, text="^", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
                     command = added_value.poten).grid(row=3, column=6, pady=1)
btnEuller = Button(calc, text="e", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
                   command=added_value.e).grid(row=3, column=7, pady=1)

btnx = Button(calc, text="x", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
              command=lambda: added_value.numberEnter("x")).grid(row=4, column=4, pady=1)
btnParentesis1 = Button(calc, text="(", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
                        command=lambda: added_value.numberEnter("(")).grid(row=4, column=5, pady=1)
btnParentesis2 = Button(calc, text=")", width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
                        command=lambda: added_value.numberEnter(")")).grid(row=4, column=6, pady=1)
btnPM = Button(calc, text=chr(177), width=6, height=2, font=("arial", 20, "bold"), bd=4,bg="white",
               command = added_value.mathsPM).grid(row=4, column=7, pady=1)


lblDisplay = Label(calc, text="Scientific Calculator", font=("arial", 30, "bold"), justify=CENTER)
lblDisplay.grid(row=0, column=4, columnspan = 4)

#===================================== MENÚ=============================================================================


def iExit():
    iExit = tkinter.messagebox.askyesno("Calculadora", "¿Seguro que deseas cerrar?")
    if iExit > 0:
        root.destroy()
        return


def Standard():
    root.geometry("480x568+0+0")
    root.resizable(width=False, height=False)
    return


def Scientific():
    root.geometry("944x568+0+0")
    root.resizable(width=False, height=False)
    return


def memoria():
    mem = Tk()
    mem.title("Memoria")
    mem.configure(background="white")
    mem.resizable(width=False, height=False)
    mem.geometry("480x100+0+0")
    memo = Frame(mem)
    memo.grid()
    memDisplay = Entry(memo, font=("arial", 20, "bold"), bg="white", bd=30, width=28, justify=RIGHT)
    memDisplay.grid(row=0, column=0, columnspan=4, pady=1)
    memDisplay.insert(0, float(txtDisplay.get()))
    memory_list.insert(0, float(txtDisplay.get()))


menubar = Menu(calc)

filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Estándar", command=Standard)
filemenu.add_command(label="Científica", command=Scientific)
filemenu.add_command(label="Memoria", command=memoria)
filemenu.add_separator()
filemenu.add_command(label="Salir", command=iExit)


root.configure(menu=menubar)
root.mainloop()
