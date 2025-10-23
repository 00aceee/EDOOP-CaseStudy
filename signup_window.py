from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import tkinter as tk
from tkinter import messagebox
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
YOUR_APP_PASSWORD = os.getenv("GMAIL_APP")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_EXPIRY_MINUTES = 5

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "" 
DB_NAME = "marmudb"


class SignUpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title(APP_TITLE_SIGNUP)
        self.configure(bg=BG_COLOR)

        # OTP storage
        self.stored_otp = None
        self.otp_sent_time = None
        self.send_otp_btn = None

        self.resizable(False, False)

        # Main frame for all content
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(padx=40, pady=30)

        card_frame = tk.Frame(main_frame, bg=CARD_COLOR, bd=2, relief="ridge")
        card_frame.pack(pady=20, fill="x")
        card_frame.config(width=500)

        tk.Label(card_frame, text="Create Account", font=("Arial", 16, "bold"),
                 fg=ACCENT_COLOR, bg=CARD_COLOR).pack(pady=15)

        def add_input(label_text, show="*"):
            frame = tk.Frame(card_frame, bg=CARD_COLOR)
            frame.pack(pady=8, fill="x", padx=40)
            tk.Label(frame, text=label_text, fg=ACCENT_COLOR, bg=CARD_COLOR, font=("Arial", 11, "bold")).pack(anchor="w")
            entry = tk.Entry(frame, font=("Arial", 12), fg=FG_COLOR, bg="#333",
                 insertbackground="white", relief="flat", width=40, show=show)
            entry.pack(fill="x", ipady=6, pady=4)
            return entry

        self.entry_fullname = add_input("Full Name", show="")
        self.entry_user = add_input("Username", show="")

        # Email + SEND OTP button on same line but aligned nicely
        email_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        email_frame.pack(pady=8, fill="x", padx=40)
        tk.Label(email_frame, text="Email", fg=ACCENT_COLOR, bg=CARD_COLOR, font=("Arial", 11, "bold")).pack(anchor="w")

        input_email_frame = tk.Frame(email_frame, bg=CARD_COLOR)
        input_email_frame.pack(fill="x", pady=4)

        self.entry_email = tk.Entry(input_email_frame, font=("Arial", 12), fg=FG_COLOR, bg="#333",
                            insertbackground="white", relief="flat")
        self.entry_email.pack(side="left", fill="x", expand=True, ipady=6)

        self.send_otp_btn = tk.Button(input_email_frame, text="SEND OTP", font=("Arial", 10),
                                      fg="white", bg=BG_COLOR_DARK, relief="flat",
                                      command=self.send_otp, width=10)
        self.send_otp_btn.pack(side="right", padx=(5, 0), ipady=4)
        self.bind('<Return>', lambda event: self.send_otp())

        self.entry_pass = add_input("Password", show="*")
        self.entry_confirm = add_input("Confirm Password", show="*")

        otp_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        otp_frame.pack(pady=8, fill="x", padx=40)
        tk.Label(otp_frame, text="OTP Code (6 digits)", fg=ACCENT_COLOR, bg=CARD_COLOR, font=("Arial", 11, "bold")).pack(anchor="w")
        self.entry_otp = tk.Entry(otp_frame, font=("Arial", 12), fg=FG_COLOR, bg="#333",
                          insertbackground="white", relief="flat")
        self.entry_otp.pack(fill="x", ipady=6, pady=4)

        self.status_label = tk.Label(otp_frame, text="", font=("Arial", 10), fg="green", bg=CARD_COLOR)
        self.status_label.pack(anchor="w", pady=2)

        btn_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        btn_frame.pack(pady=20)

        self.signup_btn = tk.Button(
            btn_frame, 
            text="Sign Up", 
            font=("Arial", 12),
            fg="white", 
            bg=BG_COLOR_DARK, 
            relief="flat", 
            padx=10, pady=0,
            width=12,
            command=self.signup, 
            activebackground="#888", 
            activeforeground=ACCENT_COLOR
        )
        self.signup_btn.pack(side="left", pady=30, padx=10)
        self.bind('<Return>', lambda event: self.signup())

        self.clear_btn = tk.Button(
            btn_frame,
            text="Clear",
            font=("Arial", 12),
            fg=FG_COLOR_LIGHT,
            bg=BG_COLOR_LIGHT,
            relief="flat", 
            padx=10, pady=0,
            width=12,
            command=self.clear_fields
        )
        self.clear_btn.pack(side="left", pady=30, padx=10)
        self.bind('<Return>', lambda event: self.clear_fields())

        back_btn = tk.Label(main_frame, text="Back to Login", fg=ACCENT_COLOR,
                            bg=BG_COLOR, font=("Arial", 11, "underline"), cursor="hand2")
        back_btn.pack(pady=10)
        back_btn.bind("<Button-1>", lambda e: self.back_to_login())

        self.protocol("WM_DELETE_WINDOW", self.back_to_login)

        self.update_idletasks()
        self.center_window()

    def generate_otp(self):
        """Generate a random 6-digit OTP."""
        return str(random.randint(100000, 999999))

    def is_valid_email(self, email):
        """Basic email validation using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail.com$'  
        return re.match(pattern, email) is not None

    def send_otp(self):

        self.send_otp_btn.config(state="disabled", text="Sending OTP", bg="#888")
        self.update_idletasks() 

        email = self.entry_email.get().strip()
        if not email:
            messagebox.showerror("Error", "Please enter your email first.")
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=BG_COLOR_DARK)
            return
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Please enter a valid Gmail address.")
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=BG_COLOR_DARK)
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
                    <p style="font-size: 16px; color: #333;">Use the following One-Time Password (OTP) to complete your signup process:</p>
                    
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

            text_body = f"Your OTP for Marmu Barber & Tattoo Shop Signup is: {otp}. It expires in {OTP_EXPIRY_MINUTES} minutes."

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Your OTP for Signup"
            msg['From'] = YOUR_GMAIL
            msg['To'] = email

            msg.attach(MIMEText(text_body, 'plain')) 
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(YOUR_GMAIL, YOUR_APP_PASSWORD)
            server.send_message(msg)
            server.quit()

            self.send_otp_btn.config(text="OTP Sent!", state="disabled", bg="#888")
            self.status_label.config(text=f"OTP sent to {email}. Check your inbox (and spam).", fg="green")
            messagebox.showinfo("Success", "OTP sent! Enter it in the OTP field below.")

        except Exception as e:
            self.stored_otp = None  
            self.otp_sent_time = None
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=BG_COLOR_DARK)
            self.status_label.config(text="Failed to send OTP. Try again.", fg="red")
            messagebox.showerror("SMTP Error", f"Failed to send OTP: {str(e)}\nCheck your internet and SMTP settings.")

    def validate_otp(self, user_otp):
        """Check if OTP is valid (matches, 6 digits, not expired)."""
        if not user_otp.isdigit() or len(user_otp) != 6:
            return False, "OTP must be a 6-digit number."
        
        if not self.stored_otp or not self.otp_sent_time:
            return False, "No OTP sent. Click 'SEND OTP' first."
        
        if datetime.now() > self.otp_sent_time + timedelta(minutes=OTP_EXPIRY_MINUTES):
            self.stored_otp = None
            self.otp_sent_time = None
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=BG_COLOR_DARK)
            return False, "OTP expired. Request a new one."
        
        if user_otp != self.stored_otp:
            return False, "Invalid OTP. Try again."
        
        return True, "Valid OTP."

    def hash_password(self, password):
        """Hash the password using SHA-256 (upgrade to bcrypt for production)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def user_exists(self, conn, username, email):
        """Check if username or email already exists in DB."""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tbl_users WHERE username = %s OR email = %s", (username, email))
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

    def signup(self):

        self.signup_btn.config(state="disabled", text="Processing...", bg="#888")
        self.update_idletasks()

        fullname = self.entry_fullname.get().strip()
        username = self.entry_user.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_pass.get().strip()
        confirm_pass = self.entry_confirm.get().strip()
        otp = self.entry_otp.get().strip()

        if not all([fullname, username, email, password, confirm_pass, otp]):
            messagebox.showerror("Error", "All fields are required!")
            self.signup_btn.config(state="normal", text="Sign Up", bg=BG_COLOR_DARK)
            return
        if password != confirm_pass:
            messagebox.showerror("Error", "Passwords do not match!")
            self.signup_btn.config(state="normal", text="Sign Up", bg=BG_COLOR_DARK)
            return
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format!")
            self.signup_btn.config(state="normal", text="Sign Up", bg=BG_COLOR_DARK)
            return
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            self.signup_btn.config(state="normal", text="Sign Up", bg=BG_COLOR_DARK)
            return

        is_valid, msg = self.validate_otp(otp)
        if not is_valid:
            messagebox.showerror("Error", msg)
            self.submit_btn.config(state="normal", text="Sign Up", bg=BG_COLOR_DARK)
            return

        conn = None
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = conn.cursor()

            if self.user_exists(conn, username, email):
                messagebox.showerror("Error", "Username or email already exists. Please choose different ones.")
                return

            hashed_pass = self.hash_password(password)

            query = "INSERT INTO tbl_users (fullname, username, email, hash_pass) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (fullname, username, email, hashed_pass))
            conn.commit()

            self.stored_otp = None
            self.otp_sent_time = None
            self.send_otp_btn.config(state="normal", text="SEND OTP", bg=ACCENT_COLOR)
            self.status_label.config(text="", fg="green")

            messagebox.showinfo("Success", f"Welcome, {fullname}! Your account ({username}) has been created.")
            self.back_to_login()

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            if conn:
                cursor.close()
                conn.close()
                self.signup_btn.config(state="normal", text="Sign Up", bg=ACCENT_COLOR)

    def clear_fields(self):
        self.entry_fullname.delete(0, tk.END)
        self.entry_user.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)
        self.entry_confirm.delete(0, tk.END)
        self.entry_otp.delete(0, tk.END)
        self.status_label.config(text="")
        self.stored_otp = None
        self.otp_sent_time = None
        self.send_otp_btn.config(state="normal", text="SEND OTP", bg=ACCENT_COLOR)

    def back_to_login(self):
        self.destroy()
        self.parent.deiconify()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')


