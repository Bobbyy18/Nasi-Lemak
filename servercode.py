import socket
import threading

# Server configuration
SERVER_IP = ''  # Must align with server IP address
SERVER_PORT = 12153

# List to hold client connections
clients = []
order_list = {}
accepted_clients = set()  # To keep track of clients who have accepted an order
current_order = ""  # Initialize the global variable to hold the current order

"""def handle_new_order(order_details):
    global accepted_clients, current_order

    # Reset state for the new order
    accepted_clients = set()
    current_order = None

    # Set the new order details
    current_order = order_details

    handle_client(client_socket, client_address)"""

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
    global current_order, order_list,accepted_clients

    while True:
        try:
            # Receive message from a client
            message = client_socket.recv(1024).decode()
                
            if message == "accept":
                # Check if the order is already accepted by another client
                if current_order and accepted_clients:
                    # Inform the client that the order is already accepted
                    client_socket.send("Request has been accepted by another runner.".encode()) # JUST SHOW.INFO POPUP
                else:                        # First client to accept the order
                    accepted_clients.add(client_address)
                    print(f"Request accepted by {client_address[0]}, {client_address[1]}, ignoring further accept.")
                    # Send the order details to this client
                    runner_socket = client_socket
                    print(order_list)
                    runner_socket.send(f"You accepted the order. Complete the order at LOCATION, CUSTOMER'S NAME. \nAccepted order: {current_order}".encode()) # JUST SHOW.INFO POPUP
                    
                    for order_id, order in order_list.items():
                        if order["order id"] == order_id:
                            order_list[order_id]["runner"] = runner_socket
                            order_list[order_id]["status"] = "accepted"
                            print(order_list)

                            customer_socket = order_list[order_id]["customer"]
                            customer_socket.send("Your order has been accepted by a runner".encode())
                            print(f"Message sent to customer of order {order_id}")

                    current_order = None
                    accepted_clients = set()

            elif message == "reject":
                print(f"Request rejected by {client_address[0]}, {client_address[1]}")
            
            elif message == "disconnect":
                print("Client wants to disconnect")
                if client_socket in order_list:

                    for order_id, order in order_list.items():
                        if client_socket == order.get("runner"):
                            client_socket = order["runner"]
                            runner_socket = client_socket

                            client_socket = order.get("customer")
                            customer_socket = client_socket

                            runner_socket.send("Have you finished the request?")
                            confirmation = runner_socket.recv(1024).decode()
                            
                            if confirmation == "yes":
                                customer_socket.send("Have you received your order?".encode())
                                orderConfirmation = customer_socket.recv(1024).decode()

                                if orderConfirmation == "yes":
                                    runner_socket.send("You have successfully finished a request. Runner fee is rewarded".encode())

                                    if runner_socket in clients:
                                        clients.remove(runner_socket)
                                    if customer_socket in clients:
                                        clients.remove(customer_socket)

                                    runner_socket.close()
                                    customer_socket.close()

                                    order_list[order_id]["status"] = "completed"
                                    print(f"Order {order_id} completed")
                                    print(order_list)
                            else:
                                runner_socket.send("Please complete the request before disconnecting".encode())

                        elif client_socket == order.get("customer"):
                            customer_socket = order["customer"]
                            runner_socket = order["runner"]

                            runner_socket.send("You have successfully finished a request. Runner fee is rewarded".encode())

                            if customer_socket in clients:
                                clients.remove(customer_socket)
                                customer_socket.close()
                            
                            print(f"Customer for order{order_id} has been disconnected")
                            break

                else:
                    clients.remove(client_socket)
                    client_socket.close()
                    break
                
            else:
                # Print the received order with the client's IP and port
                print(f"Received order from {client_address[0]}, {client_address[1]} : {message}")
                order_id = len(order_list)+1
                order_list[order_id]={"order id": order_id,"customer":client_socket,"runner":None,"status":"pending"}
                print(order_list)

                # Store the current order for sending later
                current_order = message
                # Broadcast the order to all other clients
                broadcast(message, client_socket)
       
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
    print(f"Connected to {client_address}")

    # Add the client to the list
    clients.append(client_socket)

    # Start a new thread to handle messages from this client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
