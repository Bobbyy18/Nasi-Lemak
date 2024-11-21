import socket
import json
import threading

host = ''
port = 15123

clients=[]

# Function to handle broadcasting messages to all clients
def broadcast(message, sender_socket):
    # Avoid sending the message back to the sender
    for client_socket in clients[:]:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                # If sending fails, remove the client from the list
                clients.remove(client_socket)
                client_socket.close()


# Function to handle each client connection
def handle_client(client_socket,client_address):
    print(f"Connected to {client_address}")
    clients.append(client_socket)

    try:
        while True:
            # Receive message from a client
            data = client_socket.recv(1024).decode()
            if data:
                order = json.loads(data)
                print("Order received!", order)

                response = {"type":"response", "status":"success","message":"Order received"}
                print("Sending acknowledgement response:", response)
                client_socket.send(json.dumps(response).encode())
                
                runner_message = {"type":"broadcast","status":"info", "message":"Runner Needed!"}
                broadcast(json.dumps(runner_message), sender_socket=client_socket)
            else:
                break
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
