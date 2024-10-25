import tkinter as tk
import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox

#custom module parser
import Parser


#function to draw rounded rectangle
def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
        
    points = [x1+radius, y1, x2-radius, y1,
              x2, y1,
              x2, y1+radius, x2, y2-radius,
              x2, y2,
              x2-radius, y2, x1+radius, y2,
              x1, y2,
              x1, y2-radius, x1, y1+radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth=True)


global func_pane
global axes #Axes of matplotlib
global viewport
global isViewportScatter

global viewportParameters
viewportParameters = [-10, 10, -10, 10, 350]
global equations
equations = []

#Function to update sidebar and show functions on viewport
def show_funcs():
    func_pane.delete("all")
    func_rects = []
    upperBound = 10
    for i, fun in enumerate(equations):
        x1, y1 = 10, upperBound + i*50
        x2, y2 = 190, upperBound + 30 + i*50
        func_rects.append(round_rectangle(func_pane, x1, y1, x2, y2, radius=10, fill="white", outline="lightgray"))
        func_pane.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=fun, anchor=tk.CENTER, font=('Arial', 8, "italic"))
        func_pane.create_text(x1+10, y1+10, text=(str(i+1)), anchor=tk.CENTER, fill="pink")
        
    x = np.linspace(viewportParameters[0], viewportParameters[1], viewportParameters[4])
    axes.clear()
    axes.grid()
    axes.set_ylim(viewportParameters[2], viewportParameters[3])
    axes.set_xlim(viewportParameters[0], viewportParameters[1])
    for func in equations:
        y = []
        for i in x:
            y.append(Parser.val(func, i))
        if (isViewportScatter.get()):
            axes.scatter(x, y, s=2)
        else:
            axes.plot(x, y)
    viewport.draw()

#Function to add equation to plot
def get_input():
    global equations
    result = simpledialog.askstring("", "Enter a Function")
    if result:
        try:
            equation = Parser.parse(result)
            if equation == []:
                raise
            else:
                equations.append(equation)
                
        except:
            messagebox.showerror("Parser Failed", "Please enter a valid function!")
        show_funcs()
    else:
        messagebox.showinfo("", "Please enter a function!")

#Function to remove equation from plot
def remove_func():
    global equations
    inputString = simpledialog.askstring("", "Which function to remove? (number)")
    if inputString:
        try:
            inputString=int(inputString)
            equations.pop(inputString-1)
        except:
            messagebox.showerror("Invalid Index", f"Please enter a valid index! (1 to {len(equations)})") 
        print(equations)
        show_funcs()
    else:
        messagebox.showinfo("", "Please enter an index!")


#Function to accept values for viewport dimensions
def get_viewport_params():
    input_window = tk.Toplevel()
    input_window.geometry("200x250")

    entry_label = tk.Label(input_window, text="Cartesian Plane Limits (float)", font=("Arial", "8", "bold"))
    entry_label.pack()
    
    parameterNames = ('-x', '+x', '-y', '+y', 'clarity')
    parameters = []
    for i in range(5):
        entry_label = tk.Label(input_window, text=parameterNames[i], font=("Arial", "8", "italic"))
        entry_label.pack()
        entry = tk.Entry(input_window)
        entry.insert(0, str(viewportParameters[i]))
        entry.pack()
        parameters.append(entry)
        
    commit_button = tk.Button(input_window, text="Commit", command=lambda: set_viewport(parameters))
    commit_button.pack()

#Function to get equation parameters
def get_equation_params():
    input_window = tk.Toplevel()
    input_window.geometry("200x500")

    entry_label = tk.Label(input_window, text="Edit Parameters", font=("Arial", "8", "bold"))
    entry_label.pack()
    
    params = []
    for parameterCharacter in Parser.parameters.keys():
        entry_label = tk.Label(input_window, text=parameterCharacter, font=("Arial", "8", "italic"))
        entry_label.pack()
        entry = tk.Entry(input_window)
        entry.insert(0, str(Parser.parameters[parameterCharacter]))
        entry.pack()
        params.append(entry)
    
    
    commit_button = tk.Button(input_window, text="Commit", 
        command=(lambda: (Parser.set_equation_params(dict(zip(Parser.parameters.keys(), [float(entry.get()) for entry in params]))), show_funcs())))
    commit_button.pack()
    


