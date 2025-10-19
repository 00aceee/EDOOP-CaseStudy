import tkinter as tk
from tkinter import messagebox
import mysql.connector
import hashlib
from config import *
from utils import load_image
from signup_window import SignUpWindow
from main_window import MainWindow
from forgot_password import ForgotPasswordWindow
from admin_window import AdminWindow

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "marmudb"

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE_LOGIN)
        self.geometry("450x650")
        self.after(0, self.center_window())
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.logo_img_ref = load_image(LOGO_FILE_LOGIN, 150, 60)

        # Title
        tk.Label(self, text="MARMU BARBER & TATTOO SHOP",
            font=("Times New Roman", 18, "bold"),
            fg=FG_COLOR, bg=BG_COLOR).pack(pady=15)

        # Logo
        if self.logo_img_ref:
            logo_label = tk.Label(self, image=self.logo_img_ref, bg=BG_COLOR)
            logo_label.pack(pady=10)
        else:
            tk.Label(self, text="[LOGO]", fg=FG_COLOR,
                bg=BG_COLOR, font=("Arial", 14, "bold")).pack(pady=10)

        # Subtitle
        tk.Label(self, text="Since 2022", font=("Arial", 11),
                fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=5)

        # Form
        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Username", fg=ACCENT_COLOR, bg=BG_COLOR, font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=10)
        self.entry_user = tk.Entry(form_frame, font=("Arial", 12), fg=FG_COLOR, bg="#333", insertbackground="white")
        self.entry_user.grid(row=1, column=0, ipadx=50, ipady=5)

        tk.Label(form_frame, text="Password", fg=ACCENT_COLOR, bg=BG_COLOR, font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=10)
        self.entry_pass = tk.Entry(form_frame, font=("Arial", 12), fg=FG_COLOR, bg="#333", insertbackground="white", show="*")
        self.entry_pass.grid(row=3, column=0, ipadx=50, ipady=5)

        forgot_btn = tk.Label(form_frame, text="Forgot Password?", fg=ACCENT_COLOR,
                    bg=BG_COLOR, font=("Arial", 10, "underline"), cursor="hand2")
        forgot_btn.grid(row=4, column=0, sticky="e", pady=8)
        forgot_btn.bind("<Button-1>", lambda e: self.forgot_password())

        tk.Button(self, text="LOGIN", font=("Arial", 12, "bold"),
                    fg=BG_COLOR, bg=ACCENT_COLOR, relief="flat",
                    padx=20, pady=10, command=self.login).pack(pady=25)
        self.bind('<Return>', lambda event: self.login())

        create_btn = tk.Label(self, text="Create Account", fg=ACCENT_COLOR,
                            bg=BG_COLOR, font=("Arial", 10, "underline"), cursor="hand2")
        create_btn.pack()
        create_btn.bind("<Button-1>", lambda e: self.open_signup())

        tk.Label(self, text="Barber Ink © 2022", font=("Arial", 10),
                fg="gray", bg=BG_COLOR).pack(side="bottom", pady=10)

        # --- Hashing Utility (Must match signup_window.py) ---
    def hash_password(self, password):
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username_or_email = self.entry_user.get().strip()
        raw_password = self.entry_pass.get().strip()

        if not username_or_email or not raw_password:
            messagebox.showerror("Login Failed", "Username/Email and Password are required.")
            return

        conn = None
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            print("✅ Database connection successful.")
            cursor = conn.cursor()

            # Query to find user by username or email, also fetch role
            query = "SELECT username, fullname, hash_pass, role FROM tbl_users WHERE username = %s OR email = %s"
            cursor.execute(query, (username_or_email, username_or_email))
            result = cursor.fetchone()

            if result:
                authenticated_username, fullname, stored_hashed_pass, role = result
                input_hashed_pass = self.hash_password(raw_password)
                username = authenticated_username

                if input_hashed_pass == stored_hashed_pass:
                    messagebox.showinfo("Login Success", f"Welcome, {fullname}!")
                    
                    # Open window based on role
                    if role == 'Admin':
                        self.open_admin_window(username, role)
                    else:
                        self.open_main_window(username)
                else:
                    messagebox.showerror("Login Failed", "Invalid username/email or password.")
            else:
                messagebox.showerror("Login Failed", "Invalid username/email or password.")

        except mysql.connector.Error as err:
            print(f"❌ DATABASE CONNECTION FAILED: {err}")
            messagebox.showerror("Database Error", f"Failed to connect or query database: {err}")
        except Exception as e:
            print(f"🛑 UNEXPECTED ERROR: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def forgot_password(self):
        self.withdraw()  # hide current window
        ForgotPasswordWindow(self)
    
    def clear_login_fields(self):
        """Clears the username/email and password entry fields."""
        self.entry_user.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)

    def open_signup(self):
        self.withdraw()
        SignUpWindow(parent=self)

    def open_admin_window(self, username, role):
        self.withdraw() 
        is_admin = (role == 'Admin')  
        admin_win = AdminWindow(self, username, is_admin=is_admin)  
        admin_win.grab_set()

    def open_main_window(self, username):
        self.withdraw()
        main_win = MainWindow(self, username)
        main_win.grab_set()
