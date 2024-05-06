import tkinter as tk
from tkinter import messagebox
import configparser

def execute_command(command):
    # Here you would execute the command associated with the button
    messagebox.showinfo("Command Executed", f"Executed command: {command}")

def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def create_buttons_from_config(config, parent):
    sections = config.sections()
    buttons = {}
    for section in sections:
        section_frame = tk.LabelFrame(parent, text=section)
        section_frame.pack(padx=10, pady=5, fill="both", expand=True)

        for key, value in config.items(section):
            button = tk.Button(section_frame, text=key, command=lambda v=value: execute_command(v))
            button.pack(side=tk.LEFT, padx=5, pady=5)
            buttons[key] = button
    return buttons

def main():
    config_file = 'auto_test.ini'
    config = load_config(config_file)

    root = tk.Tk()
    root.title("Config Buttons Generator")

    buttons = create_buttons_from_config(config, root)

    root.mainloop()

if __name__ == "__main__":
    main()
