import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def encode_message(image_path, message, password, output_path="encryptedImage.png"):
    img = cv2.imread(image_path)

    if img is None:
        messagebox.showerror("Error", "Image not found!")
        return

    height, width, _ = img.shape
    max_chars = (height * width * 3) // 8  # Store 1 char in 8 bits using 3 channels

    if len(message) + len(password) + 4 > max_chars:  # Extra 4 for "###|"
        messagebox.showerror("Error", "Message is too long!")
        return

    full_message = password + "|" + message + "###"  # Store password & message
    binary_message = ''.join(format(ord(c), '08b') for c in full_message)  # Convert to binary

    n, m, channel = 0, 0, 0
    for bit in binary_message:
        pixel_value = int(img[n, m, channel])  # Convert to int
        pixel_value = (pixel_value & 254) | int(bit)  # Ensure valid uint8 range (0-255)
        img[n, m, channel] = np.uint8(pixel_value)  # Convert back to uint8

        channel += 1
        if channel == 3:
            channel = 0
            m += 1
            if m == width:
                m = 0
                n += 1
        if n == height:
            break

    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])  # Use PNG to avoid compression
    update_output_area(f"Message encoded successfully in {output_path}", success=True)
    os.system(f"start {output_path}")  # Open image

def decode_message(image_path, passcode_entry):
    img = cv2.imread(image_path)

    if img is None:
        messagebox.showerror("Error", "Image not found!")
        return

    height, width, _ = img.shape
    binary_message = ""
    n, m, channel = 0, 0, 0

    while True:
        binary_message += str(img[n, m, channel] & 1)  # Read LSB
        channel += 1
        if channel == 3:
            channel = 0
            m += 1
            if m == width:
                m = 0
                n += 1
        if n == height:
            break

        if len(binary_message) % 8 == 0 and binary_message[-24:] == "001000110010001100100011":  # "###" in binary
            break

    extracted_text = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message) - 24, 8))

    if "|" not in extracted_text:
        messagebox.showerror("Error", "Message corrupted or no password found!")
        return

    stored_password, message = extracted_text.split("|", 1)

    pas = passcode_entry.get().strip()

    if stored_password.strip() != pas.strip():
        update_output_area("YOU ARE NOT AUTHORIZED", success=False)
        return

    update_output_area(f"Decrypted message: {message}", success=True)

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        image_entry.delete(0, tk.END)
        image_entry.insert(0, file_path)

def encode_button_clicked():
    image_path = image_entry.get()
    message = message_entry.get()
    password = password_entry.get()

    if not image_path or not message or not password:
        messagebox.showerror("Error", "Please fill all fields!")
        return

    encode_message(image_path, message, password)

def decode_button_clicked():
    image_path = image_entry.get()
    if not image_path:
        messagebox.showerror("Error", "Please select an image!")
        return

    passcode = password_entry.get()
    if not passcode:
        messagebox.showerror("Error", "Please enter a passcode!")
        return

    decode_message(image_path, password_entry)

def mode_choice():
    mode = mode_var.get()
    if mode == "Encode":
        message_entry.grid(row=1, column=1, padx=20, pady=10)  # Show message entry for encoding
        encode_button.grid(row=3, column=0, columnspan=3, pady=20)
        decode_button.grid_forget()  # Hide the decode button
    elif mode == "Decode":
        message_entry.grid_forget()  # Hide message entry for decoding
        encode_button.grid_forget()  # Hide encode button
        decode_button.grid(row=3, column=0, columnspan=3, pady=20)  # Show the decode button

def update_output_area(message, success=True):
    output_area.config(state=tk.NORMAL)  # Enable text area to edit
    if success:
        output_area.insert(tk.END, f"SUCCESS: {message}\n", 'success')
    else:
        output_area.insert(tk.END, f"ERROR: {message}\n", 'error')
    output_area.yview(tk.END)  # Scroll to the bottom
    output_area.config(state=tk.DISABLED)  # Disable editing

# Setup Tkinter GUI
root = tk.Tk()
root.title("Steganography Encoder/Decoder")

# Set window size and background color
root.geometry("500x500")
root.config(bg="#f5f5f5")

# Create input fields and buttons
font_style = ("Helvetica", 12)

tk.Label(root, text="Select Image:", bg="#f5f5f5", font=font_style).grid(row=0, column=0, padx=20, pady=10, sticky="w")
image_entry = tk.Entry(root, width=40, font=font_style)
image_entry.grid(row=0, column=1, padx=20, pady=10)
browse_button = tk.Button(root, text="Browse", command=browse_image, font=font_style, bg="#007BFF", fg="white", relief="flat")
browse_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Enter Secret Message:", bg="#f5f5f5", font=font_style).grid(row=1, column=0, padx=20, pady=10, sticky="w")
message_entry = tk.Entry(root, width=40, font=font_style)
message_entry.grid(row=1, column=1, padx=20, pady=10)

tk.Label(root, text="Enter Passcode:", bg="#f5f5f5", font=font_style).grid(row=2, column=0, padx=20, pady=10, sticky="w")
password_entry = tk.Entry(root, width=40, font=font_style, show="*")  # Hide the password
password_entry.grid(row=2, column=1, padx=20, pady=10)

# Mode selection (Encode/Decode)
mode_var = tk.StringVar(value="Encode")
encode_radio = tk.Radiobutton(root, text="Encode", variable=mode_var, value="Encode", font=font_style, bg="#f5f5f5", command=mode_choice)
encode_radio.grid(row=4, column=0, padx=20, pady=10)
decode_radio = tk.Radiobutton(root, text="Decode", variable=mode_var, value="Decode", font=font_style, bg="#f5f5f5", command=mode_choice)
decode_radio.grid(row=4, column=1, padx=20, pady=10)

# Encode and Decode Buttons
encode_button = tk.Button(root, text="Encode Message", command=encode_button_clicked, font=font_style, bg="#28a745", fg="white", relief="flat")
decode_button = tk.Button(root, text="Decode Message", command=decode_button_clicked, font=font_style, bg="#ffc107", fg="white", relief="flat")

# Initially show the encode button and hide the decode button
encode_button.grid(row=3, column=0, columnspan=3, pady=20)

# Output Area (for status messages)
output_area = tk.Text(root, height=8, width=50, font=("Courier", 10), bg="#f5f5f5", wrap=tk.WORD)
output_area.grid(row=5, column=0, columnspan=3, padx=20, pady=10)
output_area.config(state=tk.DISABLED)  # Make the text area read-only initially
output_area.tag_config('success', foreground="green")
output_area.tag_config('error', foreground="red")

# Run the Tkinter event loop
root.mainloop()