#Function to set viewport dimensions  
def set_viewport(getParams: tk.Entry, flag=0):
    global viewportParameters
    params = []
    try:
        if flag == 0:
            for param in getParams:
                params.append(float(param.get()))
            params[-1] = int(params[-1])
                
            viewportParameters = params
        elif flag == 1:
            viewportParameters = getParams
            
        elif flag == 2:
            
            avg_x = abs(viewportParameters[0] - viewportParameters[1])/2
            avg_y = abs(viewportParameters[2] - viewportParameters[3])/2
            
            viewportParameters = [
                viewportParameters[0] + int(getParams[0]*avg_x),
                viewportParameters[1] + int(getParams[1]*avg_x),
                viewportParameters[2] + int(getParams[2]*avg_y),
                viewportParameters[3] + int(getParams[3]*avg_y),
                int(viewportParameters[4]*getParams[4])
            ]
        elif flag == 3: raise 
            
    except:
        if flag != 3:
            messagebox.showerror("", "Cartesian Plane Limits Invalid. Reverting to default")
        viewportParameters = [-10, 10, -10, 10, 350]
        
    show_funcs()
            
#Function to clear all equations and reset viewport
def clear_funcs():
    global equations
    equations.clear()
    show_funcs()
    set_viewport([], flag=3)
    
    messagebox.showinfo("", "Cleared Viewport")

#To save equations and settings in a binary file
def save_equations():
    inputString = simpledialog.askstring("", "Enter a filename to save equations")
    if inputString:
        try:
            with open('../saved/'+inputString+'.dat', 'wb') as f:
                pickle.dump((viewportParameters, equations), f)
            messagebox.showinfo("", "Saved File")
        except:
            messagebox.showerror("Fail", "Please enter a valid filename!")
    else:
        messagebox.showinfo("", "Please enter a filename!")

#To load from the binary file
def load_equations():
    global equations
    global viewportParameters
    inputString = simpledialog.askstring("", "Enter a filename to load equations")
    if inputString:
        try:
            with open('../saved/'+inputString+'.dat', 'rb') as f:
                tup = pickle.load(f)
                viewportParameters = tup[0]
                equations = tup[1]
            messagebox.showinfo("", "Loaded File")
        except:
            messagebox.showerror("Fail", "Please enter a valid filename!")
        show_funcs()
    else:
        messagebox.showinfo("", "Please enter a filename!")
def save_snapshot():
    inputString = simpledialog.askstring("", "Enter a filename to save snapshot")
    if inputString:
        try:
            viewport.print_figure('../snaps/'+inputString+'.png')
            messagebox.showinfo("", "Snapshot Saved")
        except:
            messagebox.showerror("Fail", "Please enter a valid filename!")
    else:
        messagebox.showinfo("", "Please enter a filename!")

#Initialise window
window = tk.Tk()
window.title("PyLiner")
window.geometry("960x540")

#Sidebar to display functions
sidebar_rect = tk.Frame(window, width=200, bg="lightgray")
sidebar_rect.pack(fill=tk.Y, side=tk.LEFT)

func_pane = tk.Canvas(sidebar_rect, width=200, height=1080, bg='lightgray', highlightthickness=0)
func_pane.pack()

#Sidebar for action buttons
actionbar_rect = tk.Frame(window, width=50, bg="lightgray")
actionbar_rect.pack(fill=tk.Y, side=tk.RIGHT)

#Creating Viewport
isViewportScatter = tk.BooleanVar()
viewport_rect = tk.Frame(window, width=800)
viewport_rect.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

