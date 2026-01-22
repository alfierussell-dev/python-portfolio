import tkmacosx
import tkinter as tk

button_values = [
    ["AC", "+/-", "%", "÷"], 
    ["7", "8", "9", "×"], 
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "√", "="]
]

right_symbols = ["÷", "×", "-", "+", "="]
top_symbols = ["AC", "+/-", "%", ]

row_count = len(button_values)
column_count = len(button_values[0])

colour_light_grey = "#D4D4D2"
colour_black = "#1C1C1C"
colour_dark_grey = "#696969"
colour_blue = "#4169E1"
colour_white = "white"

#Window setup
window = tk.Tk() #creates window
window.title("Calculator")
window.resizable(False, False)

frame = tk.Frame(window)
label = tk.Label(frame, text="0", font=("Arial", 45), background=colour_black, 
	foreground=colour_white, anchor="e", width=column_count)

label.grid(row=0, column=0, columnspan=column_count, sticky="we")

for row in range(row_count):
    for column in range(column_count):
        value = button_values[row][column]
        
        # Use pixel values for width and height (e.g., 80)
        # Adding borderless=1 ensures the color fills the button
        button = tkmacosx.Button(frame, text=value, font=("Arial", 30),
                                 width=80, height=80, borderless=1,
                                 command=lambda v=value: button_clicked(v))
        
        # Applying your color logic
        if value in top_symbols:
            button.config(foreground=colour_black, background=colour_light_grey)
        elif value in right_symbols:
            button.config(foreground=colour_white, background=colour_blue)
        else:
            button.config(foreground=colour_white, background=colour_dark_grey)

        button.grid(row=row+1, column=column, padx=2, pady=2)
 


frame.pack()

A = "0"
operator = None
B = None
#AC button code(clear)
def clear_all():
	global A, B, operator
	A = "0"
	operator = None
	B = None	

def remove_zero_decimal(num):
	if num % 1 == 0:
		num = int(num)
	return str(num)

		

def button_clicked(value):
	global right_symbols, top_symbols, label, A, B, operator

	if value in right_symbols:
		if value == "=":
			if A is not None and operator is not None:
				B = label["text"]
				numA = float(A)
				numB = float(B)

				if operator == "+":
					label["text"] = remove_zero_decimal(numA + numB)
				elif operator == "-":
					label["text"] = remove_zero_decimal(numA - numB)

				elif operator == "×":
					label["text"] = remove_zero_decimal(numA * numB)
				elif operator == "÷":
					label["text"] = remove_zero_decimal(numA / numB)

				clear_all()


		elif value in "+-×÷":
			if operator is None:
				A = label["text"]
				label["text"] = "0"
				B = "0"
			operator = value


#top symbol functions
	elif value in top_symbols:
		if value == "AC":
			clear_all()
			label["text"] = "0"
		elif value == "+/-":
			result = float(label["text"]) * -1
			label["text"] = remove_zero_decimal(result)
		elif value =="%":
			result = float(label["text"]) / 100
			label["text"] = remove_zero_decimal(result)
	

	else:
		if value == ".":
			if value not in label["text"]:
				label["text"] += value

		elif value in "0123456789":
			if label["text"] == "0":
				label["text"] = value
			else:
				label["text"] += value
		
		else:
			if value == "√":
				numA = float(label["text"])
			label["text"] = remove_zero_decimal(numA ** 0.5)
			return

window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width/2) - (window_width/2))
window_y = int((screen_height/2) - (window_height/2))

#format "(w)x(h)+(x)+(y)"
window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window.mainloop()