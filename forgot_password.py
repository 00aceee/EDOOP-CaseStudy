from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import messagebox
import smtplib
import random
import re
import hashlib  # For password hashing
from datetime import datetime, timedelta
import mysql.connector
from config import *
from utils import load_image
from dotenv import load_dotenv
import os

load_dotenv()  
YOUR_GMAIL = os.getenv("GMAIL_ADDRESS")
YOUR_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_EXPIRY_MINUTES = 5 

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "" 
DB_NAME = "marmudb"


class ForgotPasswordWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Forgot Password")
        self.configure(bg=BG_COLOR)

        self.stored_otp = None
        self.otp_sent_time = None

        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(padx=40, pady=30)

        card_frame = tk.Frame(main_frame, bg=CARD_COLOR, bd=2, relief="ridge")
        card_frame.pack(pady=20, fill="x")
        card_frame.config(width=500)

        tk.Label(card_frame, text="Forgot Password", font=("Arial", 16, "bold"),
                 fg=ACCENT_COLOR, bg=CARD_COLOR).pack(pady=15)

        def add_input(label_text, show=""):
            frame = tk.Frame(card_frame, bg=CARD_COLOR)
            frame.pack(pady=8, fill="x", padx=40)
            tk.Label(frame, text=label_text, fg=ACCENT_COLOR, bg=CARD_COLOR, font=("Arial", 11, "bold")).pack(anchor="w")
            entry = tk.Entry(frame, font=("Arial", 12), fg=FG_COLOR, bg="#333",
                 insertbackground="white", relief="flat", show=show, width=40)
            entry.pack(fill="x", ipady=6, pady=4)
            return entry

        # Email input + send OTP button
        email_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        email_frame.pack(pady=8, fill="x", padx=30)
        tk.Label(email_frame, text="Registered Email", fg=ACCENT_COLOR, bg=CARD_COLOR, font=("Arial", 11, "bold")).pack(anchor="w")

        input_email_frame = tk.Frame(email_frame, bg=CARD_COLOR)
        input_email_frame.pack(fill="x", pady=4)
        self.entry_email = tk.Entry(input_email_frame, font=("Arial", 12), fg=FG_COLOR, bg="#333",
                                    insertbackground="white", relief="flat", width=40)
        self.entry_email.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 5))

        self.send_otp_btn = tk.Button(input_email_frame, text="SEND OTP", font=("Arial", 10),
                                      fg="white", bg=ACCENT_COLOR, relief="flat",
                                      command=self.send_otp)
        self.send_otp_btn.pack(side="right", padx=(5, 0))

        # OTP input
        otp_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        otp_frame.pack(pady=8, fill="x", padx=30)
        tk.Label(otp_frame, text="OTP Code (6 digits)", fg=ACCENT_COLOR, bg=CARD_COLOR, font=("Arial", 11, "bold")).pack(anchor="w")
        self.entry_otp = tk.Entry(otp_frame, font=("Arial", 12), fg=FG_COLOR, bg="#333",
                          insertbackground="white", relief="flat", width=20)
        self.entry_otp.pack(fill="x", ipady=6, pady=4)

        self.status_label = tk.Label(otp_frame, text="", font=("Arial", 10), fg="green", bg=CARD_COLOR)
        self.status_label.pack(anchor="w", pady=2)

        # New password and confirmation
        self.entry_new_pass = add_input("New Password", show="*")
        self.entry_confirm_pass = add_input("Confirm New Password", show="*")

        btn_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Reset Password", font=("Arial", 12),
                  fg="white", bg=ACCENT_COLOR, relief="flat", width=15,
                  command=self.reset_password).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Cancel", font=("Arial", 12),
                  fg="white", bg="red", relief="flat", width=15,
                  command=self.cancel).grid(row=0, column=1, padx=10)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
        return re.match(pattern, email) is not None

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def send_otp(self):
        email = self.entry_email.get().strip()
        if not email:
            messagebox.showerror("Error", "Please enter your registered email.")
            return
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Please enter a valid Gmail address.")
            return

        # Check if user exists with this email in DB
        try:
            conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tbl_users WHERE email = %s", (email,))
            if cursor.fetchone() is None:
                messagebox.showerror("Error", "No account found with this email.")
                cursor.close()
                conn.close()
                return
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return

        otp = self.generate_otp()
        self.stored_otp = otp
        self.otp_sent_time = datetime.now()

        try:
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h2 style="color: #0078d7; text-align: center;">Marmu Barber & Tattoo Shop</h2>
                    <p style="font-size: 16px; color: #333;">Hi there,</p>
                    <p style="font-size: 16px; color: #333;">Use the following One-Time Password (OTP) to reset your password:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #ffffff; background-color: #0078d7; padding: 15px 25px; border-radius: 4px; letter-spacing: 5px;">
                            {otp}
                        </span>
                    </div>

                    <p style="font-size: 14px; color: #777;">
                        This code is valid for **{OTP_EXPIRY_MINUTES} minutes**. Do not share this code with anyone.
                    </p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center;">Thank you for choosing Marmu.</p>
                </div>
            </body>
            </html>
            """

            text_body = f"Your OTP for Marmu Barber & Tattoo Shop password reset is: {otp}. It expires in {OTP_EXPIRY_MINUTES} minutes."

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Your OTP for Password Reset"
            msg['From'] = YOUR_GMAIL
            msg['To'] = email

            msg.attach(MIMEText(text_body, 'plain')) 
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(YOUR_GMAIL, YOUR_APP_PASSWORD)
            server.send_message(msg)
            server.quit()

            self.send_otp_btn.config(text="OTP Sent!", state="disabled", bg="gray")
            self.status_label.config(text=f"OTP sent to {email}. Check your inbox (and spam).", fg="green")
            messagebox.showinfo("Success", "OTP sent! Enter it in the field below.")

        except Exception as e:
            self.stored_otp = None  
            self.otp_sent_time = None
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=ACCENT_COLOR)
            self.status_label.config(text="Failed to send OTP. Try again.", fg="red")
            messagebox.showerror("SMTP Error", f"Failed to send OTP: {str(e)}")

    def validate_otp(self, user_otp):
        if not user_otp.isdigit() or len(user_otp) != 6:
            return False, "OTP must be a 6-digit number."
        
        if not self.stored_otp or not self.otp_sent_time:
            return False, "No OTP sent. Click 'SEND OTP' first."
        
        if datetime.now() > self.otp_sent_time + timedelta(minutes=OTP_EXPIRY_MINUTES):
            self.stored_otp = None
            self.otp_sent_time = None
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=ACCENT_COLOR)
            return False, "OTP expired. Request a new one."
        
        if user_otp != self.stored_otp:
            return False, "Invalid OTP. Try again."
        
        return True, "Valid OTP."

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def reset_password(self):
        email = self.entry_email.get().strip()
        otp = self.entry_otp.get().strip()
        new_pass = self.entry_new_pass.get().strip()
        confirm_pass = self.entry_confirm_pass.get().strip()

        if not all([email, otp, new_pass, confirm_pass]):
            messagebox.showerror("Error", "All fields are required!")
            return

        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format!")
            return

        if len(new_pass) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        is_valid, msg = self.validate_otp(otp)
        if not is_valid:
            messagebox.showerror("Error", msg)
            return

        try:
            conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
            cursor = conn.cursor()

            # Update password for that email
            hashed_pass = self.hash_password(new_pass)
            query = "UPDATE tbl_users SET hash_pass = %s WHERE email = %s"
            cursor.execute(query, (hashed_pass, email))
            conn.commit()

            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Your password has been reset successfully.")
            self.destroy()
            self.parent.deiconify()

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", f"Error: {err}")

    def cancel(self):
        self.destroy()
        self.parent.deiconify()
