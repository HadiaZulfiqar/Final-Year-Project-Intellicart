import cv2
import re
import time
from functools import partial
import sys
import os
from pathlib import Path
from PIL import Image, ImageTk
from pathlib import Path
import requests
import tkinter as tk
import numpy as np
from tkinter import messagebox
from tkinter import Tk, Canvas, PhotoImage, Label, Button, Entry
from tkinter import Tk, Canvas, Frame, Label, Button, Scrollbar,Toplevel
# from tkinter.ttk import Treeview, Style
from ttkbootstrap import Style
from ttkbootstrap import Style, Frame
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Treeview
from pymongo import MongoClient
from pyzbar.pyzbar import decode
from collections import defaultdict
import threading
import ttkbootstrap as ttk
import serial
import datetime

import os
import subprocess
SQUEEKBOARD_RUNNING = False



# MongoDB connection
connection_string = "mongodb+srv://FYP:intellicart@fyp.hou2s.mongodb.net/smart_cart_db?retryWrites=true&w=majority"
client = MongoClient(connection_string, tls=True, tlsInsecure=True)
db = client['smart_cart_db']
collection = db['products']
customer_accounts = db["cards"]
customer_bills = db['customer_bills']


# Initialize data structures
scanned_barcodes = set()
bill = defaultdict(lambda: {'Product Name': '', 'Quantity': 0, 'Price': 0.0})
total_amount = 0

# Prompt user for IP Webcam URL
# ipv4 = input("Enter the IP Webcam URL (e.g., http://192.168.0.101:8080/shot.jpg): ")
# ipv4 = "192.168.0.33"

# url = 'http://'+str(ipv4)+':8080/shot.jpg'
# print(f"Using camera URL: {url}")

# Serial Communication with ESP32
# ser = serial.Serial('COM4', 9600, timeout=1)  # Update with correct port


def resource_path(relative_path: str) -> Path:
    """ Get the absolute path to a resource, works for both development and PyInstaller. """
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent  # Corrected: Use __file__
    return base_path / Path(relative_path)


# Define asset paths dynamically
ASSETS_PATH1 = resource_path("assets/frame1")
ASSETS_PATH2 = resource_path("assets/frame2")
ASSETS_PATH3 = resource_path("assets/frame3")
ASSETS_PATH4 = resource_path("assets/frame4")
ASSETS_PATH5 = resource_path("assets/frame0_new")
ASSETS_PATH6 = resource_path("assets/frame1_new")
ASSETS_PATH7 = resource_path("assets/frame2_new")



# Functions to get specific asset files
def relative_to_assets1(path: str) -> Path:
    return ASSETS_PATH1 / Path(path)

def relative_to_assets2(path: str) -> Path:
    return ASSETS_PATH2 / Path(path)

def relative_to_assets3(path: str) -> Path:
    return ASSETS_PATH3 / Path(path)

def relative_to_assets4(path: str) -> Path:
    return ASSETS_PATH4 / Path(path)

def relative_to_assets5(path: str) -> Path:
    return ASSETS_PATH5 / Path(path)

def relative_to_assets6(path: str) -> Path:
    return ASSETS_PATH6 / Path(path)

def relative_to_assets7(path: str) -> Path:
    return ASSETS_PATH7 / Path(path)


# # SERIAL_PORT = "COM4"  # Adjust as needed
SERIAL_PORT ="/dev/ttyUSB0"
# # SERIAL_PORT = 'COM4'
BAUD_RATE = 9600

def fix_uid(uid):
    """Fix UID by removing spaces and second-last zero if necessary."""
    uid = uid.replace(" ", "")
    if len(uid) > 7 and uid[-2] == "0":
        uid = uid[:-2] + uid[-1]
    return uid

def remove_UID(uid):
    """Remove unwanted text from scanned UID."""
    uid = re.sub(r'\bUID\b|\bCard\b|[^0-9A-F ]', '', uid, flags=re.IGNORECASE)
    return uid.strip()

