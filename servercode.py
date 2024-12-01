import socket
import threading

# Server configuration
SERVER_IP = ''  # Must align with server IP address
SERVER_PORT = 12345

# List to hold client connections
clients = []
accepted_clients = set()  # To keep track of clients who have accepted an order
current_order = ""  # Initialize the global variable to hold the current order

# Function to handle broadcasting messages to all clients except the sender
def broadcast(message, sender_socket):
    for client_socket in clients:
        # Avoid sending the message back to the sender
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode()) # send the DO YOU WANT TO TAKE REQ
            except Exception as e:
                # If sending fails, log the error and remove the client from the list
                print(f"Error sending to {client_socket.getpeername()}: {e}")
                if client_socket in clients:
                    clients.remove(client_socket)
                    client_socket.close()

# Function to handle each client connection
def handle_client(client_socket, client_address):
    global current_order  # Declare the global variable inside the function
    global accepted_clients

    while True:
        try:
            # Receive message from a client
            message = client_socket.recv(1024)

            if message:
                message = message.decode()
                
                if message == "accept":
                    # Check if the order is already accepted by another client
                    if current_order and accepted_clients:
                        # Inform the client that the order is already accepted
                        client_socket.send("Request has been accepted by another runner.".encode()) # JUST SHOW.INFO POPUP
                    else:
                        # First client to accept the order
                        accepted_clients.add(client_address)
                        print(f"Request accepted by {client_address[0]}, {client_address[1]}, ignoring further accept.")
                        # Send the order details to this client
                        client_socket.send(f"You accepted the order. Complete the order at LOCATION, CUSTOMER'S NAME. \nAccepted order: {current_order}".encode()) # JUST SHOW.INFO POPUP

                elif message == "reject":
                    print(f"Request rejected by {client_address[0]}, {client_address[1]}")
                
                else:
                    # Print the received order with the client's IP and port
                    print(f"Received order from {client_address[0]}, {client_address[1]} : {message}")
                    # Store the current order for sending later
                    current_order = message
                    # Broadcast the order to all other clients
                    broadcast(message, client_socket)

            """# Reset for the next round of orders
            accepted_clients = set()
            current_order = None  # Reset current order""" 

        except Exception as e:
            # If there's an error with the client connection, log and remove it
            print(f"Error with client {client_address[0]}, {client_address[1]}: {e}")
            if client_socket in clients:
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
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
