import tkinter as tk
from tkinter import messagebox
import socket
import json
import threading

host = '127.0.0.1'
port = 15123

# List of shops and their respective items
shops = ["Mom's Touch", "Unistore", "EMart"]

shops_items = {
    "Mom's Touch": {
        "Fried Chicken": 9900,
        "Yangnyeom Chicken": 10900,
        "Soy Garlic Chicken": 10900
    },
    "Unistore": {
        "Pen": 3000,
        "Book": 5000,
        "Bottle": 5000
    },
    "EMart": {
        "Ice Cream": 1500,
        "Bread": 2000,
        "Coffee": 3500
    }
}

class CoupangEats:
    def __init__(self, root):
        self.root = root
        self.root.title("Kodae Store")
        self.cart = {}

        # Socket initialization for both sending and receiving
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))  # Connect to the server
        
        # Start the listener thread to receive broadcast messages
        self.listener_thread = threading.Thread(target=self.receive_messages)
        self.listener_thread.daemon = True  # Ensure it exits when the main program exits
        self.listener_thread.start()

        # Shop Selection
        tk.Label(root, text="Select a Shop", font=("Arial", 16)).pack()
        self.selected_shop = tk.StringVar(root)
        self.selected_shop.set(shops[0])  # Default selection
        shops_menu = tk.OptionMenu(root, self.selected_shop, *shops, command=self.update_menu)
        shops_menu.pack(pady=10)

        # Menu Label
        self.menu_label = tk.Label(root, text="Menu", font=("Arial", 16))
        self.menu_label.pack()

        # Menu items frame (initially empty)
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack()

        # Cart and Order Section
        tk.Label(root, text="Your cart", font=("Arial", 16)).pack(pady=10)
        self.cart_display = tk.Text(root, height=10, width=30, state='disabled')
        self.cart_display.pack()

        orderButton = tk.Button(root, text="Place Order", command=self.place_order)
        orderButton.pack(pady=10)

        # Initialize with the first shop's menu
        self.update_menu(shops[0])

    def update_menu(self, shop):
        self.cart.clear()  # Clear the cart when changing shops
        self.update_cart_display()  # Update the cart display

        # Clear previous menu items
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        # Display new menu items for the selected shop
        shop_items = shops_items[shop]
        for item, price in shop_items.items():
            self.add_menu(item, price)

    def add_menu(self, item, price):
        frame = tk.Frame(self.menu_frame)
        frame.pack()

        label = tk.Label(frame, text=f"{item}: ₩ {price:,}", width=20, anchor="w")
        label.pack(side="left")

        add_button = tk.Button(frame, text="Add", command=lambda: self.add_to_cart(item))
        add_button.pack(side="left")

    def add_to_cart(self, item):
        shop = self.selected_shop.get()
        if item in self.cart:
            self.cart[item] += 1
        else:
            self.cart[item] = 1
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_display.config(state="normal")
        self.cart_display.delete(1.0, tk.END)  # Clear the display

        total = 0
        shop_items = shops_items[self.selected_shop.get()]
        for item, quantity in self.cart.items():
            price = shop_items[item] * quantity
            total += price
            self.cart_display.insert(tk.END, f"{item} x{quantity} - ₩ {price:,}\n")
        
        self.cart_display.insert(tk.END, f"\nTotal: ₩{total:,}")
        self.cart_display.config(state="disabled")  # Make the display read-only

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Your cart is empty!")
            return

        # Get the selected shop and prepare order data
        shop = self.selected_shop.get()
        shop_items = shops_items[shop]
        order_data = {
            "shop": shop,
            "items": self.cart,
            "total": sum(shop_items[item] * quantity for item, quantity in self.cart.items())
        }

        # Send order to the server
        try:
            # Send order data as JSON
            self.client_socket.send(json.dumps(order_data).encode())

            # Receive response from server
            response = self.client_socket.recv(1024).decode()
            response_data = json.loads(response)  # Convert JSON string to dictionary

            messagebox.showinfo("Order Status", response_data["message"])
            self.cart.clear()  # Clear cart after successful order
            self.update_cart_display()
        except socket.error:
            messagebox.showerror("Connection Error", "Could not connect to server.")

    def receive_messages(self):
        """Receive messages (broadcasts) from the server."""
        while True:
            try:
                message_data = self.client_socket.recv(1024).decode()
                if message_data:
                    message = json.loads(message_data)
                    messagebox.showinfo("Server Message", message["message"])  # Display broadcast message
            except Exception as e:
                print("Error receiving message:", e)
                break

# Run the app
root = tk.Tk()
app = CoupangEats(root)
root.mainloop()
