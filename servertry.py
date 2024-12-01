import socket
import json
import threading

host = ''
port = 15123

clients=[]
current_broadcast = None
broadcast_taken = False

# Function to handle broadcasting messages to all clients
def broadcast(message, sender_socket):
    global current_broadcast, broadcast_taken

    # If the order is already taken, STOP broadcasting
    if broadcast_taken:
        return
    
    current_broadcast = message

    for client_socket in clients[:]:
        try:
            if client_socket != sender_socket: # Do not send the message back to the sender
                client_socket.send(json.dumps(message).encode())
        except:
            # If sending fails, remove the client from the list
            clients.remove(client_socket)
            client_socket.close()


# Function to handle each client connection
def handle_client(client_socket,client_address):
    global broadcast_taken, current_broadcast
    print(f"Connected to {client_address}")
    clients.append(client_socket)

    try:
        while True:
            # Receive message from a client
            data = client_socket.recv(1024).decode()
            if data:
                message = json.loads(data)

                if message.get("type") == "order":
                    # Reset state for new order
                    broadcast_taken = False  # Allow new broadcasts for the next order
                    current_broadcast = None  # Clear any previous broadcast

                    print("Order received:", message)
                    response = {"type":"response", "status":"success","message":"Your order has been sent to the server!"}
                    print("Sending acknowledgement response:", response)
                    client_socket.send(json.dumps(response).encode())

                    # Broadcast order to all other clients
                    if not broadcast_taken:
                        runner_message = {"type":"broadcast","status":"info", "message":message}
                        broadcast(runner_message, sender_socket=client_socket)

                elif message.get("type") == "accept":
                    if not broadcast_taken:
                        # First client to accept
                        broadcast_taken = True
                        print(f"Request accepted by client: {client_address}")
                        response = {"type": "details", "status": "accepted", "message": "You have accepted the order."}
                        client_socket.send(json.dumps(response).encode())

                        stop_broadcast = {"type": "broadcast", "status": "info", "message": "Order has been taken."}
                        broadcast(stop_broadcast, sender_socket=client_socket)  # Notify all clients
                    else:
                        # Order already taken
                        response = {"type": "response", "status": "failed", "message": "Request has been accepted by another runner."}
                        client_socket.send(json.dumps(response).encode())

                elif message.get("type") == "disconnect":
                    print(f"Client {client_address} wants to disconnect.")
                    break

            else:
                break
    
    except (ConnectionResetError, ConnectionAbortedError): 
        # server can handle both graceful and abrupt disconnections without leaving dangling resources.
        print(f"Connection with {client_address} was reset or aborted.")
    
    finally:
        print(f"Connection to {client_address} closed.")
        try:
            clients.remove(client_socket)
            client_socket.close()
        except:
            pass


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('',port))
server_socket.listen(5)
print("Server is listening")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"New connection from {client_address}")

    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
