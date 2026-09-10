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
        self.geometry(f"{min(1150, screen_w)}x{min(780, screen_h)}")
        self.configure(fg_color="#F4F6F9")

        # Start in maximized mode on startup
        self.after(50, self.force_fullscreen)

        # Minimum window size for flexible resizing
        self.minsize(750, 520)

        # Key bindings
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.exit_borderless_fullscreen())
        self.bind("<Configure>", self.on_window_resize)

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

    def on_window_resize(self, event):
        if event.widget == self and self.image_path:
            self.after(50, self.update_image_preview)

    def setup_ui(self):
        # Outer Padding Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=24, pady=18)

        # Form Card Container
        self.form_card = ctk.CTkFrame(self.main_container, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
        self.form_card.pack(expand=True, fill="both", padx=0, pady=0)

        # ----------------------------------------------------
        # 2-COLUMN SIDE-BY-SIDE GRID LAYOUT
        # ----------------------------------------------------
        self.columns_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.columns_frame.pack(expand=True, fill="both", padx=20, pady=20)
        self.columns_frame.columnconfigure(0, weight=1, uniform="col")
        self.columns_frame.columnconfigure(1, weight=1, uniform="col")
        self.columns_frame.rowconfigure(0, weight=1)

        # ====================================================
        # LEFT COLUMN: Image Selection & Best-Fit Image Preview
        # ====================================================
        self.left_column = ctk.CTkFrame(self.columns_frame, fg_color="#FAFAFA", corner_radius=10, border_width=1, border_color="#E0E0E0")
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Select Image Input Row
        self.row_select = ctk.CTkFrame(self.left_column, fg_color="transparent")
        self.row_select.pack(fill="x", padx=16, pady=(16, 10))

        self.lbl_select_image = ctk.CTkLabel(
            self.row_select,
            text="Select Image:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1E293B"
        )
        self.lbl_select_image.pack(anchor="w", pady=(0, 6))

        self.path_select_frame = ctk.CTkFrame(self.row_select, fg_color="transparent")
        self.path_select_frame.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            self.path_select_frame,
            placeholder_text="No file selected...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#FFFFFF",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=6,
            height=36
        )
        self.path_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.btn_browse = ctk.CTkButton(
            self.path_select_frame,
            text="Browse",
            command=self.browse_image,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#007BFF",
            hover_color="#0056B3",
            text_color="#FFFFFF",
            width=85,
            height=36,
            corner_radius=6
        )
        self.btn_browse.pack(side="right")

        # Best-Fit Image Preview Container
        self.preview_box = ctk.CTkFrame(self.left_column, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E0E0E0")
        self.preview_box.pack(expand=True, fill="both", padx=16, pady=(0, 10))
        self.preview_box.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_box,
            text="📷 Image Preview\n\nClick 'Browse' to select an image",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#64748B"
        )
        self.preview_label.pack(expand=True, fill="both", padx=10, pady=10)

        # File Info Metadata
        self.info_label = ctk.CTkLabel(
            self.left_column,
            text="No file loaded",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#64748B"
        )
        self.info_label.pack(fill="x", padx=16, pady=(0, 14))


        # ====================================================
        # RIGHT COLUMN: Form Controls, Radio Switcher & Logs
        # ====================================================
        self.right_column = ctk.CTkFrame(self.columns_frame, fg_color="#FAFAFA", corner_radius=10, border_width=1, border_color="#E0E0E0")
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        # Enter Secret Message
        self.lbl_secret_msg = ctk.CTkLabel(
            self.right_column,
            text="Enter Secret Message:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1E293B"
        )
        self.lbl_secret_msg.pack(anchor="w", padx=16, pady=(16, 6))

        self.message_input = ctk.CTkTextbox(
            self.right_column,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#FFFFFF",
            text_color="#1E293B",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=6,
            height=90
        )
        self.message_input.pack(fill="x", padx=16, pady=(0, 12))
        self.message_input.bind("<KeyRelease>", self.on_input_change)

        # Enter Passcode
        self.lbl_passcode = ctk.CTkLabel(
            self.right_column,
            text="Enter Passcode:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1E293B"
        )
        self.lbl_passcode.pack(anchor="w", padx=16, pady=(0, 6))

        self.pass_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        self.pass_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.passcode_input = ctk.CTkEntry(
            self.pass_frame,
            placeholder_text="••••",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            show="*",
            fg_color="#FFFFFF",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=6,
            height=36
        )
        self.passcode_input.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.passcode_input.bind("<KeyRelease>", self.on_input_change)

        self.toggle_pass_btn = ctk.CTkButton(
            self.pass_frame,
            text="👁",
            width=36,
            height=36,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=6,
            command=self.toggle_password_visibility
        )
        self.toggle_pass_btn.pack(side="right")

        # Action Button (Encode Message / Decode Message)
        self.action_btn = ctk.CTkButton(
            self.right_column,
            text="Encode Message",
            command=self.on_action_click,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#28A745",
            hover_color="#218838",
            text_color="#FFFFFF",
            width=180,
            height=38,
            corner_radius=6
        )
        self.action_btn.pack(anchor="center", pady=(0, 10))

        # Side-by-Side Radio Buttons: (•) Encode   ( ) Decode
        self.mode_var = ctk.StringVar(value="Encode")

        self.radio_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        self.radio_frame.pack(anchor="center", pady=(0, 10))

        self.radio_encode = ctk.CTkRadioButton(
            self.radio_frame,
            text="Encode",
            variable=self.mode_var,
            value="Encode",
            command=self.on_mode_change,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#1E293B",
            fg_color="#28A745",
            hover_color="#218838"
        )
        self.radio_encode.pack(side="left", padx=16)

        self.radio_decode = ctk.CTkRadioButton(
            self.radio_frame,
            text="Decode",
            variable=self.mode_var,
            value="Decode",
            command=self.on_mode_change,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#1E293B",
            fg_color="#FFC107",
            hover_color="#E0A800"
        )
        self.radio_decode.pack(side="left", padx=16)

        # Output Log Box (Light container with green text)
        self.log_container = ctk.CTkFrame(self.right_column, fg_color="#FFFFFF", corner_radius=6, border_width=1, border_color="#E0E0E0")
        self.log_container.pack(expand=True, fill="both", padx=16, pady=(0, 14))

        self.log_textbox = ctk.CTkTextbox(
            self.log_container,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#FFFFFF",
            text_color="#28A745",
            border_width=0,
            height=110
        )
        self.log_textbox.pack(expand=True, fill="both", padx=10, pady=8)

        self.log("Ready. Select an image file using 'Browse' to begin.")

    def update_image_preview(self):
        if not self.image_path or not os.path.isfile(self.image_path):
            return

        try:
            pil_img = Image.open(self.image_path)
            orig_w, orig_h = pil_img.size

            self.preview_box.update_idletasks()
            box_w = self.preview_box.winfo_width()
            box_h = self.preview_box.winfo_height()

            if box_w < 50: box_w = 400
            if box_h < 50: box_h = 300

            avail_w = max(20, box_w - 24)
            avail_h = max(20, box_h - 24)

            # Best Fit aspect-ratio scaling (object-fit: contain)
            ratio = min(avail_w / orig_w, avail_h / orig_h)
            new_w = max(1, int(orig_w * ratio))
            new_h = max(1, int(orig_h * ratio))

            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
            self.preview_label.configure(image=ctk_img, text="")
            self.preview_label.image = ctk_img
        except Exception:
            pass

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

            self.after(20, self.update_image_preview)

            self.info_label.configure(text=f"{filename} ({orig_w}x{orig_h}) • Max capacity: {self.current_img_capacity:,} bytes")
            self.validate_inputs()
            self.log(f"Loaded '{filename}' ({orig_w}x{orig_h}). Max capacity: {self.current_img_capacity:,} bytes.")

        except Exception as e:
            self.show_dialog("Error", f"Failed to open image: {e}", "error")
            self.log(f"ERROR: Could not load image: {e}", is_error=True)

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
