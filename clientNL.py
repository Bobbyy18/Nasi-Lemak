import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Server configuration
SERVER_IP = '172.30.1.56'  # Must align with server IP address
SERVER_PORT = 12153

# Variables to hold quantities and prices of items in cart
cart = []
runner_fee = 2000  # Runner fee for each order

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function to handle receiving messages from the server
def receive_messages(sock):
    while True:
        try:
            # Receive message from the server
            message = sock.recv(1024).decode()
            if message:
                if message == "Request has been accepted by another runner." :
                    messagebox.showinfo("Notification", message)
                    print("Failed to accept request")
                elif "You accepted the order. " in message:
                    messagebox.showinfo("Notification", message)
                    print("Accepted request")
                elif "Your order has been accepted by a runner" in message:
                    messagebox.showinfo("Notification", message)
                    print("Order is received by runner")
                elif "Have you finished the request?" in message:
                    response = messagebox.askquestion("Order Status", f"{message}")
                    if response == "yes":
                        client_socket.send("yes".encode())  
                    else:
                        client_socket.send("no".encode())

                elif "Have you received your order?" in message:
                    response = messagebox.askquestion("Order Status", f"{message}")
                    if response == "yes":
                        client_socket.send("received".encode())  
                    else:
                        client_socket.send("not received".encode())
                        

                elif "You have successfully finished a request. Runner fee is rewarded" in message:
                    messagebox.showinfo("Order status", f"{message}")
                    print("Request finished")
                    exit_program()
                elif "Done" in message:
                    print("Exiting")
                    exit_program()
                else:
                    # Show notification about the received order
                    show_incoming_order(message)
        except:
            pass

# Function to show notification pop-up when a message is received
def show_incoming_order(order):
    response = messagebox.askquestion("Incoming Order", f"{order}\nDo you want to take this request?")
    if response == "yes":
        client_socket.send("accept".encode())
    else:
        client_socket.send("reject".encode())

# Function to connect to the server
def connect_to_server():
    client_socket.connect((SERVER_IP, SERVER_PORT))
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    print("Connected to server.")

# Function to update the displayed total cost (including runner fee)
def update_total():
    total_cost = sum(item['price'] * item['quantity'] for item in cart)
    total_cost += runner_fee  # Add runner fee
    total_label.config(text=f"Total: ₩{total_cost}")

# Function to add an item to the cart
def add_to_cart(item_name, price):
    for item in cart:
        if item['name'] == item_name:
            item['quantity'] += 1
            update_total()
            return
    cart.append({'name': item_name, 'price': price, 'quantity': 1})
    update_total()

# Function to remove an item from the cart
def remove_from_cart(item_name):
    global cart
    cart = [item for item in cart if item['name'] != item_name]
    update_total()

# Function to send the order to the server
def send_order():
    if not cart:
        messagebox.showwarning("Invalid Order", "Please select at least one item before sending the order.")
        return
    order = "ORDER -> "
    for item in cart:
        order += f"{item['name']}: {item['quantity']} x ₩{item['price']}, "
    total_cost = sum(item['price'] * item['quantity'] for item in cart) + runner_fee
    order += f"Total: ₩{total_cost}"
    client_socket.send(order.encode())
    print(f"Order sent to server: {order}")
    show_order_sent()

# Function to show the order sent confirmation pop-up
def show_order_sent():
    messagebox.showinfo("Order Sent", "Your order has been successfully sent.")

def disconnecting():
    client_socket.send("disconnect".encode())
    print("Sending disconnecting message")

# Function to exit the program
def exit_program():
    root.quit()

# Function to populate shop items based on shop selection
def update_items(shop_name):
    for widget in items_frame.winfo_children():
        widget.destroy()

    items = {
        'Moms TouchShop 1': [('Fried Chicken', 9900), ('Yangnyeom Chicken', 10900), ('Soy Garlic Chicken', 10900)],
        'Ari Cafe Media Hall': [('Choco Latte', 3000), ('Hibiscus Lemonade', 3800), ('Green Tea Latte', 3200)],
        'Unistore': [('Pen', 3000), ('Book', 5000), ('Bottle', 5000)],
        'EMart': [('Ice Cream', 1500), ('Bread', 3000), ('Coffee', 3500)],
        'Pound Coffee': [('Iced Americano', 2500), ('Coffee Latte', 3000), ('Coffee Cream Latte', 3800)],
        'GS25': [('Seoul Milk', 1500), ('Kinder Bueno', 1900), ('Tuna Kimbap', 2000)],
        
    }

    for item_name, price in items.get(shop_name, []):
        item_button = tk.Button(items_frame, text=f"{item_name} (₩{price})", 
                                command=lambda item_name=item_name, price=price: add_to_cart(item_name, price))
        item_button.pack(pady=5)

# Create the main window (root)
root = tk.Tk()
root.title("KU Runner")

# Create Shop Selection Dropdown
shop_label = tk.Label(root, text="Select Shop", font=("Arial", 14))
shop_label.pack(pady=10)

shop_dropdown = tk.StringVar(root)
shop_dropdown.set("Mom's Touch")  # Default shop
shop_menu = tk.OptionMenu(root, shop_dropdown, "Ari Cafe Media Hall", "Mom's Touch", "Unistore", "EMart", "Pound Coffee", "GS25", command=update_items)
shop_menu.pack(pady=10)

# Create a frame for displaying items from the selected shop
items_frame = tk.Frame(root)
items_frame.pack(pady=10)

# Create labels to display the total cost
total_label = tk.Label(root, text="Total: ₩0", font=("Arial", 14))
total_label.pack(pady=10)

# Create buttons for sending the order and exiting
send_order_button = tk.Button(root, text="Send Order", font=("Arial", 14), command=send_order)
send_order_button.pack(pady=20)

exit_button = tk.Button(root, text="EXIT", font=("Arial", 14), command=disconnecting)
exit_button.pack(pady=10)

# Connect to the server
connect_to_server()

# Start the GUI event loop
root.mainloop()
