import os
import sys
import datetime
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

from steganography import encode_lsb, decode_lsb, calculate_max_capacity, validate_inputs
from ui.dialogs import CTkCustomDialog

ctk.set_appearance_mode("Dark")
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

        self.title("CELATUS - Hide. Secure. Reveal.")
        
        # Set Window Icon
        try:
            ico_path = get_resource_path(os.path.join("assets", "icon.ico"))
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception:
            pass

        # Set full screen resolution
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        self.configure(fg_color="#0B0F17")  # Minimalist Deep Charcoal Background

        # Start in maximized mode on startup
        self.after(50, self.force_fullscreen)

        # Set minimum window size for flexible resizing
        self.minsize(550, 400)

        # Key bindings: F11 toggles borderless fullscreen, Escape returns to maximized window with titlebar
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.exit_borderless_fullscreen())

        self.image_path = ""
        self.show_password = False
        self.current_img_capacity = 0
        self._current_layout = None

        self.setup_ui()
        self.bind("<Configure>", self.on_window_resize)

    def force_fullscreen(self):
        try:
            self.state('zoomed')
        except Exception:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

    def toggle_fullscreen(self):
        is_fs = self.attributes('-fullscreen')
        if not is_fs:
            self.attributes('-fullscreen', True)
        else:
            self.attributes('-fullscreen', False)
            try:
                self.state('zoomed')
            except Exception:
                pass

    def exit_borderless_fullscreen(self):
        self.attributes('-fullscreen', False)
        try:
            self.state('zoomed')
        except Exception:
            pass

    def on_window_resize(self, event):
        if event.widget != self:
            return
        
        w = event.width
        if w < 850:
            if self._current_layout != "narrow":
                self._current_layout = "narrow"
                self.apply_narrow_layout()
        else:
            if self._current_layout != "wide":
                self._current_layout = "wide"
                self.apply_wide_layout()

        if self.image_path:
            self.after(30, self.update_image_preview)

    def update_image_preview(self):
        if not self.image_path or not os.path.isfile(self.image_path):
            return

        try:
            pil_img = Image.open(self.image_path)
            orig_w, orig_h = pil_img.size

            self.preview_box.update_idletasks()
            box_w = self.preview_box.winfo_width()
            box_h = self.preview_box.winfo_height()

            if box_w < 100: box_w = 600
            if box_h < 100: box_h = 360

            avail_w = max(50, box_w - 24)
            avail_h = max(50, box_h - 24)

            # Compute Best Fit scale (object-fit: contain)
            ratio = min(avail_w / orig_w, avail_h / orig_h)
            new_w = max(1, int(orig_w * ratio))
            new_h = max(1, int(orig_h * ratio))

            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
            self.preview_label.configure(image=ctk_img, text="")
            self.preview_label.image = ctk_img

        except Exception:
            pass

    def apply_wide_layout(self):
        self.content_grid.columnconfigure(0, weight=1, uniform="col")
        self.content_grid.columnconfigure(1, weight=1, uniform="col")
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=0)
        if hasattr(self, 'message_input'):
            self.message_input.configure(height=240)
        if hasattr(self, 'log_textbox'):
            self.log_textbox.configure(height=140)

    def apply_narrow_layout(self):
        self.content_grid.columnconfigure(0, weight=1, uniform="")
        self.content_grid.columnconfigure(1, weight=0, uniform="")
        self.left_card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 16))
        self.right_card.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        if hasattr(self, 'message_input'):
            self.message_input.configure(height=130)
        if hasattr(self, 'log_textbox'):
            self.log_textbox.configure(height=95)

    def setup_ui(self):
        # Main Workspace Container (clean, zero scrollbars)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=24, pady=16)

        # Header Bar
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_box.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.title_box, 
            text="CELATUS", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#F3F4F6"
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.title_box, 
            text="Hide. Secure. Reveal.", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#818CF8"
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Header Action Controls (Container for Segmented Switcher & Fullscreen Button)
        self.header_actions = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_actions.pack(side="right")

        # Mode Tab Switcher
        self.mode_var = ctk.StringVar(value="Encode")
        self.segmented_button = ctk.CTkSegmentedButton(
            self.header_actions,
            values=["Encode", "Decode"],
            command=self.on_mode_change,
            variable=self.mode_var,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            selected_color="#6366F1",
            selected_hover_color="#4F46E5",
            unselected_color="#151D2A",
            unselected_hover_color="#1F2937",
            height=36,
            width=180
        )
        self.segmented_button.pack(side="left", padx=(0, 12))

        # Fullscreen Icon Button
        self.fullscreen_btn = ctk.CTkButton(
            self.header_actions,
            text="⛶",
            width=36,
            height=36,
            fg_color="#151D2A",
            hover_color="#1F2937",
            text_color="#E5E7EB",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            command=self.toggle_fullscreen,
            corner_radius=8
        )
        self.fullscreen_btn.pack(side="left")

        # BOTTOM PANEL: Clean Minimal Console Output (Packed at bottom first to reserve fixed space)
        self.console_card = ctk.CTkFrame(self.main_container, fg_color="#151D2A", corner_radius=14, border_width=1, border_color="#263346")
        self.console_card.pack(side="bottom", fill="x")

        self.console_header = ctk.CTkFrame(self.console_card, fg_color="transparent")
        self.console_header.pack(fill="x", padx=24, pady=(12, 6))

        self.console_title = ctk.CTkLabel(
            self.console_header, 
            text="Activity Log", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#E5E7EB"
        )
        self.console_title.pack(side="left")

        self.clear_log_btn = ctk.CTkButton(
            self.console_header,
            text="Clear",
            width=60,
            height=24,
            fg_color="#1E293B",
            hover_color="#334155",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self.clear_log,
            corner_radius=6
        )
        self.clear_log_btn.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(
            self.console_card,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0D131F",
            text_color="#818CF8",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8,
            height=130
        )
        self.log_textbox.pack(fill="x", padx=24, pady=(0, 14))

        # Main Workspace Card (Center panel filling available space)
        self.content_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_grid.pack(side="top", expand=True, fill="both", pady=(0, 16))
        self.content_grid.columnconfigure(0, weight=1, uniform="col")
        self.content_grid.columnconfigure(1, weight=1, uniform="col")
        self.content_grid.rowconfigure(0, weight=1)

        # LEFT PANEL: Minimalist Image Select Box
        self.left_card = ctk.CTkFrame(self.content_grid, fg_color="#151D2A", corner_radius=14, border_width=1, border_color="#263346")
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.left_card_title = ctk.CTkLabel(
            self.left_card, 
            text="Source Image", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#E5E7EB"
        )
        self.left_card_title.pack(anchor="w", padx=24, pady=(20, 12))

        # Image Preview Zone (Fixed propagation so preview fits without pushing Activity Log down)
        self.preview_box = ctk.CTkFrame(self.left_card, fg_color="#0D131F", corner_radius=10, border_width=1, border_color="#1E293B")
        self.preview_box.pack(expand=True, fill="both", padx=24, pady=(0, 12))
        self.preview_box.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_box, 
            text="No Image Selected\n\nClick 'Choose Image' below to start",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#64748B"
        )
        self.preview_label.pack(expand=True, fill="both", padx=12, pady=12)

        # File Info Metadata
        self.info_label = ctk.CTkLabel(
            self.left_card, 
            text="No file loaded", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#9CA3AF"
        )
        self.info_label.pack(anchor="w", padx=24, pady=(0, 12))

        # Browse Action
        self.browse_btn = ctk.CTkButton(
            self.left_card,
            text="Choose Image...",
            command=self.browse_image,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#F3F4F6",
            height=40,
            corner_radius=8
        )
        self.browse_btn.pack(fill="x", padx=24, pady=(0, 20))

        # RIGHT PANEL: Payload & Password Security
        self.right_card = ctk.CTkFrame(self.content_grid, fg_color="#151D2A", corner_radius=14, border_width=1, border_color="#263346")
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self.right_card_title = ctk.CTkLabel(
            self.right_card, 
            text="Payload & Key", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#E5E7EB"
        )
        self.right_card_title.pack(anchor="w", padx=24, pady=(20, 12))

        # Secret Message Input Header
        self.msg_header_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")

        self.message_label = ctk.CTkLabel(
            self.msg_header_frame, 
            text="Secret Message", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#D1D5DB"
        )
        self.message_label.pack(side="left")

        self.char_count_label = ctk.CTkLabel(
            self.msg_header_frame, 
            text="0 chars", 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#6B7280"
        )
        self.char_count_label.pack(side="right")

        self.message_input = ctk.CTkTextbox(
            self.right_card,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#0D131F",
            text_color="#F9FAFB",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8,
            height=120
        )
        self.message_input.bind("<KeyRelease>", self.on_input_change)

        # Passcode Protection Header & Field
        self.pass_label = ctk.CTkLabel(
            self.right_card, 
            text="Passcode Key (min 4 chars)", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#D1D5DB"
        )

        self.pass_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")

        self.passcode_input = ctk.CTkEntry(
            self.pass_frame,
            placeholder_text="Enter passcode key...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            show="*",
            fg_color="#0D131F",
            text_color="#F9FAFB",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8,
            height=40
        )
        self.passcode_input.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.passcode_input.bind("<KeyRelease>", self.on_input_change)

        self.toggle_pass_btn = ctk.CTkButton(
            self.pass_frame,
            text="👁",
            width=40,
            height=40,
            fg_color="#1E293B",
            hover_color="#334155",
            corner_radius=8,
            command=self.toggle_password_visibility
        )
        self.toggle_pass_btn.pack(side="right")

        # Live Validation Status Badge
        self.validation_badge = ctk.CTkLabel(
            self.right_card,
            text="⚠️ Select an image file to begin",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#F59E0B"
        )

        # Action Button
        self.action_btn = ctk.CTkButton(
            self.right_card,
            text="Encode Payload",
            command=self.on_action_click,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#6366F1",
            hover_color="#4F46E5",
            height=44,
            corner_radius=8
        )

        self.repack_right_panel()

        self.log("Ready. Select an image file to begin.")

    def repack_right_panel(self):
        mode = self.mode_var.get()
        self.msg_header_frame.pack_forget()
        self.message_input.pack_forget()
        self.pass_label.pack_forget()
        self.pass_frame.pack_forget()
        self.validation_badge.pack_forget()
        self.action_btn.pack_forget()

        if mode == "Encode":
            self.msg_header_frame.pack(fill="x", padx=24, pady=(0, 6))
            self.message_input.pack(fill="x", padx=24, pady=(0, 16))

        self.pass_label.pack(anchor="w", padx=24, pady=(0, 6))
        self.pass_frame.pack(fill="x", padx=24, pady=(0, 10))
        self.validation_badge.pack(anchor="w", padx=24, pady=(0, 10))
        self.action_btn.pack(fill="x", padx=24, pady=(0, 20))

    def show_dialog(self, title, message, dialog_type="info", allow_copy=False, action_cmd=None, action_text=""):
        dialog = CTkCustomDialog(self, title, message, dialog_type, allow_copy, action_cmd, action_text)
        self.wait_window(dialog)

    def on_mode_change(self, value):
        if value == "Encode":
            self.action_btn.configure(
                text="Encode Payload",
                fg_color="#6366F1",
                hover_color="#4F46E5"
            )
            self.log("Mode set to ENCODE.")
        else:
            self.action_btn.configure(
                text="Decode Payload",
                fg_color="#8B5CF6",
                hover_color="#7C3AED"
            )
            self.log("Mode set to DECODE.")
        self.repack_right_panel()
        self.validate_inputs()

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.passcode_input.configure(show="")
            self.toggle_pass_btn.configure(fg_color="#6366F1", hover_color="#4F46E5")
        else:
            self.passcode_input.configure(show="*")
            self.toggle_pass_btn.configure(fg_color="#1E293B", hover_color="#334155")

    def on_input_change(self, event=None):
        self.update_char_count()
        self.validate_inputs()

    def update_char_count(self):
        text = self.message_input.get("1.0", "end-1c")
        byte_count = len(text.encode('utf-8'))
        if self.current_img_capacity > 0:
            self.char_count_label.configure(text=f"{byte_count:,} / {self.current_img_capacity:,} bytes")
        else:
            self.char_count_label.configure(text=f"{byte_count:,} bytes")

    def validate_inputs(self):
        mode = self.mode_var.get()
        message = self.message_input.get("1.0", "end-1c")
        password = self.passcode_input.get()

        is_valid, badge_text, badge_color, err_msg = validate_inputs(
            self.image_path, message, password, mode, self.current_img_capacity
        )
        self.validation_badge.configure(text=badge_text, text_color=badge_color)
        return is_valid, err_msg

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.webp")])
        if not file_path:
            return

        self.image_path = file_path
        filename = os.path.basename(file_path)

        try:
            pil_img = Image.open(file_path)
            width, height = pil_img.size
            self.current_img_capacity = calculate_max_capacity(file_path)

            self.after(20, self.update_image_preview)

            self.info_label.configure(text=f"File: {filename} ({width}x{height}) • Max: {self.current_img_capacity:,} bytes")
            self.update_char_count()
            self.validate_inputs()
            self.log(f"Loaded '{filename}' ({width}x{height}). Max capacity: {self.current_img_capacity:,} bytes.")

        except Exception as e:
            self.show_dialog("Error", f"Failed to open image: {e}", "error")
            self.log(f"ERROR: Could not load image: {e}", is_error=True)

    def log(self, text, is_error=False):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = "[ERR]" if is_error else "[OK]"
        log_entry = f"{timestamp} {prefix} {text}\n"
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def clear_log(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

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

        # Suggest default filename based on original source image
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

        self.log(f"SUCCESS: Encoded payload ({bytes_len:,} bytes) saved to '{res}'.")
        self.show_dialog(
            "Encoding Successful",
            f"Message payload encoded cleanly!\n\nSaved location:\n{res}",
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

        self.log(f"SUCCESS: Decrypted Message extracted cleanly: '{res}'")
        self.show_dialog("Decrypted Payload", res, "payload", allow_copy=True)
