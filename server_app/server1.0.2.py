import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

BROADCAST_PORT = 5555
BUFFER_SIZE = 1024

class ChatServer:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Server 1.0.2")  # Version number added here

        self.server = None
        self.clients = []
        self.is_running = False

        self.key = os.urandom(32)  # AES-256 key
        self.iv = os.urandom(16)   # AES block size

        self.start_button = tk.Button(master, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(master, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.messages_frame = tk.Frame(master)
        scrollbar = tk.Scrollbar(self.messages_frame)
        self.msg_list = scrolledtext.ScrolledText(self.messages_frame, height=15, width=50, yscrollcommand=scrollbar.set, wrap=tk.WORD)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack(pady=10)

        self.local_ip_label = tk.Label(master, text="Server IP: Not running")
        self.local_ip_label.pack(pady=5)

        # Adding version label
        self.version_label = tk.Label(master, text="Version 1.0.2", font=("Arial", 10))
        self.version_label.pack(side=tk.TOP, anchor="ne", padx=10, pady=5)

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

    def broadcast(self, message, _client):
        for client in self.clients:
            if client != _client:
                try:
                    encrypted_message = self.encrypt(message)
                    client.send(encrypted_message)
                except:
                    client.close()
                    self.clients.remove(client)

    def handle_client(self, client):
        while self.is_running:
            try:
                encrypted_message = client.recv(1024)
                if not encrypted_message:
                    break
                message = self.decrypt(encrypted_message).decode('utf-8')
                self.broadcast(message, client)
                self.msg_list.insert(tk.END, message + "\n")
                self.msg_list.yview(tk.END)
            except:
                client.close()
                self.clients.remove(client)
                break

    def start_server(self):
        if not self.is_running:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.get_ip_address(), BROADCAST_PORT))
            self.server.listen()
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.local_ip_label.config(text=f"Server IP: {self.get_ip_address()}")
            threading.Thread(target=self.accept_clients).start()
            self.msg_list.insert(tk.END, "Server started...\n")

    def accept_clients(self):
        self.server.settimeout(1)  # Set a timeout for accept
        while self.is_running:
            try:
                client, addr = self.server.accept()
                self.msg_list.insert(tk.END, f"Connected with {addr}\n")
                self.clients.append(client)
                client.send(self.key + self.iv)  # Send key and IV to client
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except socket.timeout:
                continue
            except OSError:
                break

    def stop_server(self):
        if self.is_running:
            self.is_running = False
            for client in self.clients:
                try:
                    client.send(self.encrypt("Server is stopping..."))  # Notify clients about server stop
                    client.close()
                except Exception as e:
                    print(f"Error closing client: {e}")
            if self.server:
                self.server.close()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.local_ip_label.config(text="Server IP: Not running")
            self.msg_list.insert(tk.END, "Server stopped...\n")
            self.master.quit()

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception as e:
            ip = '127.0.0.1'
        return ip

if __name__ == "__main__":
    root = tk.Tk()
    server = ChatServer(root)
    root.protocol("WM_DELETE_WINDOW", server.stop_server)
    root.mainloop()