viewportFigure = plt.Figure(figsize=(6, 4))
axes = viewportFigure.add_subplot(111)
#Integrating matplotlib
viewport = FigureCanvasTkAgg(viewportFigure, master=viewport_rect)
viewport.draw()
viewport.get_tk_widget().pack(fill=tk.BOTH, expand=True)
show_funcs()


#Action Buttons
addButton = tk.Button(actionbar_rect, text="ƒ", width=2, background="lightgray",
                highlightthickness=0, border=0, activeforeground="gray", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=get_input)
addButton.pack(pady=0, padx=5)
addButton = tk.Button(actionbar_rect, text="π", width=2, background="lightgray",
                highlightthickness=0, border=0, activeforeground="gray", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=get_equation_params)
addButton.pack(pady=0, padx=5)
removeButton = tk.Button(actionbar_rect, text="--", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="yellow", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=remove_func)
removeButton.pack(pady=0, padx=5)
spaceButton = tk.Button(actionbar_rect, text="~", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="pink", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=get_viewport_params)
spaceButton.pack(pady=0, padx=5)
#Scatter vs Line
scatterImage = tk.PhotoImage(width=2, height=2)
scatterImage.put(("pink",), to=(0, 0, 2, 2))
scatterButton = tk.Checkbutton(actionbar_rect, background="lightgray", highlightthickness=0, border=0,
                    variable = isViewportScatter,  activeforeground="pink", activebackground="lightgray",
                    onvalue = 1, offvalue = 0, height = 2, width = 2,
                    selectimage=scatterImage, command=show_funcs) 
scatterButton.pack(padx=0, pady=0)

clearButton = tk.Button(actionbar_rect, text="×", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="red", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="gray", command=clear_funcs)
clearButton.pack(side=tk.BOTTOM, pady=0, padx=5)

#Button to save equations / snapshot
saveButton = tk.Button(actionbar_rect, text="⭳", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="gray", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=save_equations)
saveButton.pack(pady=0, padx=5, side=tk.BOTTOM)
loadButton = tk.Button(actionbar_rect, text="⤒", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="gray", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=load_equations)
loadButton.pack(pady=0, padx=5, side=tk.BOTTOM)
snapButton = tk.Button(actionbar_rect, text="🖻", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="gray", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white", command=save_snapshot)
snapButton.pack(pady=0, padx=5, side=tk.BOTTOM)

#Buttons to adjust viewport
spaceButton = tk.Button(actionbar_rect, text="o", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="pink", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white",
                command=lambda: set_viewport([], flag=3))
spaceButton.pack(pady=0, padx=5)
spaceButton = tk.Button(actionbar_rect, text="-", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="pink", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white",
                command=lambda: set_viewport([0, 0, 0, 0, 1/1.5], flag=2))
spaceButton.pack(pady=0, padx=5)
spaceButton = tk.Button(actionbar_rect, text="+", width=2, background="lightgray", 
                highlightthickness=0, border=0, activeforeground="pink", activebackground="lightgray",
                font=('Arial', 16, "bold"), foreground="white",
                command=lambda: set_viewport([0, 0, 0, 0, 1.5], flag=2))
spaceButton.pack(pady=0, padx=5)

#Keyboard/Mouse inputs
window.bind(
    "<MouseWheel>",
    lambda x: set_viewport([viewportParameters[i]*(1/2 if x.delta > 0 else 2) for i in range(4)] + [viewportParameters[4]], flag=1)
)
window.bind(
    "<KeyPress-Left>",
    lambda x: set_viewport([-1, -1, 0, 0, 1], flag=2)
)
window.bind(
    "<KeyPress-Right>",
    lambda x: set_viewport([+1, +1, 0, 0, 1], flag=2)
)
window.bind(
    "<KeyPress-Up>",
    lambda x: set_viewport([0, 0, +1, +1, 1], flag=2)
)
window.bind(
    "<KeyPress-Down>",
    lambda x: set_viewport([0, 0, -1, -1, 1], flag=2)
)



window.mainloop()