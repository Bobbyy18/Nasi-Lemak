import tkinter as tk
from tkinter import messagebox
import socket
import json
import threading

RUNNER_FEE = 2000  # ₩2,000 per order

host = '10.121.131.23' # change referring to server's IP Address
port = 15123


locations = ["Aegineung Student Hall","Science Library","Informatics Hall", "Woodang Hall", "International Studies Hall"]

# List of shops and their respective items
shops = ["Ari Cafe Media Hall", "Mom's Touch", "Unistore", "EMart", "Pound Coffee", "GS25"]

shops_items = {
    "Ari Cafe Media Hall": {
        "Choco Latte": 3000,
        "Hibiscus Lemonade": 3800,
        "Green Tea Latte": 3000
    },
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
    },
    "Pound Coffee": {
        "Iced Americano": 2500,
        "Coffee Latte": 3000,
        "Coffee Cream Latte": 3800
    },
    "GS25": {
        "Seoul Milk": 1500,
        "Kinder Bueno": 1900,
        "Tuna Kimbap": 2000
    }
}

class KURunner:
    def __init__(self, root):
        self.root = root
        self.root.title("Kodae Store")
        self.cart = {}

        # Set background color of the window
        self.root.config(bg="maroon")

         # Socket initialization for both sending and receiving
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))  # Connect to the server

         # Start the listener thread to receive broadcast messages
        self.listener_thread = threading.Thread(target=self.receive_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()

        tk.Label(root, text="Select a Shop", font=("Arial", 16), bg="maroon", fg="white").pack()
        self.selected_shop = tk.StringVar(root)
        self.selected_shop.set(shops[0])  # Default selection
        shops_menu = tk.OptionMenu(root, self.selected_shop, *shops, command=self.update_menu)
        shops_menu.config(bg="yellow", fg="black")
        shops_menu.pack(pady=10)

        # Menu Label
        self.menu_label = tk.Label(root, text="Menu", font=("Arial", 16),bg="maroon", fg="white")
        self.menu_label.pack()

        # Menu items frame (initially empty)
        self.menu_frame = tk.Frame(root, bg="maroon")
        self.menu_frame.pack()

        tk.Label(root, text="Select your location", font=("Arial",16), bg="maroon", fg="white").pack(pady=10)
        self.selected_location = tk.StringVar(root)
        self.selected_location.set(locations[0])
        location_menu = tk.OptionMenu(root,self.selected_location, *locations)
        location_menu.config(bg="yellow",fg="black")
        location_menu.pack(pady=10)

        # Cart and Order Section
        tk.Label(root, text="Your cart", font=("Arial", 16), bg="maroon", fg="white").pack(pady=10)
        self.cart_display = tk.Text(root, height=10, width=30, state='disabled', bg="white", fg="black")
        self.cart_display.pack()

        # Place Order Button
        orderButton = tk.Button(root, text="Place Order", command=self.place_order, bg="yellow", fg="black")
        orderButton.pack(pady=10)

        # Done Button to close the connection
        done_button = tk.Button(root, text="Done", command=self.close_connection, bg="orange", fg="black")
        done_button.pack(pady=10)

        # Initialize with the first shop's menu
        self.update_menu(shops[0])

    def update_menu(self, shop):

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
        if shop not in self.cart:
            self.cart[shop] = {}  # Initialize the shop in the cart
        if item in self.cart[shop]:
            self.cart[shop][item] += 1  # Increment quantity if item exists
        else:
            self.cart[shop][item] = 1  # Add item with quantity 1
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_display.config(state="normal")
        self.cart_display.delete(1.0, tk.END)  # Clear the display

        total = 0
        for shop, items in self.cart.items():
            self.cart_display.insert(tk.END, f"{shop}:\n")  # Display shop name
            shop_items = shops_items[shop]
            for item, quantity in items.items():
                price = shop_items[item] * quantity
                total += price
                self.cart_display.insert(tk.END, f"  {item} x{quantity} - ₩ {price:,}\n")
            self.cart_display.insert(tk.END, "\n")
            
        total += RUNNER_FEE

        self.cart_display.insert(tk.END, f"Runner Fee: ₩{RUNNER_FEE:,}\n")    
        self.cart_display.insert(tk.END, f"Total: ₩{total:,}")
        self.cart_display.config(state="disabled")  # Make the display read-only

    def receive_messages(self):
        """Receive both broadcast messages and acknowledgments from the server."""
        while True:
            try:
                message_data = self.client_socket.recv(1024).decode()
                if message_data:
                    message = json.loads(message_data)
                    if message.get("type") == "broadcast":
                        print("Received broadcast message")
                        self.handle_broadcast(message["message"])
                    elif message.get("type") == "response":
                        print("Received order acknowledgement")
                        messagebox.showinfo("Order Status", message["message"])
                        
            except socket.error as e:
                print(f"Socket error: {e}")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break


    def handle_broadcast(self,message):
        if "Runner Found!" in message:
            print("Runner found. Broadcast stop")
            messagebox.showinfo("Order Update", "This order has already been assigned")
            return 
        
        response = messagebox.askquestion("Incoming order", "Do you want to take this request?")
        if response == "yes":
            messagebox.showinfo("Order Accepted",f"Order Accepted! Details:{message}")
            try:
                response_data={"type":"accept","details":message}
                self.client_socket.send(json.dumps(response_data).encode())
                print("Accepted order details sent to server.")
            except socket.error as e:
                print(f"Error sending acceptance to server:{e}")
        else:
            print("User declined the order.")

    def place_order(self): #updated place order
        if not self.cart:
            messagebox.showwarning("Warning", "Your cart is empty!")
            return

        # Prepare order data
        order_data = {
            "type":"order",
            "location":self.selected_location.get(),
            "shops": self.cart,  # Send the entire cart
            "runner_fee": RUNNER_FEE,  # Include the flat runner fee
            "total": sum(
                shops_items[shop][item] * quantity
                    for shop, items in self.cart.items()
            for item, quantity in items.items()
            )+ RUNNER_FEE,  # Add the flat runner fee to the total
        }

        # Send order to the server
        try:
            formatted_order_data = json.dumps(order_data, indent=4)
            self.client_socket.send(formatted_order_data.encode())
            print("Order sent:\n", formatted_order_data)

            self.cart.clear()  # Clear cart after successful order
            self.update_cart_display()
        except socket.error:
            messagebox.showerror("Connection Error", "Could not connect to server.")

    def close_connection(self):
        try:
            # Send a message to the server indicating the client is disconnecting
            disconnect_message = {"type": "disconnect"}
            self.client_socket.send(json.dumps(disconnect_message).encode())
            print("Disconnect message sent to the server.")
    
        except socket.error as e:
            print(f"Error sending disconnect message: {e}")

        finally:
            # Exit app
            print("Connection closed.")
            self.root.destroy()


# Run the app
root = tk.Tk()
app = KURunner(root)
root.mainloop()
