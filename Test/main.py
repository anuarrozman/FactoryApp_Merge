import tkinter as tk
import requests

def download_data():
    url = "http://localhost:3000/serialnumber"  # Replace with the actual API endpoint
    try:
        response = requests.get(url)
        data = response.json()
        display_data(data)
    except Exception as e:
        status_label.config(text="Error downloading data: " + str(e))

def display_data(data):
    # Clear any existing data in the listbox
    listbox.delete(0, tk.END)
    # Iterate over the list of devices and add them to the listbox
    for device in data:
        mac_address = device.get("mac_address", "N/A")
        serial_number = device.get("serial_number", "N/A")
        listbox.insert(tk.END, f"MAC: {mac_address}, Serial: {serial_number}")
    status_label.config(text="Data downloaded successfully!")

root = tk.Tk()
root.title("Device List")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, width=50, height=10)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

download_button = tk.Button(root, text="Download Data", command=download_data)
download_button.pack(pady=5)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
