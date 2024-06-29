import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import subprocess
import os

BROADCAST_PORT = 5555
BUFFER_SIZE = 1024

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client 1.1.3")  # Version number added here

        self.nickname = tk.StringVar()
        self.nickname.set("Enter your nickname")

        self.server_ip = tk.StringVar()
        self.server_ip.set("Enter server IP address")

        self.nickname_label = tk.Label(master, text="Nickname:")
        self.nickname_label.pack()
        self.nickname_entry = tk.Entry(master, textvariable=self.nickname)
        self.nickname_entry.pack()

        self.server_ip_label = tk.Label(master, text="Server IP:")
        self.server_ip_label.pack()
        self.server_ip_entry = tk.Entry(master, textvariable=self.server_ip)
        self.server_ip_entry.pack()

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()

        self.messages_frame = tk.Frame(master)
        self.my_msg = tk.StringVar()  # For the messages to be sent.
        self.my_msg.set("Type your messages here.")

        scrollbar = tk.Scrollbar(self.messages_frame)  # To see through previous messages.
        self.msg_list = scrolledtext.ScrolledText(self.messages_frame, height=15, width=50, yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.msg_list.tag_config("self", foreground="red")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack()

        self.entry_field = tk.Entry(master, textvariable=self.my_msg)
        self.entry_field.bind("<Return>", self.send)
        self.entry_field.pack()
        self.send_button = tk.Button(master, text="Send", command=self.send)
        self.send_button.pack()

        # Adding version label
        self.version_label = tk.Label(master, text="Version 1.1.3", font=("Arial", 10))
        self.version_label.pack(side=tk.TOP, anchor="ne", padx=10, pady=5)

        # Adding Play Game button
        self.play_game_button = tk.Button(master, text="Play Game", command=self.open_game_selection)
        self.play_game_button.pack(side=tk.LEFT, anchor="sw", padx=10, pady=10)

        # Create or open chat log file
        self.log_file = open("client_chat.log", "w")

    def connect_to_server(self):
        server_ip = self.server_ip.get()
        if server_ip and server_ip != "Enter server IP address":
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client_socket.connect((server_ip, BROADCAST_PORT))
                self.key = self.client_socket.recv(32)
                self.iv = self.client_socket.recv(16)
                self.receive_thread = threading.Thread(target=self.receive)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            except Exception as e:
                messagebox.showerror("Connection Error", f"Unable to connect to the server: {e}")
                if hasattr(self, 'client_socket'):
                    self.client_socket.close()
        else:
            messagebox.showerror("Input Error", "Please enter a valid server IP address.")

    def encrypt(self, plaintext):
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.CFB(self.iv),
            backend=default_backend()
        ).encryptor()
        return encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()

    def decrypt(self, ciphertext):
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.CFB(self.iv),
            backend=default_backend()
        ).decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def receive(self):
        while True:
            try:
                encrypted_message = self.client_socket.recv(BUFFER_SIZE)
                if not encrypted_message:
                    break
                message = self.decrypt(encrypted_message).decode('utf-8')
                self.display_message(message)
            except OSError:
                break

    def send(self, event=None):
        if not hasattr(self, 'client_socket'):
            return
        msg = self.my_msg.get()
        self.my_msg.set("")  # Clears input field.
        nickname = self.nickname.get()
        full_msg = f"{nickname}: {msg}"
        encrypted_message = self.encrypt(full_msg)
        try:
            self.client_socket.send(encrypted_message)
            self.display_message(full_msg, "self")
            if msg == "{quit}":
                self.client_socket.close()
                self.master.quit()
        except Exception as e:
            messagebox.showerror("Send Error", f"Unable to send the message: {e}")

    def display_message(self, message, tag=None):
        self.msg_list.insert(tk.END, message + "\n", tag)
        self.msg_list.yview(tk.END)
        self.log_file.write(message + "\n")
        self.log_file.flush()

    def on_closing(self, event=None):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                if hasattr(self, 'client_socket'):
                    self.my_msg.set("{quit}")
                    self.send()
                    self.client_socket.close()
            except Exception as e:
                print(f"Error closing the connection: {e}")
            finally:
                self.log_file.close()
                os.remove("client_chat.log")
                self.master.destroy()

    def open_game_selection(self):
        self.game_window = tk.Toplevel(self.master)
        self.game_window.title("Select a Game")
        self.game_window.geometry("300x200")

        blackjack_button = tk.Button(self.game_window, text="Blackjack", command=self.start_blackjack)
        blackjack_button.pack(pady=10)

        slot_button = tk.Button(self.game_window, text="Slot", command=self.start_slot)
        slot_button.pack(pady=10)

    def start_blackjack(self):
        script_path = os.path.join(os.path.dirname(__file__), 'playingcard-mini', 'playingcard-mini', 'brackjack.py')
        subprocess.Popen(['python', script_path])
        self.game_window.destroy()

    def start_slot(self):
        script_path = os.path.join(os.path.dirname(__file__), 'playingcard-mini', 'playingcard-mini', 'slot.py')
        subprocess.Popen(['python', script_path])
        self.game_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()
