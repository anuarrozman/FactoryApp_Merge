# Dockerfile
FROM balenalib/raspberrypi3-python:3.9-buster

# Install Tkinter and X11 utilities
RUN install_packages python3-tk x11-xserver-utils

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Set the display environment variable to use the host's display
ENV DISPLAY=:0

# Run app.py when the container launches
CMD ["python3", "app.py"]
