
class WriteDeviceInfo:
    def __init__(self, send_command, log_message):
        self.send_command = send_command
        self.log_message = log_message

    def send_entry_command(self, send_entry):
        command = send_entry.get() + "\r\n"
        self.send_command(command)
        send_entry.delete(0, "end")
