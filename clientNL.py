import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# Server configuration
SERVER_IP = '172.30.1.56'  # Must align with server IP address
SERVER_PORT = 12153

# Variables to hold quantities and prices of items in cart
cart = []
runner_fee = 2000  # Runner fee for each order

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function to connect to the server
def connect_to_server():
    client_socket.connect((SERVER_IP, SERVER_PORT))
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    print("Connected to server.")
    
# Function to handle receiving messages from the server
def receive_messages(sock):
    while True:
        try:
            # Receive message from the server
            message = sock.recv(1024).decode()

            if message:
                if message == "Request has been accepted by another runner.":
                    print("Failed to accept request")
                    messagebox.showinfo("Notification", message)
                    

                elif "You accepted the order." in message:
                    print(f"Received message: {message}")
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

# Function to update the displayed total cost (including runner fee)
def update_total():
    total_cost = sum(item['price'] * item['quantity'] for item in cart)
    total_cost += runner_fee  # Add runner fee
    total_label.config(text=f"Total: ₩{total_cost}")
    
#Function to add to cart   
def add_to_cart(item, price):
    selected_shop = shop_dropdown.get()
    # Check if the item already exists in the cart
    for cart_item in cart:
        if cart_item['name'] == item and cart_item['shop'] == selected_shop:  # Check by item name
            cart_item['quantity'] += 1  # Increment quantity
            update_cart_display()  # Update the display
            return

    # If item is not found, add it as a new entry (as a dictionary)
    cart.append({'shop': selected_shop,'name': item, 'price': price, 'quantity': 1})
    update_cart_display()  # Update the display

# Function to remove an item from the cart
def remove_from_cart(item_name):
    global cart
    cart = [item for item in cart if item['name'] != item_name]
    update_total()

#Function to send order to server
def send_order():
    if not cart:
        messagebox.showwarning("Invalid Order", "Please select at least one item before sending the order.")
        return
    
    # Retrieve name and location inputs
    customer_name = name_entry.get().strip()
    selected_location = location_dropdown.get().strip()

    if not customer_name:
        messagebox.showwarning("Invalid Input", "Please enter your name.")
        return

    if selected_location == "Select a Location":
        messagebox.showwarning("Invalid Input", "Please select a valid location.")
        return

    # Build the order string
    order = f"ORDER from {customer_name} at {selected_location} -> "
    total_cost = 0  # Initialize total cost

    for cart_item in cart:
        shop_name = cart_item['shop']
        item_name = cart_item['name']
        item_price = cart_item['price']
        item_quantity = cart_item['quantity']
        item_total = item_price * item_quantity

        order += f"[{shop_name}]{item_name}: {item_quantity} x ₩{item_price}, "
        total_cost += item_total

    # Add runner fee
    total_cost += runner_fee
    order += f"Total: ₩{total_cost}"

    # Send order to the server
    client_socket.send(order.encode())
    print(f"Order sent to server: {order}")
    messagebox.showinfo("Order Sent", "Your order has been successfully sent.")

def disconnecting():
    client_socket.send("disconnect".encode())
    print("Sending disconnecting message")

# Function to exit the program
def exit_program():
    root.quit()

# Example shop data: available items with prices
shops = {
    "Mom's Touch": [('Fried Chicken', 9900), ('Yangnyeom Chicken', 10900), ('Soy Garlic Chicken', 10900)],
    "Ari Cafe Media Hall": [('Choco Latte', 3000), ('Hibiscus Lemonade', 3800), ('Green Tea Latte', 3200)],
    "Unistore": [('Pen', 3000), ('Book', 5000), ('Bottle', 5000)],
    "EMart": [('Ice Cream', 1500), ('Bread', 3000), ('Coffee', 3500)],
    "Pound Coffee": [('Iced Americano', 2500), ('Coffee Latte', 3000), ('Coffee Cream Latte', 3800)],
    "GS25": [('Seoul Milk', 1500), ('Kinder Bueno', 1900), ('Tuna Kimbap', 2000)],
}
# Function to update item buttons based on the selected shop
def update_item_buttons(shop_name):
    for widget in item_frame.winfo_children():
        widget.destroy()  # Clear previous items

    if shop_name in shops:
        for item, price in shops[shop_name]:
            item_button = tk.Button(item_frame, text=f"{item} - ₩{price}", font=("Arial", 12),
                                    command=lambda item=item, price=price, shop=shop_name: add_to_cart(item, price))
            item_button.pack(fill="x", pady=5)
            
