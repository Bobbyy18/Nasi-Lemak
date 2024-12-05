import socket
import threading

# Server configuration
SERVER_IP = ''  # Must align with server IP address
SERVER_PORT = 12153

# List to hold client connections
clients = []
order_list = {}
accepted_clients = set()  # To keep track of clients who have accepted an order

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
    global order_list, clients, accepted_clients

    while True:
        try:
            # Receive message from a client
            message = client_socket.recv(1024).decode().strip()
            print("Receive message from client")

            if message.startswith("ORDER"):
                # Print the received order with the client's IP and port
                print(f"Received order from {client_address[0]}, {client_address[1]} : {message}")

                order_parts = message.split("->",1)
                order_header = order_parts[0].replace("ORDER from", "").strip()

                customer_details = order_header.split("at",1)
                customer_name = customer_details[0]
                location = customer_details[1].strip()

                order_details = order_parts[1].strip() if len(order_parts)>1 else "No details provided"

                order_id = len(order_list)+1
                order_list[order_id]={"order id": order_id,"customer":client_socket,"runner":None,"status":"pending","name":customer_name,"location":location,"details":order_details}
                print(order_list)

                # Store the current order for sending later
                message = f"Order at {location}"
                # Broadcast the order to all other clients
                broadcast(message, client_socket)
       
                
            elif message == "accept":
                # Find the first pending order
                pending_order = next((order for order in order_list.values() if order["status"] == "pending"), None)
                if pending_order:
                    order_id = pending_order["order id"]

                    if order_id in accepted_clients:
                    # Inform the client that the order is already accepted
                        client_socket.send("Request has been accepted by another runner.".encode())
                    else:
                        # First runner to accept the order
                        accepted_clients.add(order_id)
                        print(f"Request accepted by {client_address[0]}, {client_address[1]}.")

                        # Update the order status and assign the runner
                        pending_order["runner"] = client_socket
                        pending_order["status"] = "accepted"
                        print(order_list)
                        
                        location = pending_order["location"]
                        customer_name = pending_order["name"]
                        order_details = pending_order["details"]

                        # Send the order details to the runner
                        client_socket.send(f"You accepted the order. Complete the order at {location}, Customer's name is {customer_name}. \nAccepted order: {order_details}".encode()) # JUST SHOW.INFO POPUP
                        # Notify the customer
                        customer_socket = pending_order["customer"]
                        customer_socket.send("Your order has been accepted by a runner.".encode())
                        print(f"Message sent to customer of order {order_id}.")


            elif message == "reject":
                print(f"Request rejected by {client_address[0]}, {client_address[1]}")
            
            else:
                print("Client wants to disconnect")
                found_order = False

                for order_id, order in order_list.items():
                    if client_socket == order_list[order_id]["runner"]:
                        found_order = True
                        runner_socket = order_list[order_id]["runner"]
                        customer_socket = order_list[order_id]["customer"]
            
                        print("Sent request confirmation")
                        runner_socket.send("Have you finished the request?".encode())
                        confirmation = runner_socket.recv(1024).decode()
                            
                        if confirmation == "yes":
                            print("Sent order confirmation")
                            customer_socket.send("Have you received your order?".encode())
                            orderConfirmation = runner_socket.recv(1024).decode()
                            print(f"Order confirmation received :{orderConfirmation}")

                            if orderConfirmation == "received":
                                runner_socket.send("You have successfully finished a request. Runner fee is rewarded".encode())
                                order_list[order_id]["status"] = "completed"
                                print(f"Order {order_id} completed")
                                print(order_list)

                                if runner_socket in clients:
                                    print("Connection to runner socket closed")
                                    runner_socket.send("Done".encode())
                                    clients.remove(runner_socket)
                                    break
                                if customer_socket in clients:
                                    print("Connection to customer socket closed")
                                    customer_socket.send("Done".encode())
                                    clients.remove(customer_socket)    
                                    break

                                runner_socket.shutdown(socket.SHUT_RDWR)
                                runner_socket.close()
                                print("Runner socket disconnect")
                                customer_socket.shutdown(socket.SHUT_RDWR)
                                customer_socket.close()
                                print("Customer disconnected")

                            else:
                                runner_socket.send("Please complete the request".encode())

                        else:
                            runner_socket.send("Please complete the request before disconnecting".encode())

                    elif client_socket == order.get("customer"):
                            found_order = True
                            customer_socket = order.get("customer")
                            runner_socket = order.get("runner")

                            if runner_socket:
                                runner_socket.send("You have successfully finished a request. Runner fee is rewarded".encode())
                                order_list[order_id]["status"] = "completed"
                                print(f"Order {order_id} completed")
                                print(order_list)

                            if customer_socket in clients:
                                print("Connection to customer socket closed")
                                customer_socket.send("Done".encode())
                                clients.remove(customer_socket)
                                customer_socket.shutdown(socket.SHUT_RDWR)
                                customer_socket.close()
                            
                            print(f"Customer for order{order_id} has been disconnected")
                            break

                    if not found_order:
                            if client_socket in clients:
                                print(f"Connection to {client_socket} close")
                                client_socket.send("Done".encode())
                                clients.remove(client_socket)
                                client_socket.shutdown(socket.SHUT_RDWR)
                                client_socket.close()
                                break
                            
     
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
