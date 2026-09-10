import os

def validate_inputs(image_path: str, message: str, password: str, mode: str, max_capacity: int = 0) -> tuple[bool, str, str, str]:
    """
    Validates user input fields for encoding or decoding.
    Returns: (is_valid: bool, badge_text: str, badge_color: str, error_msg: str)
    """
    valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')

    # Image File Validation
    if not image_path or not os.path.isfile(image_path):
        return False, "⚠️ Select a valid image file first", "#F59E0B", "Please select a valid image file first."

    if not image_path.lower().endswith(valid_exts):
        return False, "❌ Unsupported file format", "#EF4444", "Unsupported file format. Please select a PNG, JPG, BMP or WEBP image."

    clean_password = password.strip()

    if mode == "Encode":
        clean_message = message.strip()
        if not clean_message:
            return False, "⚠️ Secret message cannot be empty", "#F59E0B", "Secret message payload cannot be empty."

        if not clean_password:
            return False, "⚠️ Passcode key is required", "#F59E0B", "Passcode key is required."

        if len(clean_password) < 4:
            return False, "⚠️ Passcode key must be at least 4 characters", "#F59E0B", "Passcode key must be at least 4 characters long."

        full_payload = (clean_password + "|" + clean_message + "###").encode('utf-8')
        payload_len = len(full_payload)

        if max_capacity > 0 and payload_len > max_capacity:
            return False, f"❌ Payload ({payload_len:,} B) exceeds max capacity ({max_capacity:,} B)", "#EF4444", f"Payload size ({payload_len:,} bytes) exceeds maximum capacity ({max_capacity:,} bytes)."

        return True, "🟢 Ready to encode payload", "#10B981", ""

    else:  # Decode Mode
        if not clean_password:
            return False, "⚠️ Passcode key is required", "#F59E0B", "Passcode key is required."

        if len(clean_password) < 4:
            return False, "⚠️ Passcode key must be at least 4 characters", "#F59E0B", "Passcode key must be at least 4 characters long."

        return True, "🟢 Ready to decode payload", "#10B981", ""