def read_rfid():
    """Scan RFID card and display UID."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print("hello")
        # messagebox.showinfo("RFID Scanner", "Waiting for RFID card...")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "Card UID:" in line:
                    f_uid = remove_UID(line)
                    r_uid = fix_uid(f_uid)
                    print("ruidd", r_uid)
                    ser.close()
                    fetch_user_details(r_uid)
                    # root.withdraw()  # Hide the scan screen instead of destroying
                    # open_card_options_window(r_uid)
                    break
    except Exception as e:
        # messagebox.showerror("Error", f"Serial Port Error: {e}")
        pass

def fetch_user_details(uid):
    global correct_pin, user_uid
    print("rfid uid:", uid)
    user = customer_accounts.find_one({"uid": uid})
    if user:
        name = user.get("customerName", "Unknown")
        user_id = user.get("customerId", "Unknown")
        pin = user.get("pin", None)  # Fetch the stored PIN
        correct_pin = pin  # Update the correct_pin with the new PIN
        user_uid = uid
        update_gui(name, user_id)
    else:
        correct_pin = None  # Reset correct_pin if no user is found
        user_uid = None  # Reset if no user found
        messagebox.showerror("Error", "RFID not registered")


        


def update_gui(name, user_id):
    global entry_1, entry_2
    global scanned_customer_name, scanned_customer_id
    if 'scanned_customer_name' not in globals() or 'scanned_customer_id' not in globals():
        print("Error: Entry fields not initialized yet.")
        return
    # Store values globally
    scanned_customer_name = name
    scanned_customer_id = user_id

    # Update frame03 entry field
    entry_1.delete(0, tk.END)
    entry_1.insert(0, name)

    entry_2.delete(0, tk.END)
    entry_2.insert(0, user_id)


def resize_image(image_path, max_width, max_height):
    image = Image.open(image_path)
    original_width, original_height = image.size
    
    # Calculate new dimensions maintaining aspect ratio
    ratio = min(max_width/original_width, max_height/original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return image.resize((new_width, new_height), Image.ANTIALIAS)



def start_frame():
    global scanned_customer_name, scanned_customer_id, final_bill, bill, total_amount, scanned_barcodes
    scanned_customer_name = ""
    scanned_customer_id = ""
    final_bill = {}
    bill = {}
    total_amount = 0
    scanned_barcodes = set()  # Reset the scanned barcodes
    window = Tk()
    # window.iconbitmap("C:\FYP\myProject\assets\trolley.ico")  # Set window icon

    window.geometry("1000x600")
    window.configure(bg = "#000000")

    def called_frame2():
        window.destroy()
        paymentmethod_frame()

    canvas = Canvas(
        window,
        bg = "#000000",
        height=600,
        width=1024,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    image_image_1 = PhotoImage(
        file= resource_path("assets/frame1/image_1.png"))
    image_1 = canvas.create_image(
        400.0,
        240.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file= resource_path("assets/frame1/image_2.png"))
    image_2 = canvas.create_image(
        490.0,
        310.0,
        image=image_image_2
    )

    button_image_1 = PhotoImage(
        file= resource_path("assets/frame1/button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: called_frame2(),
        relief="flat"
    )
    button_1.place(
        x=380.0,
        y=430.0,
        width=209.0,
        height=40.0
    )
    # window.resizable(False, False)
    window.mainloop()

def rfid_frame():
    """Create the RFID window for PIN entry."""
    global correct_pin, entry_3, user_uid
    print(user_uid)

    print("jafjV", correct_pin)

    window = Tk()
    window.geometry("1024x600")
    window.configure(bg="#000000")

    def verify_pin(entered_pin, user_uid, window):
        """Verify the entered PIN against the PIN stored in the database."""
        # Fetch the user's PIN from the customer_accounts collection
        print(user_uid)
        user = customer_accounts.find_one({"uid": user_uid})
        if user:
            print('KHVvVCl,v')
            stored_pin = user.get("pin", None)  # Assuming the PIN is stored in the "pin" field
            if stored_pin and entered_pin == stored_pin:
                window.destroy()  # Destroy the RFID window
                camera_frame(update_user=True)  # Call the camera frame
            else:
                show_message("Incorrect PIN", 2000)  # Show incorrect PIN message for 2 seconds
                entry_3.delete(0, 'end')  # Clear the entry field for a new PIN
        else:
            show_message("User not found", 2000)  # Show user not found message for 2 seconds
            entry_3.delete(0, 'end')  # Clear the entry field

    def append_to_entry(digit):
        """Append a digit to the PIN entry field."""
        current_text = entry_3.get()
        if len(current_text) < 4:  # Allow only 4 digits
            entry_3.delete(0, 'end')
            entry_3.insert(0, current_text + digit)
            # Automatically verify the PIN when 4 digits are entered
            if len(current_text) == 3:  # After the 4th digit is added
                verify_pin(current_text + digit, user_uid, window)
        else:
            show_message("PIN limit exceeded (4 digits)", 1500)  # Show limit exceeded message for 1.5 seconds

    def show_message(message, duration):
        """Show a popup message for a specified duration."""
        popup = Toplevel()
        popup.geometry("300x150")
        popup.title("Message")
        popup.resizable(False, False)
        popup.configure(bg="white")
        popup.grab_set()  # Make the popup modal

        label = Label(popup, text=message, fg="black", bg="white", font=("Arial", 12))
        label.pack(pady=20)

        ok_button = Button(
            popup,
            text="OK",
            bg="#0078D7",
            fg="white",
            font=("Arial", 10),
            command=popup.destroy,
            relief="flat",
            padx=10,
            pady=5
        )
        ok_button.pack(pady=10)

        popup.after(duration, popup.destroy)  # Close the popup after the specified duration

    canvas = Canvas(
        window,
        bg="#000000",
        height=600,
        width=1024,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    image_image_2 = PhotoImage(file=resource_path("assets/frame2/image_1.png"))
    image_2 = canvas.create_image(400.0, 240.0, image=image_image_2)

    image_image_3 = PhotoImage(file=resource_path("assets/frame2/image_2.png"))
    image_3 = canvas.create_image(450.0, 255.0, image=image_image_3)

    button_image_1 = PhotoImage(file=resource_path("assets/frame2/button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("1"),
        relief="flat"
    )
    button_1.place(
        x=140.0,
        y=214.0,
        width=60.0,
        height=43.0
    )

    button_image_2 = PhotoImage(file=resource_path("assets/frame2/button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("2"),
        relief="flat"
    )
    button_2.place(x=285.0, y=217.0, width=48.0, height=33.0)

    button_image_3 = PhotoImage(file=resource_path("assets/frame2/button_3.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("3"),
        relief="flat"
    )
    button_3.place(x=420.0, y=217.0, width=48.0, height=33.0)

    button_image_4 = PhotoImage(file=resource_path("assets/frame2/button_4.png"))
    button_4 = Button(
        image=button_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("4"),
        relief="flat"
    )
    button_4.place(x=145.0, y=286.0, width=48.0, height=33.0)

    button_image_5 = PhotoImage(file=resource_path("assets/frame2/button_5.png"))
    button_5 = Button(
        image=button_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("5"),
        relief="flat"
    )
    button_5.place(
        x=270.0,
        y=283.0,
        width=81.60406494140625,
        height=35.0
    )

    button_image_6 = PhotoImage(file=resource_path("assets/frame2/button_6.png"))
    button_6 = Button(
        image=button_image_6,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("6"),
        relief="flat"
    )
    button_6.place(
        x=400.0,
        y=286.0,
        width=80.0,
        height=44.0
    )

    button_image_7 = PhotoImage(file=resource_path("assets/frame2/button_7.png"))
    button_7 = Button(
        image=button_image_7,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("7"),
        relief="flat"
    )
    button_7.place(
        x=140.0,
        y=354.0,
        width=68.171142578125,
        height=42.0
    )

    button_image_8 = PhotoImage(file=resource_path("assets/frame2/button_8.png"))
    button_8 = Button(
        image=button_image_8,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("8"),
        relief="flat"
    )
    button_8.place(
        x=275.0,
        y=354.0,
        width=77.0,
        height=40.0
    )

    button_image_9 = PhotoImage(file=resource_path("assets/frame2/button_9.png")) 
    button_9 = Button(
        image=button_image_9,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("9"),
        relief="flat"
    )
    button_9.place(x=410.0, y=354.0, width=48.0, height=33.0)

    button_image_10 = PhotoImage(file=resource_path("assets/frame2/button_0.png"))
    button_10 = Button(
        image=button_image_10,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: append_to_entry("0"),
        relief="flat"
    )
    button_10.place(x=275.0, y=420.0, width=48.0, height=33.0)

    entry_3 = Entry(
        bd=0,
        bg="#DACFFD",
        fg="#000716",
        highlightthickness=0,
        show="*"
    )
    entry_3.place(x=150.0, y=150.0, width=210.0, height=28.0)

    window.mainloop()

def paymentmethod_frame():
    window = Tk()

    window.geometry("1024x600")
    window.configure(bg = "#000000")


    canvas = Canvas(
        window,
        bg = "#000000",
        height=600,
        width=1024,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    image_image_1 = PhotoImage(
        file=resource_path("assets/frame0_new/image_1.png"))
    image_1 = canvas.create_image(
        600.0,
        310.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=resource_path("assets/frame0_new/image_2.png"))
    image_2 = canvas.create_image(
        480.0,
        320.0,
        image=image_image_2
    )
    
    def call_rfidframe():
        window.destroy()
        rfid_frame()

    button_image_1 = PhotoImage(
        file=resource_path("assets/frame0_new/button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: call_rfidframe(),
        relief="flat"
    )
    button_1.place(
        x=500.5,
        y=448.0,
        width=309.0,
        height=45.0
    )

    def call_cameraframe():
        window.destroy()
            # Default: Set values to '---'
        # if not update_user:
        #     scanned_customer_name = "---"
        #     scanned_customer_id = "---"
        camera_frame(update_user=False)

    button_image_2 = PhotoImage(
        file=resource_path("assets/frame0_new/button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: call_cameraframe(),
        relief="flat"
    )
    button_2.place(
        x=480.0,
        y=348.5,
        width=360.0,
        height=40.0
    )

    button_image_3 = PhotoImage(
        file=resource_path("assets/frame0_new/button_3.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: call_cameraframe(),
        relief="flat"
    )
    button_3.place(
        x=520.0,
        y=240.5,
        width=209.0,
        height=45.0
    )
    window.resizable(False, False)
    window.mainloop()


# Global variables
bill = {}
final_bill = {}
total_amount = 0
scanned_barcodes = set()
scanned_customer_name = ""
scanned_customer_id = ""
# Declare image variables globally
# global dustbin_icon, button_image_1, image_image_1, image_image_2
# Add these global variables at the top with other globals
# cumulative_expected_weight = 0.0  # Sum of all expected weights
weight_tolerance_kg = 0.010  # ±10g tolerance
last_weight_check_time = 0
weight_check_interval = 4  # seconds between weight checks
weight_mismatch_count = 0  # Track consecutive mismatches
weight_check_active = False  # Flag to prevent multiple simultaneous checks
MAX_MISMATCHES = 2  # Allow up to 2 consecutive mismatches before warning
# Serial Setup (Load Cell)
ser = serial.Serial(
	port='/dev/ttyUSB1',
	baudrate=9600,
	bytesize=serial.SEVENBITS,
	parity=serial.PARITY_EVEN,
	stopbits=serial.STOPBITS_ONE,
	timeout=1
)
# Load images globally so they persist
# dustbin_icon = PhotoImage(file=resource_path("assets/frame4/dustbin.png"))
# button_image_1 = PhotoImage(file=resource_path("assets/frame4/button_1.png"))
# image_image_1 = PhotoImage(file=resource_path("assets/frame4/image_1.png"))
# image_image_2 = PhotoImage(file=resource_path("assets/frame4/image_2.png"))
def camera_frame(update_user=False):
    global entry_1, entry_2, scanned_customer_name, scanned_customer_id,final_bill,cumulative_expected_weight, weight_mismatch_count, weight_check_active # Sum of all expected weights
  # Ensure global access
    # global window  # Declare window as a global variable
    cumulative_expected_weight = 0.0  # Sum of all expected weights
    weight_mismatch_count = 0
    weight_check_active = False

    window_closed = threading.Event()

    # Dictionary to track dustbin buttons
    dustbin_buttons = {}
    final_bill = {}


    def start_camera():
        def video_stream():
            frame_count = 0
            FRAME_SKIP = 5

            try:
                video_label.place(x=40, y=30, width=320, height=255)
            except Exception as e:
                print("Video label not available:", e)
                return

            use_picamera = False
            picam2 = None

            try:
                from picamera2 import Picamera2
                picam2 = Picamera2()
                camera_config = picam2.create_preview_configuration(main={"size": (1280, 720)})
                picam2.configure(camera_config)
                picam2.start()
                time.sleep(2)
                picam2.set_controls({"AfMode": 2})
                use_picamera = True
                print("Using Pi Camera with autofocus")
            except Exception as e:
                print("Falling back to IP Webcam:", e)
                use_picamera = False

            while not window_closed.is_set():
                frame = None
                try:
                    if use_picamera:
                        try:
                            frame = picam2.capture_array()
                        except Exception as e:
                            print("Pi Camera capture error:", e)
                            break
                    else:
                        try:
                            img_resp = requests.get(url, timeout=1)
                            img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
                            frame = cv2.imdecode(img_arr, -1)
                        except:
                            pass

                    if frame is not None:
                        frame = cv2.flip(frame, 1)
                        frame = cv2.convertScaleAbs(frame, alpha=1, beta=50)

                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        resized = cv2.resize(frame, (268, 220))

                        try:
                            if video_label.winfo_exists():
                                img_tk = ImageTk.PhotoImage(image=Image.fromarray(resized))
                                video_label.config(image=img_tk)
                                video_label.image = img_tk
                                video_label.config(text="Camera is running...")
                        except Exception as e:
                            print("Widget already destroyed. Skipping frame update.", e)
                            break

                        frame_count += 1
                        if frame_count % FRAME_SKIP == 0:
                            barcodes = decode(gray)
                            for barcode in barcodes:
                                barcode_data = barcode.data.decode("utf-8")
                                if barcode_data not in scanned_barcodes:
                                    scanned_barcodes.add(barcode_data)
                                    process_barcode(barcode_data)

                except Exception as e:
                    print("Error in video stream:", e)
                    break

            # Cleanup
            if use_picamera and picam2:
                try:
                    picam2.stop()
                    picam2.close()
                    print("Pi Camera closed")
                except Exception as e:
                    print("Error closing camera:", e)

        camera_thread = threading.Thread(target=video_stream, daemon=True)
        camera_thread.start()



    def process_barcode(barcode_data):
        global total_amount, cumulative_expected_weight, weight_mismatch_count
        
        print("Processing barcode:", barcode_data)
        try:
            # Attempt to interpret the barcode as a number
            if barcode_data.isdigit():
                barcode_int = int(barcode_data)
                result = collection.find_one({"code": barcode_int})
            else:
                result = collection.find_one({"code": barcode_data})

            if result:
                product_name = result.get("Product Name", "Unknown Item")
                price = float(result.get("Price (PKR)", "0").replace('Rs', ''))
                current_quantity = result.get("Quantity", 0)
                weight_kg = float(result.get("Weight (in kg)", 0))  # Get product weight

                if current_quantity > 0:
                    # Update inventory and add product to the bill
                    collection.update_one({"code": result["code"]}, {"$inc": {"Quantity": -1}})
                    
                    # Check if the product is already in the bill
                    if barcode_data in bill:
                        # Increment the quantity if the product is already in the bill
                        bill[barcode_data]["Quantity"] += 1
                    else:
                        # Add the product to the bill if it's not already there
                        bill[barcode_data] = {
                            "Product Name": product_name, 
                            "Quantity": 1, 
                            "Price": price,
                            "Weight": weight_kg  # Store product weight
                        }
                    
                    # Update cumulative expected weight
                    cumulative_expected_weight += weight_kg
                    weight_mismatch_count = 0  # Reset on new item
                    print(f"📦 Added {product_name} ({weight_kg}kg) - Total expected: {cumulative_expected_weight:.3f}kg")
                    
                    total_amount += price
                    update_bill_list()
                    update_suggestions(result)
                    
                    # Schedule weight verification after a delay
                    periodic_weight_check()
                else:
                    messagebox.showerror("Stock Error", f"Insufficient stock for {product_name}")
            else:
                messagebox.showerror("Error", f"Product with barcode {barcode_data} not found.")

            # Remove the barcode from scanned_barcodes to allow re-scanning
            scanned_barcodes.discard(barcode_data)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def periodic_weight_check():
        global weight_check_active
        if not weight_check_active:
            verify_weight()
        # Schedule next check after interval (e.g., 2 seconds)
        window.after(int(weight_check_interval * 1000), periodic_weight_check)


    def verify_weight():
        global cumulative_expected_weight, weight_mismatch_count, weight_check_active
        
        if weight_check_active:
            return
            
        weight_check_active = True
        
        measured_weight = get_stable_weight()
        if measured_weight is None:
            print("⚠️ Failed to read weight")
            weight_check_active = False
            return
        
        lower_bound = cumulative_expected_weight - weight_tolerance_kg
        upper_bound = cumulative_expected_weight + weight_tolerance_kg
        
        # Check if weight is out of bounds
        if measured_weight > upper_bound:
            # Create warning window if it doesn't exist
            if not hasattr(window, 'warning_window') or not window.warning_window.winfo_exists():
                window.warning_window = Toplevel(window)
                window.warning_window.title("Extra Items Detected")
                
                # Remove window decorations and disable closing
                window.warning_window.overrideredirect(True)
                window.warning_window.protocol("WM_DELETE_WINDOW", lambda: None)
                
                # Match main window's size and position
                window.warning_window.geometry(f"{window.winfo_width()}x{window.winfo_height()}+{window.winfo_x()}+{window.winfo_y()}")
                
                # Configure window background (using tkinter method)
                window.warning_window.config(bg='white')
                
                # Create a canvas for the red separator line
                separator_canvas = Canvas(window.warning_window, height=4, bg='white', highlightthickness=0)
                separator_canvas.pack(fill=X, pady=20)
                separator_canvas.create_line(0, 2, window.winfo_width(), 2, fill='red', width=4)
                
                # Add warning message (centered)
                msg = Label(
                    window.warning_window,
                    text="⚠️ WEIGHT MISMATCH DETECTED ⚠️\n\n"
                        f"Expected: {cumulative_expected_weight:.3f} kg\n"
                        f"Actual: {measured_weight:.3f} kg\n"
                        f"Difference: +{measured_weight - cumulative_expected_weight:.3f} kg\n\n"
                        "PLEASE REMOVE EXTRA ITEMS FROM YOUR CART\n"
                        "THIS MESSAGE WILL DISAPPEAR AUTOMATICALLY\n"
                        "WHEN THE WEIGHT MATCHES",
                    font=("Arial", 20, "bold"),
                    justify=CENTER,
                    bg='white',
                    fg='red',
                    wraplength=window.winfo_width()-40
                )
                msg.place(relx=0.5, rely=0.5, anchor=CENTER)
                
                # Make sure this window stays on top
                window.warning_window.attributes('-topmost', True)
            
            # Schedule next check
            window.after(2000, verify_weight)
        else:
            # Weight is good - destroy warning if it exists
            if hasattr(window, 'warning_window') and window.warning_window.winfo_exists():
                window.warning_window.destroy()
            
        weight_check_active = False

    def process_weight_result(measured_weight):
        global cumulative_expected_weight, weight_mismatch_count
        
        lower_bound = cumulative_expected_weight - weight_tolerance_kg
        upper_bound = cumulative_expected_weight + weight_tolerance_kg
        
        if measured_weight > upper_bound:
            if not hasattr(window, 'warning_window') or not window.warning_window.winfo_exists():
                create_weight_warning_window(measured_weight)
            window.after(2000, verify_weight)
        else:
            if hasattr(window, 'warning_window') and window.warning_window.winfo_exists():
                window.warning_window.destroy()

    def create_weight_warning_window(measured_weight):
        window.warning_window = Toplevel(window)
        window.warning_window.title("Extra Items Detected")
        window.warning_window.overrideredirect(True)
        window.warning_window.protocol("WM_DELETE_WINDOW", lambda: None)
        window.warning_window.geometry(f"{window.winfo_width()}x{window.winfo_height()}+{window.winfo_x()}+{window.winfo_y()}")
        window.warning_window.config(bg='white')
        
        separator_canvas = Canvas(window.warning_window, height=4, bg='white', highlightthickness=0)
        separator_canvas.pack(fill=tk.X, pady=20)
        separator_canvas.create_line(0, 2, window.winfo_width(), 2, fill='red', width=4)
        
        msg = tk.Label(
            window.warning_window,
            text="⚠️ WEIGHT MISMATCH DETECTED ⚠️\n\n"
                f"Expected: {cumulative_expected_weight:.3f} kg\n"
                f"Actual: {measured_weight:.3f} kg\n"
                f"Difference: +{measured_weight - cumulative_expected_weight:.3f} kg\n\n"
                "PLEASE REMOVE EXTRA ITEMS FROM YOUR CART\n"
                "THIS MESSAGE WILL DISAPPEAR AUTOMATICALLY\n"
                "WHEN THE WEIGHT MATCHES",
            font=("Arial", 20, "bold"),
            justify=tk.CENTER,
            bg='white',
            fg='red',
            wraplength=window.winfo_width()-40
        )
        msg.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        window.warning_window.attributes('-topmost', True)

    # Global weight-related functions (put these near the top with other global variables)
    def get_stable_weight(samples=7, retry_limit=3):
        """Get median of multiple weight readings for better stability"""
        for _ in range(retry_limit):
            weights = []
            for _ in range(samples):
                try:
                    ser.reset_input_buffer()
                    ser.write(b'PRINT\r\n')
                    time.sleep(0.1)
                    
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('ascii').strip()
                        if line:
                            match = re.search(r'[-+]?\s*\d+\.?\d*', line)
                            if match:
                                numeric_str = match.group().replace(' ', '')
                                weight = float(numeric_str)
                                weights.append(weight)
                                
                    time.sleep(0.2)
                except (serial.SerialException, ValueError) as e:
                    print(f"Read error: {str(e)}")
                    continue
                    
            if weights:
                # Use median instead of average to filter outliers
                weights.sort()
                return weights[len(weights)//2]
            
            print("Retrying weight measurement...")
            time.sleep(2)
            
        return None


    # [Rest of the existing code remains the same...]
    def update_suggestions(product):
        # Fetch related products based on brand or category
        brand = product.get("Brand", "")
        category = product.get("Category", "")

        related_products = collection.find({"$or": [{"Brand": brand}, {"Category": category}], "code": {"$ne": product["code"]}})

        # Update the suggestion list
        suggestion_list.delete(*suggestion_list.get_children())
        for related in related_products:
            suggestion_name = related.get("Product Name", "Unknown")
            suggestion_price = float(related.get("Price (PKR)", "0").replace('Rs', ''))
            suggestion_list.insert("", "end", values=(suggestion_name, f"Rs{suggestion_price}"))


    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def call_checkout_frame():
        global final_bill, total_amount  # Declare window as a global variable
        
        # Debugging print to verify final_bill data
        print("FINAL", final_bill)

        # Destroy the current window
        window.destroy()

        # Call the checkout frame
        checkout_frame()

    def remove_item(barcode):
        global bill, total_amount, scanned_barcodes, cumulative_expected_weight

        def destroy_dustbin_button(bcode):
            dustbin_buttons[bcode].destroy()
            del dustbin_buttons[bcode]

        try:
            if barcode in bill:
                # Get the weight of the item being removed
                item_weight = bill[barcode]["Weight"]
                
                # Reduce the quantity by 1
                bill[barcode]["Quantity"] -= 1

                # Update the total amount and expected weight
                total_amount -= bill[barcode]["Price"]
                cumulative_expected_weight -= item_weight

                # If the quantity reaches 0, remove the product from the bill
                if bill[barcode]["Quantity"] == 0:
                    del bill[barcode]
                    scanned_barcodes.discard(barcode)
                    if barcode in dustbin_buttons:
                        # Schedule the button destruction on the main thread
                        window.after(0, destroy_dustbin_button, barcode)

                # Update the bill list on the main thread
                window.after(0, update_bill_list)
                print(f"Removed one quantity of item with barcode: {barcode}")

                # Immediately check weight after removal
                def check_weight_after_removal():
                    measured_weight = get_stable_weight()
                    if measured_weight is None:
                        print("⚠️ Failed to read weight after removal")
                        return
                    
                    # Check if actual weight is more than expected
                    if measured_weight > (cumulative_expected_weight + weight_tolerance_kg):
                        # Show warning message
                        if not hasattr(window, 'warning_window') or not window.warning_window.winfo_exists():
                            create_weight_warning_window(measured_weight)
                        window.after(2000, verify_weight)
                    else:
                        # Close any existing warning window if weight matches
                        if hasattr(window, 'warning_window') and window.warning_window.winfo_exists():
                            window.warning_window.destroy()

                # Run weight check in a separate thread to avoid blocking GUI
                threading.Thread(target=check_weight_after_removal, daemon=True).start()

        except Exception as e:
            print(f"Error in remove_item: {str(e)}")
            # Show error in GUI without blocking
            window.after(0, lambda: messagebox.showerror("Error", f"Failed to remove item: {str(e)}"))




                
    def update_bill_list():
        global final_bill, total_amount

        # Update the Treeview with the bill details
        bill_list.delete(*bill_list.get_children())

        # Clear existing buttons
        for button in dustbin_buttons.values():
            button.destroy()
        dustbin_buttons.clear()

        # Reset final_bill before updating
        final_bill = {}
        total_amount = 0

        for barcode, details in bill.items():
            amount = details['Quantity'] * details['Price']
            item_id = bill_list.insert(
                "", 
                "end", 
                values=(details['Product Name'], details['Quantity'], f"Rs{details['Price']}", f""), 
                tags=(barcode,)
            )
            # Store in final_bill
            final_bill[barcode] = {
                "Product Name": details["Product Name"],
                "Quantity": details["Quantity"],
                "Price": details["Price"],
                "Amount": amount
            }
            # Update total bill amount
            total_amount += amount  

        # Update total label
        total_label.config(text=f"Rs{total_amount}")

        # Add dustbin buttons
        add_dustbin_buttons()

    def add_dustbin_buttons():
        for child in bill_list.get_children():
            # Retrieve the barcode stored in the Treeview tags
            barcode = bill_list.item(child, "tags")[0]

            dustbin_button = Button(
                bill_list,
                image=dustbin_icon,
                command=partial(remove_item, barcode),
                borderwidth=0,
                highlightthickness=0,
                bg="#d9d8d8",
                relief="flat"
            )

            # Place the button next to the row
            dustbin_button.place(x=380, y=bill_list.bbox(child)[1] + 2)

            # Store the button in the dictionary
            dustbin_buttons[barcode] = dustbin_button

    def on_closing():
        global window_closed
        window_closed.set()

        window_closed = True
        window.destroy()

    window = tk.Tk()
    window.geometry("1024x600")
    window.configure(bg="#000000")

    # Set the protocol for window closing
    window.protocol("WM_DELETE_WINDOW", on_closing)

    canvas = Canvas(
        window,
        bg="#000000",
        height=600,
        width=1024,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Load images
    window.image_image_1 = PhotoImage(file=resource_path("assets/frame4/image_1.png"))
    image_1 = canvas.create_image(740.0, 450.0, image=window.image_image_1)

    window.image_image_2 = PhotoImage(file=resource_path("assets/frame4/image_2.png"))
    image_1 = canvas.create_image(475.0, 255.0, image=window.image_image_2)

    window.button_image_1 = PhotoImage(file=resource_path("assets/frame4/button_1.png"))
    button_1 = Button(
        image=window.button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: call_checkout_frame(),
        relief="flat"
    )
    button_1.place(x=785.0, y=507.0, width=155.0, height=40.0)

    dustbin_icon = PhotoImage(file=resource_path("assets/frame4/dustbin.png"))
    print("Dustbin icon loaded:", dustbin_icon)

    # Place the video label directly in the window
    video_label = Label(window, bg="white")
    video_label.place(x=100, y=30, width=290, height=130)

    # Bill Section with static headers
    style = Style(theme="cosmo")
    style.configure("Custom.Treeview.Heading", background="3d9d8d8", foreground="black", font=("Sitka", 10, "bold"))
    style.configure("Custom.Treeview", background="#d9d8d8", foreground="black", rowheight=25, font=("Sitka", 10))

    bill_frame = Frame(window, style="BillFrame.TFrame", padding=0)
    bill_frame.place(x=440, y=30, width=480, height=260)

    # Add static headers
    header_frame = Frame(bill_frame)
    header_frame.pack(side=TOP, fill=X)

    # Create a scrollable Treeview below headers
    tree_frame = Frame(bill_frame)
    tree_frame.pack(side=TOP, fill=BOTH, expand=True)

    columns = ("Product", "Quantity", "Amount", "Remove")
    bill_list = Treeview(tree_frame, columns=columns, show="headings", style="Custom.Treeview")
    for i, col in enumerate(columns):
        bill_list.heading(col, text=col)
        bill_list.column(col, anchor=CENTER, width=[100, 70, 90, 70][i])

    # Add vertical scrollbar
    scrollbar = Scrollbar(tree_frame, orient=VERTICAL, command=bill_list.yview)
    bill_list.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)
    bill_list.pack(side=LEFT, fill=BOTH, expand=True)

    # Create a new frame for suggested products
    suggestion_frame = Frame(window)
    suggestion_frame.place(x=440, y=360, width=480, height=110)

    # Create a Treeview for suggestions
    suggestion_columns = ("Product", "Price")
    suggestion_list = Treeview(suggestion_frame, columns=suggestion_columns, show="headings", style="Custom.Treeview")
    for col in suggestion_columns:
        suggestion_list.heading(col, text=col)
        suggestion_list.column(col, anchor=CENTER, width=150)

    # Add vertical scrollbar for suggestions
    suggestion_scrollbar = Scrollbar(suggestion_frame, orient=VERTICAL, command=suggestion_list.yview)
    suggestion_list.configure(yscrollcommand=suggestion_scrollbar.set)
    suggestion_scrollbar.pack(side=RIGHT, fill=Y)
    suggestion_list.pack(side=LEFT, fill=BOTH, expand=True)

    if not update_user:
        scanned_customer_name = "---"
        scanned_customer_id = "---"

    # Customer Name Entry
    entry_1 = Entry(
        bd=0,
        bg="#DACFFD",
        fg="#000716",
        highlightthickness=0
    )
    entry_1.place(x=180, y=350, width=100.0, height=26.0)
    entry_1.config(bg="#d9d8d8")

    # Customer ID Entry
    entry_2 = Entry(
        bd=0,
        bg="#DACFFD",
        fg="#000716",
        highlightthickness=0
    )
    entry_2.place(x=180, y=395, width=100.0, height=26.0)
    entry_2.config(bg="#d9d8d8")

    # Populate entries with saved customer details
    entry_1.insert(0, scanned_customer_name)
    entry_2.insert(0, scanned_customer_id)

    total_label = Label(
        bd=0,
        bg="#DACFFD",
        fg="#000716",
        highlightthickness=0
    )
    total_label.place(x=180, y=440, anchor="nw")
    total_label.config(bg="#d9d8d8")

    # Start camera
    start_camera()

    # Ensure video_label and total_label do not move when scrolling
    canvas.create_window((200, 68), window=video_label, anchor="nw")
    # print(f"Existing widgets: {window.winfo_children()}")

    def suppress_error():
        try:
            window.mainloop()
        except Exception as e:
            print(f"Suppressed error: {e}")

    suppress_error()


def checkout_frame():
    global total_amount, scanned_customer_id, final_bill

    window = tk.Tk()
    window.geometry("1024x600")
    window.configure(bg="#000000")

    canvas = tk.Canvas(
        window,
        bg="#000000",
        height=600,
        width=1024,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    # Debug: Print the resolved image path
    image_path = resource_path("assets/frame1_new/image_1.png")
    print(f"Loading image from: {image_path}")


    # Load the background image and store it as an attribute of the window
    try:
        window.image_image_1 = tk.PhotoImage(file=image_path)
        print("Image loaded successfully.")
    except Exception as e:
        print(f"Error loading image: {e}")
        messagebox.showerror("Error", f"Failed to load image: {e}")
        return

    # Create the image on the canvas
    image_1 = canvas.create_image(400.0, 240.0, image=window.image_image_1)


    image_image_2 = PhotoImage(
        file= resource_path("assets/frame1_new/image_2.png"))
    image_2 = canvas.create_image(
        490.0,
        310.0,
        image=image_image_2
    )

    # Total Bill Label
    total_bill_label = tk.Label(
        window,
        text=f"Rs{total_amount}",
        bg="#DACFFD",
        fg="#000716",
        font=("Arial", 16)
    )
    total_bill_label.place(x=380, y=320)
    total_bill_label.config(bg="#dacffc")

    def complete_shopping():
        global total_amount, scanned_customer_id, final_bill, user_uid  # Add user_uid to globals
        
        try:
            # Debugging
            print("Customer ID:", scanned_customer_id)
            print("Total Amount:", total_amount)
            print("User UID:", user_uid if 'user_uid' in globals() else "Not available")

            # Save the bill
            bill_data = {
                "customer_id": scanned_customer_id,
                "customer_name": scanned_customer_name,
                "total_amount": total_amount,
                "items": list(final_bill.values()),
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            customer_bills.insert_one(bill_data)

            # 💳 Deduct only if RFID login used (i.e., user_uid exists and was valid)
            if 'user_uid' in globals() and user_uid:
                print("RFID used, checking account for:", user_uid)
                customer_account = customer_accounts.find_one({"uid": user_uid})
                if customer_account:
                    new_balance = customer_account.get("balance", 0) - total_amount
                    if new_balance >= 0:
                        # Initialize Transaction History array if it doesn't exist
                        if "Transaction History" not in customer_account:
                            customer_accounts.update_one(
                                {"uid": user_uid},
                                {"$set": {"Transaction History": []}}
                            )
                        
                        transaction = {
                            "Transaction Type": "Purchase",
                            "Amount": total_amount,
                            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Update balance and add transaction
                        result = customer_accounts.update_one(
                            {"uid": user_uid},
                            {
                                "$set": {"balance": new_balance},
                                "$push": {"Transaction History": transaction}
                            }
                        )
                        
                        print(f"Update result: {result.modified_count} documents modified")
                        
                        if result.modified_count == 0:
                            print("Warning: No documents were modified in the update")
                    else:
                        messagebox.showerror("Insufficient Balance", "Not enough balance.")
                        return
                else:
                    messagebox.showerror("Error", f"No RFID account found for UID: {user_uid}")
            else:
                print("No RFID used — treating as cash transaction")

            window.destroy()
            thankyou_frame()
        except Exception as e:
            print(f"Error in complete_shopping: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    button_image_1 = PhotoImage(
        file=resource_path("assets/frame1_new/button_1.png"))
    complete_button = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: complete_shopping(),
        relief="flat"
    )
    complete_button.place(x=300, y=450, width=350, height=35)

    # Suppress Tkinter errors
    def suppress_error():
        try:
            window.mainloop()
        except Exception as e:
            print(f"Suppressed error: {e}")

    suppress_error()

def thankyou_frame():
    window = tk.Tk()
    window.geometry("1024x600")
    window.configure(bg="#000000")

    canvas = tk.Canvas(
        window,
        bg="#000000",
        height=600,
        width=1024,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    # Load the background image and store it as an attribute of the window
    window.image_image_1 = tk.PhotoImage(file=resource_path("assets/frame2_new/image_1.png"))
    image_1 = canvas.create_image(400.0, 240.0, image=window.image_image_1)

    window.image_image_2 = tk.PhotoImage(file=resource_path("assets/frame2_new/image_2.png"))
    image_2 = canvas.create_image(490.0, 310.0, image=window.image_image_2)


    # Return to Start Frame after 3 seconds
    window.after(2000, lambda: [window.destroy(), start_frame()])

    # Suppress Tkinter errors
    def suppress_error():
        try:
            window.mainloop()
        except Exception as e:
            print(f"Suppressed error: {e}")

    suppress_error()


# Start RFID reading in a separate thread
rfid_thread = threading.Thread(target=read_rfid, daemon=True)
rfid_thread.start()
start_frame()
# rfid_frame()
# checkout_frame()