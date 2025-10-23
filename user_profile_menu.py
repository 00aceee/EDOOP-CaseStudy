import tkinter as tk
from tkinter import messagebox
import random, string, smtplib
from email.mime.text import MIMEText
from database_handler import get_user_details, get_user_appointments
from config import *
from dotenv import load_dotenv
import os

load_dotenv()
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP")

class UserProfileMenu(tk.Frame):
    def __init__(self, parent, username, mode, toggle_theme_callback, logout_callback):
        super().__init__(parent.scrollable_frame, bg=CARD_COLOR if mode == "dark" else CARD_COLOR_LIGHT)
        self.parent = parent
        self.username = username
        self.toggle_theme_callback = toggle_theme_callback
        self.logout_callback = logout_callback
        self.mode = mode
        self.email_code = None

        # Panel position
        self.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne", width=320)

        self.user = get_user_details(self.username)
        if not self.user:
            messagebox.showerror("Error", "Could not fetch user details.")
            self.destroy()
            return

        self.build_ui()
        self.focus_set()
        self.bind_outside_click()

    def build_ui(self):
        fg = FG_COLOR_DARK if self.mode == "dark" else FG_COLOR_LIGHT
        bg = CARD_COLOR if self.mode == "dark" else CARD_COLOR_LIGHT

        # ===== Header =====
        header_frame = tk.Frame(self, bg=ACCENT_COLOR, height=55, relief="flat")
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="👤 User Profile", font=("Segoe UI", 15, "bold"), fg="white", bg=ACCENT_COLOR).pack(side='left', padx=15)

        close_btn = tk.Button(
            header_frame, text="✕", font=("Arial", 14, "bold"), fg="white", bg=ACCENT_COLOR,
            relief="flat", command=self.close_menu, cursor="hand2", activebackground="#c0392b"
        )
        close_btn.pack(side='right', padx=10)

        # ===== User Info =====
        user = self.user
        info_frame = tk.Frame(self, bg=bg, padx=20, pady=10)
        info_frame.pack(fill='x')

        tk.Label(info_frame, text=f"Welcome, {user['fullname']}", font=("Segoe UI", 13, "bold"), fg=ACCENT_COLOR, bg=bg).pack(anchor="w", pady=(0, 5))
        tk.Label(info_frame, text=f"Username: {user['username']}", font=("Segoe UI", 11), fg=fg, bg=bg).pack(anchor="w")
        tk.Label(info_frame, text=f"Email: {user['email']}", font=("Segoe UI", 11), fg=fg, bg=bg).pack(anchor="w")

        tk.Frame(self, height=2, bg="#D0D0D0" if self.mode == "light" else "#333333").pack(fill='x', padx=15, pady=10)

        # ===== Appointments =====
        tk.Label(self, text="📅 Upcoming Appointments", font=("Segoe UI", 12, "bold"), fg=fg, bg=bg).pack(anchor='w', padx=20)

        appt_list_frame = tk.Frame(self, bg=BG_COLOR if self.mode == 'dark' else "#F8F9FA", padx=10, pady=10, relief="flat", bd=1)
        appt_list_frame.pack(fill='x', padx=20, pady=8)

        appointments = get_user_appointments(user['id'])
        if appointments:
            for appt in appointments:
                appt_text = f"• {appt['service']} — {appt['appointment_date']} at {appt['time']} ({appt['status']})"
                tk.Label(appt_list_frame, text=appt_text, font=("Segoe UI", 10), fg=fg, bg=appt_list_frame['bg'], wraplength=260, justify="left").pack(anchor="w", pady=2)
        else:
            tk.Label(appt_list_frame, text="No upcoming appointments.", font=("Segoe UI", 10, "italic"), fg=fg, bg=appt_list_frame['bg']).pack()

        # ===== Change Password Button =====
        tk.Button(
            self, text="🔐 Change Password", command=self.show_password_fields,
            fg="white", bg="#0078D7", relief="flat", cursor="hand2",
            activebackground="#005bb5", font=("Segoe UI", 11, "bold")
        ).pack(pady=(20, 8), padx=20, fill='x')

        # ===== Password Frame =====
        self.password_frame = tk.Frame(self, bg=bg, padx=20, pady=10, relief="groove", bd=1)
        self.password_frame.pack(pady=5, padx=15, fill='x')
        self.password_frame.pack_forget()

        def create_field(row, label_text, show=None, readonly=False):
            tk.Label(self.password_frame, text=label_text, bg=bg, fg=fg, font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=3)
            entry = tk.Entry(self.password_frame, show=show, width=30, relief='flat', bd=2, fg=fg, bg="#F5F5F5" if self.mode == 'light' else "#444")
            entry.grid(row=row, column=1, sticky="ew", pady=3)
            if readonly:
                entry.insert(0, user['email'])
                entry.config(state='readonly')
            return entry

        self.current_pass = create_field(0, "Current Password:", show="*")
        self.new_pass = create_field(1, "New Password:", show="*")
        self.confirm_pass = create_field(2, "Confirm Password:", show="*")
        self.email_entry = create_field(3, "Email (Verification):", readonly=True)

        # Buttons inside password frame
        tk.Button(self.password_frame, text="📧 Send Code", bg="#28A745", fg="white",
                  relief="flat", activebackground="#1e7e34", cursor="hand2",
                  command=self.send_confirmation_code).grid(row=4, column=0, columnspan=2, pady=5, sticky='ew')

        tk.Label(self.password_frame, text="Enter Code:", bg=bg, fg=fg, font=("Segoe UI", 10, "bold")).grid(row=5, column=0, sticky="w", pady=3)
        self.code_entry = tk.Entry(self.password_frame, width=15, relief='flat', bd=2, fg=fg, bg="#F5F5F5" if self.mode == 'light' else "#444")
        self.code_entry.grid(row=5, column=1, sticky="ew", pady=3)

        tk.Button(self.password_frame, text="✅ Confirm Change", bg="#FF9800", fg="white",
                  relief="flat", activebackground="#cc7a00", cursor="hand2",
                  command=self.change_password).grid(row=6, column=0, columnspan=2, pady=5, sticky='ew')

        theme_text = "🌙 Dark Mode" if self.mode == "light" else "☀️ Light Mode"
        self.theme_button = tk.Button(
            self,
            text=theme_text,
            command=self.on_toggle_theme,
            fg="white" if self.mode == "dark" else "#222222",
            bg="#256F72" if self.mode == "light" else "#256F72",
            activebackground="#55D2D6" if self.mode == "light" else "#55D2D6",
            font=("Segoe UI", 11, "bold"),
            height=2,
            relief="flat",
            cursor="hand2"
        )
        self.theme_button.pack(pady=(25, 10), padx=20, fill='x')

        tk.Button(
            self, text="🚪 Logout", command=self.logout_callback,
            fg="white", bg="#DC3545", relief="flat", cursor="hand2", activebackground="#a71d2a",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(0, 15), padx=20, fill='x')

    def on_toggle_theme(self):
        # Call the toggle callback first
        self.toggle_theme_callback()

        # Update button text depending on new mode
        self.mode = "dark" if self.mode == "light" else "light"
        new_text = "🌙 Dark Mode" if self.mode == "light" else "☀️ Light Mode"
        self.theme_button.config(text=new_text)

    # ===== Event Handling =====
    def bind_outside_click(self):
        """Close menu when clicking outside."""
        def on_click(event):
            if not self.winfo_containing(event.x_root, event.y_root):
                self.close_menu()
        self.bind_all("<Button-1>", on_click)

    def show_password_fields(self):
        if self.password_frame.winfo_ismapped():
            self.password_frame.pack_forget()
        else:
            self.password_frame.pack(pady=5, padx=15, fill='x')

    def send_confirmation_code(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Warning", "Please enter your email.")
            return

        self.email_code = ''.join(random.choices(string.digits, k=6))
        try:
            msg = MIMEText(f"Your password reset code is: {self.email_code}")
            msg["Subject"] = "Password Change Confirmation"
            msg["From"] = GMAIL_ADDRESS
            msg["To"] = email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_ADDRESS, email, msg.as_string())

            messagebox.showinfo("Success", f"Confirmation code sent to {email}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email:\n{e}")

    def change_password(self):
        import mysql.connector, hashlib
        curr = self.current_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()
        code = self.code_entry.get().strip()

        if not all([curr, new, confirm, code]):
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        if code != self.email_code:
            messagebox.showerror("Invalid Code", "Incorrect confirmation code.")
            return

        if new != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return

        conn = mysql.connector.connect(host="localhost", user="root", password="", database="marmudb")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM tbl_users WHERE username=%s", (self.username,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", "User not found.")
            return

        hashed_current = hashlib.sha256(curr.encode()).hexdigest()
        if row[0] != hashed_current:
            messagebox.showerror("Error", "Current password is incorrect.")
            return

        new_hashed = hashlib.sha256(new.encode()).hexdigest()
        cursor.execute("UPDATE tbl_users SET password=%s WHERE username=%s", (new_hashed, self.username))
        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Success", "Password changed successfully.")
        self.password_frame.pack_forget()

    def close_menu(self):
        self.unbind_all("<Button-1>")
        self.destroy()
