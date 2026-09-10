import os
import sys
import datetime
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

from steganography import encode_lsb, decode_lsb, calculate_max_capacity, validate_inputs
from ui.dialogs import CTkCustomDialog

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, relative_path)

class SteganographyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Steganography Encoder/Decoder")
        
        # Set Window Icon
        try:
            ico_path = get_resource_path(os.path.join("assets", "icon.ico"))
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception:
            pass

        # Set Window geometry & theme
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{min(1050, screen_w)}x{min(760, screen_h)}")
        self.configure(fg_color="#F4F6F9")

        # Start in maximized mode on startup
        self.after(50, self.force_fullscreen)

        # Minimum window size
        self.minsize(650, 480)

        # Key bindings
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.exit_borderless_fullscreen())

        self.image_path = ""
        self.show_password = False
        self.current_img_capacity = 0

        self.setup_ui()

    def force_fullscreen(self):
        try:
            self.state('zoomed')
        except Exception:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

    def toggle_fullscreen(self):
        is_fs = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not is_fs)

    def exit_borderless_fullscreen(self):
        self.attributes('-fullscreen', False)
        try:
            self.state('zoomed')
        except Exception:
            pass

    def setup_ui(self):
        # Outer Padding Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=30, pady=20)

        # Form Card Container
        self.form_card = ctk.CTkFrame(self.main_container, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
        self.form_card.pack(expand=True, fill="both", padx=0, pady=0)

        # Form Scrollable/Inner Frame
        self.inner_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.inner_frame.pack(expand=True, fill="both", padx=36, pady=24)

        # ----------------------------------------------------
        # ROW 1: Select Image
        # ----------------------------------------------------
        self.row1_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.row1_frame.pack(fill="x", pady=(0, 14))

        self.lbl_select_image = ctk.CTkLabel(
            self.row1_frame,
            text="Select Image:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#1E293B",
            width=160,
            anchor="w"
        )
        self.lbl_select_image.pack(side="left")

        self.path_entry = ctk.CTkEntry(
            self.row1_frame,
            placeholder_text="No image file selected...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#FFFFFF",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=6,
            height=38
        )
        self.path_entry.pack(side="left", expand=True, fill="x", padx=(0, 12))

        self.btn_browse = ctk.CTkButton(
            self.row1_frame,
            text="Browse",
            command=self.browse_image,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#007BFF",
            hover_color="#0056B3",
            text_color="#FFFFFF",
            width=95,
            height=38,
            corner_radius=6
        )
        self.btn_browse.pack(side="left")

        # ----------------------------------------------------
        # OPTIONAL ROW: Image Preview Box (Compact & Clean)
        # ----------------------------------------------------
        self.preview_frame = ctk.CTkFrame(self.inner_frame, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#E2E8F0", height=110)
        self.preview_frame.pack(fill="x", pady=(0, 14))
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="📷 Select an image file using 'Browse' button above",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748B"
        )
        self.preview_label.pack(expand=True, fill="both", padx=10, pady=6)

        # ----------------------------------------------------
        # ROW 2: Enter Secret Message
        # ----------------------------------------------------
        self.row2_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.row2_frame.pack(fill="x", pady=(0, 14))

        self.lbl_secret_msg = ctk.CTkLabel(
            self.row2_frame,
            text="Enter Secret Message:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#1E293B",
            width=160,
            anchor="w"
        )
        self.lbl_secret_msg.pack(side="left", anchor="n", pady=(6, 0))

        self.msg_input_frame = ctk.CTkFrame(self.row2_frame, fg_color="transparent")
        self.msg_input_frame.pack(side="left", expand=True, fill="x")

        self.message_input = ctk.CTkTextbox(
            self.msg_input_frame,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#FFFFFF",
            text_color="#1E293B",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=6,
            height=70
        )
        self.message_input.pack(fill="x")
        self.message_input.bind("<KeyRelease>", self.on_input_change)

        # ----------------------------------------------------
        # ROW 3: Enter Passcode
        # ----------------------------------------------------
        self.row3_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.row3_frame.pack(fill="x", pady=(0, 18))

        self.lbl_passcode = ctk.CTkLabel(
            self.row3_frame,
            text="Enter Passcode:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#1E293B",
            width=160,
            anchor="w"
        )
        self.lbl_passcode.pack(side="left")

        self.pass_input_frame = ctk.CTkFrame(self.row3_frame, fg_color="transparent")
        self.pass_input_frame.pack(side="left", expand=True, fill="x")

        self.passcode_input = ctk.CTkEntry(
            self.pass_input_frame,
            placeholder_text="••••",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            show="*",
            fg_color="#FFFFFF",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=6,
            height=38
        )
        self.passcode_input.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.passcode_input.bind("<KeyRelease>", self.on_input_change)

        self.toggle_pass_btn = ctk.CTkButton(
            self.pass_input_frame,
            text="👁",
            width=38,
            height=38,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=6,
            command=self.toggle_password_visibility
        )
        self.toggle_pass_btn.pack(side="right")

        # ----------------------------------------------------
        # ROW 4: Centered Action Button (Encode Message / Decode Message)
        # ----------------------------------------------------
        self.action_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, 16))

        self.action_btn = ctk.CTkButton(
            self.action_frame,
            text="Encode Message",
            command=self.on_action_click,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#28A745",
            hover_color="#218838",
            text_color="#FFFFFF",
            width=200,
            height=42,
            corner_radius=6
        )
        self.action_btn.pack(anchor="center")

        # ----------------------------------------------------
        # ROW 5: Side-by-side Radio Buttons: (•) Encode   ( ) Decode
        # ----------------------------------------------------
        self.radio_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.radio_frame.pack(fill="x", pady=(0, 16))

        self.mode_var = ctk.StringVar(value="Encode")

        self.radio_container = ctk.CTkFrame(self.radio_frame, fg_color="transparent")
        self.radio_container.pack(anchor="center")

        self.radio_encode = ctk.CTkRadioButton(
            self.radio_container,
            text="Encode",
            variable=self.mode_var,
            value="Encode",
            command=self.on_mode_change,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1E293B",
            fg_color="#28A745",
            hover_color="#218838"
        )
        self.radio_encode.pack(side="left", padx=24)

        self.radio_decode = ctk.CTkRadioButton(
            self.radio_container,
            text="Decode",
            variable=self.mode_var,
            value="Decode",
            command=self.on_mode_change,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1E293B",
            fg_color="#FFC107",
            hover_color="#E0A800"
        )
        self.radio_decode.pack(side="left", padx=24)

        # ----------------------------------------------------
        # ROW 6: Status / Log Output Box (Light container with green text)
        # ----------------------------------------------------
        self.log_container = ctk.CTkFrame(self.inner_frame, fg_color="#FAFAFA", corner_radius=8, border_width=1, border_color="#E0E0E0")
        self.log_container.pack(expand=True, fill="both", pady=(0, 0))

        self.log_textbox = ctk.CTkTextbox(
            self.log_container,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#FAFAFA",
            text_color="#28A745",
            border_width=0,
            corner_radius=6,
            height=120
        )
        self.log_textbox.pack(expand=True, fill="both", padx=16, pady=12)

        self.log("Ready. Select an image file using 'Browse' to begin.")

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "Encode":
            self.action_btn.configure(
                text="Encode Message",
                fg_color="#28A745",
                hover_color="#218838",
                text_color="#FFFFFF"
            )
            self.lbl_secret_msg.configure(text="Enter Secret Message:")
            self.message_input.configure(state="normal")
            self.log("Mode set to ENCODE.")
        else:
            self.action_btn.configure(
                text="Decode Message",
                fg_color="#FFC107",
                hover_color="#E0A800",
                text_color="#1E293B"
            )
            self.lbl_secret_msg.configure(text="Decrypted Output:")
            self.log("Mode set to DECODE.")
        self.validate_inputs()

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.passcode_input.configure(show="")
            self.toggle_pass_btn.configure(fg_color="#007BFF", hover_color="#0056B3", text_color="#FFFFFF")
        else:
            self.passcode_input.configure(show="*")
            self.toggle_pass_btn.configure(fg_color="#E2E8F0", hover_color="#CBD5E1", text_color="#1E293B")

    def on_input_change(self, event=None):
        self.validate_inputs()

    def validate_inputs(self):
        mode = self.mode_var.get()
        message = self.message_input.get("1.0", "end-1c")
        password = self.passcode_input.get()

        is_valid, badge_text, badge_color, err_msg = validate_inputs(
            self.image_path, message, password, mode, self.current_img_capacity
        )
        return is_valid, err_msg

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.webp")])
        if not file_path:
            return

        self.image_path = file_path
        filename = os.path.basename(file_path)
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, file_path)

        try:
            pil_img = Image.open(file_path)
            orig_w, orig_h = pil_img.size
            self.current_img_capacity = calculate_max_capacity(file_path)

            avail_w = 400
            avail_h = 95
            ratio = min(avail_w / orig_w, avail_h / orig_h)
            new_w = max(1, int(orig_w * ratio))
            new_h = max(1, int(orig_h * ratio))

            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
            self.preview_label.configure(image=ctk_img, text=f"  {filename} ({orig_w}x{orig_h}) • Max capacity: {self.current_img_capacity:,} bytes")
            self.preview_label.image = ctk_img

            self.validate_inputs()
            self.log(f"SUCCESS: Loaded image '{filename}' ({orig_w}x{orig_h}). Max capacity: {self.current_img_capacity:,} bytes.")

        except Exception as e:
            self.show_dialog("Error", f"Failed to open image: {e}", "error")
            self.log(f"ERROR: Could not load image: {e}", is_error=True)

    def log(self, text, is_error=False):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = "SUCCESS:" if not is_error else "ERROR:"
        log_entry = f"{prefix} {text}\n"
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def clear_log(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def show_dialog(self, title, message, dialog_type="info", allow_copy=False, action_cmd=None, action_text=""):
        dialog = CTkCustomDialog(self, title, message, dialog_type, allow_copy, action_cmd, action_text)
        self.wait_window(dialog)

    def on_action_click(self):
        is_valid, err_msg = self.validate_inputs()
        if not is_valid:
            self.show_dialog("Validation Error", err_msg, "error")
            self.log(f"Validation failed: {err_msg}", is_error=True)
            return

        mode = self.mode_var.get()
        if mode == "Encode":
            self.encode_message()
        else:
            self.decode_message()

    def encode_message(self):
        message = self.message_input.get("1.0", "end-1c").strip()
        password = self.passcode_input.get().strip()

        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        default_filename = f"{base_name}_encoded.png"

        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[("PNG Image (*.png)", "*.png"), ("All Files (*.*)", "*.*")],
            title="Save Encrypted Image As..."
        )

        if not output_path:
            self.log("Encoding canceled: No save location selected.")
            return

        success, res, bytes_len = encode_lsb(self.image_path, message, password, output_path)

        if not success:
            self.show_dialog("Error", res, "error")
            self.log(f"Encode failed: {res}", is_error=True)
            return

        out_name = os.path.basename(res)
        self.log(f"Message encoded successfully in {out_name}")
        self.show_dialog(
            "Encoding Successful",
            f"Message encoded successfully in {out_name}!\n\nSaved location:\n{res}",
            "success",
            action_cmd=lambda: os.system(f'start "" "{res}"'),
            action_text="🖼️ View Image"
        )

        try:
            os.system(f'start "" "{res}"')
        except Exception:
            pass

    def decode_message(self):
        password = self.passcode_input.get().strip()

        success, res = decode_lsb(self.image_path, password)

        if not success:
            self.log(f"AUTHORIZATION/DECODE ERROR: {res}", is_error=True)
            self.show_dialog("Decode Error", res, "error")
            return

        self.log(f"Decrypted message: {res}")
        self.lbl_secret_msg.configure(text="Decrypted Output:")
        self.message_input.configure(state="normal")
        self.message_input.delete("1.0", "end")
        self.message_input.insert("1.0", res)
        self.show_dialog("Decrypted Payload", res, "payload", allow_copy=True)
