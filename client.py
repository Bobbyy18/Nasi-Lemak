import socket
# Set up a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Define the server address and port
server_address = ('localhost', 10000)
# Connect to the server
sock.connect(server_address)
# Prompt the user for the food order
order = {'pizza':0, 'burger':0, 'fries':0, 'soda':0,'masala dosa':0}
food_items = {'pizza', 'burger', 'fries', 'soda','masala dosa'}
print("'Pizza': 10, 'Burger': 8, 'Fries': 4, 'Soda': 2,'masala dosa':20")
while True:
    item = input("Enter the name of the item you'd like to order (or 'done' to finish): ")
    item=item.lower()
    if item == 'done':
        break
    if item not in food_items:
        print("invalid order")
    else:
        quanƟty = int(input("Enter the quanƟty: "))
        quant=order[item]+quanƟty
        order[item] = quant
# Send the order to the server
sock.sendall(str(order).encode())
# Receive the total cost from the server and display it
total_cost = sock.recv(1024).decode()
print(f"Total cost of your order: {total_cost}")
# Close the socket
sock.close()