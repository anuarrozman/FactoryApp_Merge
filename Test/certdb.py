import tkinter as tk
import mysql.connector
import os
import subprocess

# Function to update status in the database
def update_status(certid):
    # Connect to the database
    connection = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
    )

    cursor = connection.cursor()

    # Update status to true for the selected certid
    query = "UPDATE matter_certid SET status = TRUE WHERE certid = %s"
    cursor.execute(query, (certid,))
    connection.commit()

    cursor.close()
    connection.close()

# Function to retrieve a certid where status is not true
def get_certid():
    # Connect to the database
    connection = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
    )

    cursor = connection.cursor()

    # Retrieve a certid where status is NULL or FALSE
    query = "SELECT certid FROM matter_certid WHERE status IS NULL OR status = FALSE LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        return result[0]  # Return the certid
    else:
        return None  # Return None if no certid found

# Function to handle button click event
def button_click():
    certid = get_certid()
    if certid:
        bin_path = get_bin_path(certid)
        if bin_path:
            print(f"Flashing cert {certid}...")
            flash_cert(bin_path)
            print(f"Cert {certid} flashed successfully.")
            update_status(certid)  # Update status only if .bin file is found
        else:
            print("No .bin file found for this certid.")
    else:
        print("No available certid with status not true.")

# Function to get the path of the .bin file for the selected certid
def get_bin_path(certid):
    for root, dirs, files in os.walk("/"):  # Walk through all files and directories in the current directory and its subdirectories
        for file in files:
            if file.endswith(".bin") and certid in file:  # Check if the file is a .bin file and contains the certid in its name
                return os.path.join(root, file)  # Return the path of the .bin file
    return None  # Return None if no .bin file with the certid is found

# Function to flash the .bin file onto the device
def flash_cert(bin_path):
    subprocess.run(["esptool.py", "-p", "/dev/ttyUSB0", "write_flash", "0x10000", bin_path])

# Create the GUI
root = tk.Tk()
root.title("Cert Flasher")

label = tk.Label(root, text="")
label.pack()

button = tk.Button(root, text="Flash Cert", command=button_click)
button.pack()

root.mainloop()