# Function to handle dropdown selection change
def on_shop_select(event):
    shop_name = shop_dropdown.get()  # Get the selected shop
    update_item_buttons(shop_name)  # Update the available items based on selected shop

def update_cart_display():
    # Clear the current cart display
    cart_display.delete(1.0, tk.END)
    
    total_cost = 0  # Initialize total cost
    for cart_item in cart:
        # Calculate total cost for each item
        item_total = cart_item['price'] * cart_item['quantity']
        total_cost += item_total

        # Display item details in the cart
        cart_display.insert(tk.END, f"{cart_item['name']} x {cart_item['quantity']} - ₩{item_total}\n")

    # Add the runner fee
    runner_fee = 2000
    total_cost += runner_fee
    
    # Update the total label
    total_label.config(text=f"Total: ₩{total_cost}")

# Create the main window (root)
root = tk.Tk()
root.title("KU Runner")
root.config(bg="maroon")

# Name Entry
name_label = tk.Label(root, text="KU Runner", font=("Arial", 14), bg="maroon", fg="white")
name_label.pack(pady=5)

name_entry = tk.Entry(root, font=("Arial", 12))
name_entry.pack(pady=5)
name_entry.insert(0, "Enter your name")  # Add placeholder/default text

# Clear the default text when the user clicks the entry field
def clear_placeholder(event):
    if name_entry.get() == "Enter your name":
        name_entry.delete(0, tk.END)

# Bind the Entry widget to clear placeholder text on focus
name_entry.bind("<FocusIn>", clear_placeholder)

#location selections
locations = ["Aegineung Student Hall","Science Library","Informatics Hall", "Woodang Hall", "International Studies Hall"]

# Location Dropdown
location_label = tk.Label(root, bg="maroon", fg="white")
location_label.pack(pady=5)

location_dropdown = ttk.Combobox(root, values=locations, font=("Arial", 12))
location_dropdown.pack(pady=5)
location_dropdown.set("Select a Location")  # Default text

# Create Shop Selection Dropdown
shop_label = tk.Label(root, bg="maroon", fg="white")
shop_label.pack(pady=5)

shop_dropdown = ttk.Combobox(root, values=list(shops.keys()), font=("Arial", 12))
shop_dropdown.pack(pady=5)
shop_dropdown.bind("<<ComboboxSelected>>", on_shop_select)
shop_dropdown.set("Select Shop")  # Default text

# Frame to display shop items
item_frame = tk.Frame(root, bg="yellow")
item_frame.pack(pady=5, fill="x")

# Create labels to display the cart and total cost
total_label = tk.Label(root, text="Total: ₩0", font=("Arial", 14))
total_label.pack(pady=10)

# Cart display frame
cart_frame = tk.Frame(root, bg="white")
cart_frame.pack(pady=10, fill="x")

# Cart display in a Text widget to show items
cart_display = tk.Text(cart_frame, height=5, width=30, font=("Arial", 12), wrap="word")
cart_display.pack()

# Create buttons for sending the order and exiting
send_order_button = tk.Button(root, text="Send Order", font=("Arial", 14), command=send_order)
send_order_button.pack(pady=10)

exit_button = tk.Button(root, text="EXIT", font=("Arial", 14), command=disconnecting)
exit_button.pack(pady=5)

# Connect to the server
connect_to_server()

# Start the GUI event loop
root.mainloop()
