import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Server configuration
SERVER_IP = '172.20.10.2'  # Must align with server IP address
SERVER_PORT = 12153

# Variables to hold quantities and prices of items
rice_qty = 0
bread_qty = 0
rice_price = 2100
bread_price = 1500

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function to handle receiving messages from the server
def receive_messages(sock):
    while True:
        try:
<<<<<<< Updated upstream
            message = sock.recv(1024)
            if message:
                order = message.decode()
                if order == "Request has been accepted by another runner.":
                    messagebox.showinfo("Notification", order)
                elif "You accepted the order." in order:
                    messagebox.showinfo("Notification", order)
                else:
                    show_incoming_order(order)
=======
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
                    response = messagebox.askquestion("Order Status", f"{message}?")
                    if response == "yes":
                        client_socket.send("yes".encode())  # Notify server that the order is accepted
                    else:
                        client_socket.send("no".encode())

                elif "You have successfully finished a request. Runner fee is rewarded" in message:
                    exit_program()

                else:
                    # Show notification about the received order
                    show_incoming_order(message)

>>>>>>> Stashed changes
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

# Functions to handle button actions for rice and bread
def increase_rice():
    global rice_qty
    rice_qty += 1
    update_display()

def decrease_rice():
    global rice_qty
    if rice_qty > 0:
        rice_qty -= 1
    update_display()

def increase_bread():
    global bread_qty
    bread_qty += 1
    update_display()

def decrease_bread():
    global bread_qty
    if bread_qty > 0:
        bread_qty -= 1
    update_display()

# Function to update the displayed quantities and total cost
def update_display():
    rice_label.config(text=f"Rice (₩{rice_price}): {rice_qty}")
    bread_label.config(text=f"Bread (₩{bread_price}): {bread_qty}")
    total_cost = (rice_qty * rice_price) + (bread_qty * bread_price)
    total_label.config(text=f"Total: ₩{total_cost}")

# Function to send the order to the server
def send_order():
    total_cost = (rice_qty * rice_price) + (bread_qty * bread_price)
    if rice_qty == 0 and bread_qty == 0:
        messagebox.showwarning("Invalid Order", "Please select at least one item before sending the order.")
        return
    order = f"Rice: {rice_qty} x ₩{rice_price}, Bread: {bread_qty} x ₩{bread_price}, Total: ₩{total_cost}"
    client_socket.send(order.encode())
    print(f"Order sent to server: {order}")
    show_order_sent()

# Function to show the order sent confirmation pop-up
def show_order_sent():
    messagebox.showinfo("Order Sent", "Your order has been successfully sent.")

def disconnect():
    client_socket.send("disconnect".encode())
    print("disconnected")
    exit_program()

# Function to exit the program
def exit_program():
    root.quit()

# Create the main window (root)
root = tk.Tk()
root.title("Order System")

# Create frame for rice
rice_frame = tk.Frame(root)
rice_frame.pack(pady=10, fill="x")

rice_label = tk.Label(rice_frame, text="Rice (₩2100): 0", font=("Arial", 14))
rice_label.grid(row=0, column=0, padx=10)

rice_plus_button = tk.Button(rice_frame, text="+", font=("Arial", 12), command=increase_rice)
rice_plus_button.grid(row=0, column=1, padx=5)

rice_minus_button = tk.Button(rice_frame, text="-", font=("Arial", 12), command=decrease_rice)
rice_minus_button.grid(row=0, column=2, padx=5)

# Create frame for bread
bread_frame = tk.Frame(root)
bread_frame.pack(pady=10, fill="x")

bread_label = tk.Label(bread_frame, text="Bread (₩1500): 0", font=("Arial", 14))
bread_label.grid(row=0, column=0, padx=10)

bread_plus_button = tk.Button(bread_frame, text="+", font=("Arial", 12), command=increase_bread)
bread_plus_button.grid(row=0, column=1, padx=5)

bread_minus_button = tk.Button(bread_frame, text="-", font=("Arial", 12), command=decrease_bread)
bread_minus_button.grid(row=0, column=2, padx=5)

# Create labels to display the total cost
total_label = tk.Label(root, text="Total: ₩0", font=("Arial", 14))
total_label.pack(pady=10)

# Create buttons for sending the order and exiting
send_order_button = tk.Button(root, text="Send Order", font=("Arial", 14), command=send_order)
send_order_button.pack(pady=20)

exit_button = tk.Button(root, text="EXIT", font=("Arial", 14), command=disconnect)
exit_button.pack(pady=10)

# Connect to the server
connect_to_server()

# Start the GUI event loop
root.mainloop()
