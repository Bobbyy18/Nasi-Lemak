import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# Server configuration
SERVER_IP = '192.168.219.104'  # Must align with server IP address
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
    
#Function to add to cart   
def add_to_cart(item, price):
    # Check if the item already exists in the cart
    for cart_item in cart:
        if cart_item['name'] == item:  # Check by item name
            cart_item['quantity'] += 1  # Increment quantity
            update_cart_display()  # Update the display
            return

    # If item is not found, add it as a new entry (as a dictionary)
    cart.append({'name': item, 'price': price, 'quantity': 1})
    update_cart_display()  # Update the display

# Function to remove an item from the cart
def remove_from_cart(item_name):
    global cart
    cart = [item for item in cart if item['name'] != item_name]
    update_total()
    
def send_order():
    if not cart:
        messagebox.showwarning("Invalid Order", "Please select at least one item before sending the order.")
        return
    
    order = "ORDER -> "
    total_cost = 0  # Initialize total cost

    # Iterate over the cart
    for cart_item in cart:
        # Extract item details
        item_name = cart_item['name']
        item_price = cart_item['price']
        item_quantity = cart_item['quantity']
        item_total = item_price * item_quantity  # Total for this item

        # Add to the order string
        order += f"{item_name}: {item_quantity} x ₩{item_price}, "
        
        # Add to the total cost
        total_cost += item_total

    # Add runner fee to total
    runner_fee = 2000
    total_cost += runner_fee

    # Add the total cost to the order string
    order += f"Total: ₩{total_cost}"

    # Send the order to the server
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
                                    command=lambda item=item, price=price: add_to_cart(item, price))
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

# Create Shop Selection Dropdown
shop_label = tk.Label(root, text="KU RUNNER", font=("Arial", 16), bg="maroon", fg="white")
shop_label.pack(pady=10)

shop_dropdown = ttk.Combobox(root, values=list(shops.keys()), font=("Arial", 12))
shop_dropdown.pack(pady=5)
shop_dropdown.bind("<<ComboboxSelected>>", on_shop_select)

# Frame to display shop items
item_frame = tk.Frame(root, bg="yellow")
item_frame.pack(pady=10, fill="x")

# Create labels to display the cart and total cost
total_label = tk.Label(root, text="Total: ₩0", font=("Arial", 14))
total_label.pack(pady=10)

# Cart display frame
cart_frame = tk.Frame(root, bg="white")
cart_frame.pack(pady=10, fill="x")

# Cart display in a Text widget to show items
cart_display = tk.Text(cart_frame, height=10, width=40, font=("Arial", 12), wrap="word")
cart_display.pack()

# Create buttons for sending the order and exiting
send_order_button = tk.Button(root, text="Send Order", font=("Arial", 14), command=send_order)
send_order_button.pack(pady=20)

exit_button = tk.Button(root, text="EXIT", font=("Arial", 14), command=disconnecting)
exit_button.pack(pady=10)

# Connect to the server
connect_to_server()

# Start the GUI event loop
root.mainloop()
