import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Server configuration
SERVER_IP = '192.168.0.149'  # Must align with server IP address
SERVER_PORT = 12345

# Variables to hold quantities of rice and bread
rice_qty = 0
bread_qty = 0

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function to handle receiving messages from the server
def receive_messages(sock):
    while True:
        try:
            # Receive message from the server
            message = sock.recv(1024)
            if message:
                order = message.decode()

                if order == "Request has been accepted by another runner." :
                    messagebox.showinfo("Notification", order)

                elif "You accepted the order. " in order:
                    messagebox.showinfo("Notification", order)
                    
                else:
                    # Show notification about the received order
                    show_incoming_order(order)

        except:
            pass
            """print("Disconnected from server.")
            sock.close()
            break"""

# Function to show notification pop-up when a message is received
def show_incoming_order(order):
    # Display pop-up for incoming order
    response = messagebox.askquestion("Incoming Order", f"Incoming order: {order}\nDo you want to take this request?")
    if response == "yes":
        #print(f"Accepted order: {order}")
        client_socket.send("accept".encode())  # Notify server that the order is accepted
    else:
        print(f"Reject order.")
        client_socket.send("reject".encode())  # Notify server that the order is rejected

# Function to connect to the server and start receiving messages
def connect_to_server():
    client_socket.connect((SERVER_IP, SERVER_PORT))
    # Start a thread to continuously listen for messages
    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receiver_thread.daemon = True  # This makes the thread exit when the main program exits
    receiver_thread.start()
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

# Function to update the displayed quantities
def update_display():
    rice_label.config(text=f"Rice: {rice_qty}")
    bread_label.config(text=f"Bread: {bread_qty}")

# Function to send the order to the server
def send_order():
    order = f"Rice: {rice_qty}, Bread: {bread_qty}"
    if rice_qty == 0 and bread_qty == 0:
        messagebox.showwarning("Invalid Order", "Please select at least one item before sending the order.")
        return
    client_socket.send(order.encode())
    print(f"Order sent to server: {order}")
    show_order_sent()

# Function to show the order sent confirmation pop-up
def show_order_sent():
    messagebox.showinfo("Order Sent", "Your order has been successfully sent.")

# Function to exit the program
def exit_program():
    client_socket.close()
    root.quit()

# Create the main window (root)
root = tk.Tk()
root.title("Order System")

# Create labels for displaying the quantities of rice and bread
rice_label = tk.Label(root, text="Rice: 0", font=("Arial", 14))
rice_label.pack(pady=10)

bread_label = tk.Label(root, text="Bread: 0", font=("Arial", 14))
bread_label.pack(pady=10)

# Create buttons for increasing and decreasing rice quantity
rice_buttons_frame = tk.Frame(root)
rice_buttons_frame.pack(pady=10)

rice_plus_button = tk.Button(rice_buttons_frame, text="+", font=("Arial", 12), command=increase_rice)
rice_plus_button.grid(row=0, column=0, padx=10)

rice_minus_button = tk.Button(rice_buttons_frame, text="-", font=("Arial", 12), command=decrease_rice)
rice_minus_button.grid(row=0, column=1, padx=10)

# Create buttons for increasing and decreasing bread quantity
bread_buttons_frame = tk.Frame(root)
bread_buttons_frame.pack(pady=10)

bread_plus_button = tk.Button(bread_buttons_frame, text="+", font=("Arial", 12), command=increase_bread)
bread_plus_button.grid(row=0, column=0, padx=10)

bread_minus_button = tk.Button(bread_buttons_frame, text="-", font=("Arial", 12), command=decrease_bread)
bread_minus_button.grid(row=0, column=1, padx=10)

# Create buttons for sending the order and exiting
send_order_button = tk.Button(root, text="Send Order", font=("Arial", 14), command=send_order)
send_order_button.pack(pady=20)

exit_button = tk.Button(root, text="EXIT", font=("Arial", 14), command=exit_program)
exit_button.pack(pady=10)

# Connect to the server
connect_to_server()

# Start the GUI event loop
root.mainloop()
