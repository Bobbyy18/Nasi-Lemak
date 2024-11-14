import socket

# Server configuration
SERVER_IP = '10.121.131.87' #must allign with server ip address
SERVER_PORT = 12345

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Message to be sent (e.g., the order list)
order_list = "Order 1: Coffee, Order 2: Tea"
client_socket.send(order_list.encode())

print("Order list sent to server.")
client_socket.close()
