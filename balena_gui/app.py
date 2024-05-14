# app.py
import tkinter as tk

def say_hello():
    print("Hello, Balena!")

root = tk.Tk()
root.title("Balena Tkinter App")

label = tk.Label(root, text="Hello, Balena!")
label.pack(pady=20)

button = tk.Button(root, text="Click Me", command=say_hello)
button.pack(pady=20)

root.mainloop()
