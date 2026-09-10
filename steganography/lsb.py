import cv2
import numpy as np
import os

def calculate_max_capacity(image_path: str) -> int:
    """Calculates maximum secret message payload capacity in bytes for a given image."""
    if not image_path or not os.path.isfile(image_path):
        return 0

    img = cv2.imread(image_path)
    if img is None:
        return 0

    height, width, _ = img.shape
    return (height * width * 3) // 8

def encode_lsb(image_path: str, message: str, password: str, output_path: str = "encryptedImage.png") -> tuple[bool, str, int]:
    """
    Encodes secret message and passcode into image LSB pixels using UTF-8 byte stream.
    Returns: (success: bool, output_path_or_error: str, bytes_encoded: int)
    """
    if not os.path.isfile(image_path):
        return False, "Selected image file does not exist.", 0

    img = cv2.imread(image_path)
    if img is None:
        return False, "Could not read the selected image file.", 0

    height, width, _ = img.shape
    max_capacity = (height * width * 3) // 8

    full_payload_bytes = (password + "|" + message + "###").encode('utf-8')
    payload_len = len(full_payload_bytes)

    if payload_len > max_capacity:
        return False, f"Payload size ({payload_len:,} bytes) exceeds maximum capacity ({max_capacity:,} bytes).", 0

    binary_message = ''.join(format(b, '08b') for b in full_payload_bytes)

    n, m, channel = 0, 0, 0
    for bit in binary_message:
        pixel_value = int(img[n, m, channel])
        pixel_value = (pixel_value & 254) | int(bit)
        img[n, m, channel] = np.uint8(pixel_value)

        channel += 1
        if channel == 3:
            channel = 0
            m += 1
            if m == width:
                m = 0
                n += 1
        if n == height:
            break

    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    return True, output_path, payload_len

def decode_lsb(image_path: str, password: str) -> tuple[bool, str]:
    """
    Decodes LSB binary message from image, verifies passcode, and extracts message text.
    Returns: (success: bool, extracted_message_or_error: str)
    """
    if not os.path.isfile(image_path):
        return False, "Selected image file does not exist."

    img = cv2.imread(image_path)
    if img is None:
        return False, "Could not read the image file."

    height, width, _ = img.shape
    binary_message = ""
    n, m, channel = 0, 0, 0

    while True:
        binary_message += str(img[n, m, channel] & 1)
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

    try:
        bytes_list = bytearray(int(binary_message[i:i+8], 2) for i in range(0, len(binary_message) - 24, 8))
        extracted_text = bytes_list.decode('utf-8', errors='ignore')
    except Exception:
        return False, "Corrupted or non-steganographic image!"

    if "|" not in extracted_text:
        return False, "No valid steganography payload found in this image!"

    stored_password, message = extracted_text.split("|", 1)

    if stored_password.strip() != password.strip():
        return False, "Incorrect Passcode Key!"

    return True, message
