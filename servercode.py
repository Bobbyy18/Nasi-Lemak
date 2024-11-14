import socket
import threading

# Server configuration
SERVER_IP = '10.121.131.87' #must allign with server ip address
SERVER_PORT = 12345

# List to hold client connections
clients = []

# Function to handle broadcasting messages to all clients
def broadcast(message, sender_socket):
    for client_socket in clients:
        # Avoid sending the message back to the sender
        if client_socket != sender_socket:
            try:
                client_socket.send(message)
            except:
                # If sending fails, remove the client from the list
                clients.remove(client_socket)
                client_socket.close()

# Function to handle each client connection
def handle_client(client_socket):
    while True:
        try:
            # Receive message from a client
            message = client_socket.recv(1024)
            if message:
                print("Broadcasting message to all clients.")
                broadcast(message, client_socket)
        except:
            # Remove the client if the connection is lost
            clients.remove(client_socket)
            client_socket.close()
            break

# Set up server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()

print("Server is listening for connections...")

while True:
    # Accept new client connections
    client_socket, client_address = server_socket.accept()
    print(f"New connection from {client_address}")

    # Add the client to the list
    clients.append(client_socket)

    # Start a new thread to handle messages from this client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
