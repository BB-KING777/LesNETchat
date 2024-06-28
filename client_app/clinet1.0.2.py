import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

BROADCAST_PORT = 5555
BUFFER_SIZE = 1024

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client 1.0.2")  # Version number added here

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
        self.version_label = tk.Label(master, text="Version 1.0.2", font=("Arial", 10))
        self.version_label.pack(side=tk.TOP, anchor="ne", padx=10, pady=5)

    def connect_to_server(self):
        server_ip = self.server_ip.get()
        if server_ip:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client_socket.connect((server_ip, BROADCAST_PORT))
                self.key = self.client_socket.recv(32)
                self.iv = self.client_socket.recv(16)
                receive_thread = threading.Thread(target=self.receive)
                receive_thread.start()
            except Exception as e:
                messagebox.showerror("Connection Error", f"Unable to connect to the server: {e}")
                self.master.quit()
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
                encrypted_message = self.client_socket.recv(1024)
                if not encrypted_message:
                    break
                message = self.decrypt(encrypted_message).decode('utf-8')
                self.msg_list.insert(tk.END, message + "\n")
                self.msg_list.yview(tk.END)
            except OSError:
                break

    def send(self, event=None):
        msg = self.my_msg.get()
        self.my_msg.set("")  # Clears input field.
        nickname = self.nickname.get()
        full_msg = f"{nickname}: {msg}"
        encrypted_message = self.encrypt(full_msg)
        self.client_socket.send(encrypted_message)
        self.msg_list.insert(tk.END, full_msg + "\n", "self")
        self.msg_list.yview(tk.END)
        if msg == "{quit}":
            self.client_socket.close()
            self.master.quit()

    def on_closing(self, event=None):
        self.my_msg.set("{quit}")
        self.send()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()
