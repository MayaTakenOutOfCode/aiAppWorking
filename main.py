import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal
from cohere import UserMessage
from tts_handler import startTtsThread, addToTtsQueue
from server import load_memory, save_memory
from Ai import process_message, start_irc_client, checkInactivity


class AIChatApp(QMainWindow):
    new_message_signal = pyqtSignal(str, str)  # Signal to update the chat display

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat with Avatar")
        self.setGeometry(100, 100, 600, 400)
        self.memory = load_memory()
        self.initUI()
        self.show()

        # Connect the signal to the slot
        self.new_message_signal.connect(self.update_chat_display)

        # Start the AI processing in a separate thread
        threading.Thread(target=self.run_ai_logic, daemon=True).start()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        self.avatar_label = QLabel("Avatar Placeholder")
        self.avatar_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.avatar_label)

        central_widget.setLayout(layout)

    def send_message(self):
        user_message = self.input_field.text()
        if user_message:
            self.chat_display.append(f"You: {user_message}")
            response = process_message("User", user_message)  # Use the imported function
            self.chat_display.append(f"AI: {response}")
            self.input_field.clear()

    def update_chat_display(self, user, message):
        self.chat_display.append(f"{user}: {message}")

    def run_ai_logic(self):
        # Start the IRC client and inactivity check in separate threads
        threading.Thread(target=start_irc_client, daemon=True).start()
        threading.Thread(target=checkInactivity, daemon=True).start()

        # Process messages in a loop
        while True:
            if UserMessage:
                user_nickname = "DefaultUser"  # Define and assign a value to user_nickname
                user_message = "Sample message"  # Define and assign a value to user_message
                self.new_message_signal.emit(user_nickname, user_message)
                time.sleep(1)  # Adjust sleep time as needed

def main():
    startTtsThread()
    app = QApplication(sys.argv)
    AIChatApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 