import subprocess

def setup_environment():
    # Create a virtual environment named 'myenv'
    subprocess.run(["python3", "-m", "venv", "myenv"])

    # Activate the virtual environment and install dependencies
    subprocess.run(["/bin/bash", "-c", "source myenv/bin/activate && pip install esptool pyserial hidapi"])

if __name__ == "__main__":
    setup_environment()
