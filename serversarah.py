import socket
import json

host = '127.0.0.1'
port = 15123

clients=[]

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host,port))
    server_socket.listen(5)
    print("Server is listening")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to {client_address}")

        data = client_socket.recv(1024).decode()
        order_data = json.loads(data)
        print("Order received:", order_data)

        response = {"status":"success","message":"Order received"}
        client_socket.send(json.dumps(response).encode())

        client_socket.close()

if __name__ == "__main__":
    start_server()