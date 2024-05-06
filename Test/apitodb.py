import tkinter as tk
import requests
import mysql.connector
import uuid


# Function to create database table
def create_table():
    conn = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
    )
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS device_info
                 (matter_cert_id VARCHAR(255), serial_number VARCHAR(255))''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(data):
    conn = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
    )
    cursor = conn.cursor()
    for device in data:
        matter_cert_id = device.get("matter_cert_id", "N/A")
        serial_number = device.get("serial_no", "N/A")  # Correct key to access serial number
        mac_address = device.get("mac_address", "N/A")
        cursor.execute("INSERT INTO device_info (matter_cert_id, serial_number, mac_address) VALUES (%s, %s, %s)", (matter_cert_id, serial_number, mac_address))
    conn.commit()
    conn.close()


# Function to download and display data
def download_data():
    url = "http://localhost:3000/devices"  # Correct endpoint
    try:
        response = requests.get(url)
        data = response.json()
        insert_data(data)
        display_data(data)
    except Exception as e:
        status_label.config(text="Error downloading data: " + str(e))

# Function to display data
def display_data(data):
    listbox.delete(0, tk.END)
    for device in data:
        matter_cert_id = device.get("matter_cert_id", "N/A")
        serial_number = device.get("serial_number", "N/A")  # Correct field name
        listbox.insert(tk.END, f"Matter Cert ID: {matter_cert_id}, Serial: {serial_number}")
    status_label.config(text="Data downloaded successfully!")

# Create table when the script is run
create_table()

root = tk.Tk()
root.title("Device List")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, width=100, height=10)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

download_button = tk.Button(root, text="Download Data", command=download_data)
download_button.pack(pady=5)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
