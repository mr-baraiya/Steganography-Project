import customtkinter as ctk

class CTkCustomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, dialog_type="info", allow_copy=False, action_cmd=None, action_text=""):
        super().__init__(parent)
        self.parent = parent
        self.title(title)

        # Dynamic Auto-Fit height calculation based on content length
        is_large = (dialog_type == "payload" or len(message) > 80)
        popup_w = 400
        
        if is_large:
            popup_h = 360
        else:
            line_count = message.count('\n') + max(1, len(message) // 38)
            popup_h = min(360, max(200, 125 + (line_count * 22)))

        self.geometry(f"{popup_w}x{popup_h}")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()

        # Center popup on parent window
        self.update_idletasks()
        try:
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            cx = px + max(0, (pw - popup_w) // 2)
            cy = py + max(0, (ph - popup_h) // 2)
            self.geometry(f"{popup_w}x{popup_h}+{cx}+{cy}")
        except Exception:
            pass

        # Select type styles
        if dialog_type == "error":
            badge_color = "#DC2626"
            icon = "❌"
            accent_hover = "#B91C1C"
        elif dialog_type == "success":
            badge_color = "#059669"
            icon = "✨"
            accent_hover = "#047857"
        elif dialog_type == "payload":
            badge_color = "#7C3AED"
            icon = "🔓"
            accent_hover = "#6D28D9"
        else:
            badge_color = "#4F46E5"
            icon = "ℹ️"
            accent_hover = "#4338CA"

        # Card Container
        self.card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0")
        self.card.pack(expand=True, fill="both", padx=16, pady=16)

        # Header Badge
        self.header_label = ctk.CTkLabel(
            self.card,
            text=f"{icon}  {title}",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=badge_color
        )
        self.header_label.pack(anchor="w", padx=20, pady=(18, 10))

        # Message Content Box / Label
        if is_large:
            self.msg_widget = ctk.CTkTextbox(
                self.card,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                fg_color="#F8FAFC",
                text_color="#0F172A",
                border_width=1,
                border_color="#CBD5E1",
                corner_radius=8,
                height=150
            )
            self.msg_widget.pack(expand=True, fill="both", padx=20, pady=(0, 16))
            self.msg_widget.insert("1.0", message)
            self.msg_widget.configure(state="disabled")
        else:
            self.msg_widget = ctk.CTkLabel(
                self.card,
                text=message,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="#334155",
                justify="left",
                wraplength=320
            )
            self.msg_widget.pack(anchor="w", padx=20, pady=(0, 16))

        # Action Buttons Container
        self.btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=(0, 16))

        if allow_copy:
            self.copy_btn = ctk.CTkButton(
                self.btn_frame,
                text="📋 Copy Message",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color="#F1F5F9",
                hover_color="#E2E8F0",
                text_color="#0F172A",
                height=36,
                corner_radius=8,
                command=lambda: self.copy_to_clipboard(message)
            )
            self.copy_btn.pack(side="left", padx=(0, 8))

        if action_cmd and action_text:
            self.action_extra_btn = ctk.CTkButton(
                self.btn_frame,
                text=action_text,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color="#F1F5F9",
                hover_color="#E2E8F0",
                text_color="#0F172A",
                height=36,
                corner_radius=8,
                command=action_cmd
            )
            self.action_extra_btn.pack(side="left")

        self.close_btn = ctk.CTkButton(
            self.btn_frame,
            text="Dismiss" if dialog_type == "error" else "Done",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=badge_color,
            hover_color=accent_hover,
            text_color="#FFFFFF",
            height=36,
            width=90,
            corner_radius=8,
            command=self.destroy
        )
        self.close_btn.pack(side="right")

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.copy_btn.configure(text="✅ Copied!", fg_color="#059669", text_color="#FFFFFF")
        self.after(1500, lambda: self.copy_btn.configure(text="📋 Copy Message", fg_color="#F1F5F9", text_color="#0F172A"))
