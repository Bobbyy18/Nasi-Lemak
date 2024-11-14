import socket
import threading

# Server configuration
SERVER_IP = '10.121.131.87' #must allign with server ip address
SERVER_PORT = 12345

# Function to handle receiving messages from the server
def receive_messages(sock):
    while True:
        try:
            # Receive message from the server
            message = sock.recv(1024)
            if message:
                print("Received broadcast message:", message.decode())
        except:
            print("Disconnected from server.")
            sock.close()
            break

# Set up connection to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Start a thread to continuously listen for messages
receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receiver_thread.start()
