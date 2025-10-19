from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import * 
import os
from dotenv import load_dotenv
import random
import string
import hashlib
import re

load_dotenv()
YOUR_GMAIL = os.getenv("GMAIL_ADDRESS")
YOUR_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_EXPIRY_MINUTES = 5

class AdminWindow(tk.Toplevel):

    def __init__(self, parent, username, is_admin=False):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        self.title("Admin Panel")
        self.geometry("950x650")
        self.after(0, self.center_window)
        self.configure(bg="#222")

        self.db_config = {
            "host": DB_HOST,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "database": DB_NAME
        }
        
        menu_frame = tk.Frame(self, bg="#333", width=200)
        menu_frame.pack(side="left", fill="y")

        btn_appointments = tk.Button(menu_frame, text="Manage Appointments", fg="white", bg="#555",
                                     command=self.show_appointments_panel, relief="flat")
        btn_appointments.pack(fill="x", pady=10, padx=10)

        btn_users = tk.Button(menu_frame, text="Manage Users", fg="white", bg="#555",
                              command=self.show_users_panel, relief="flat")
        btn_users.pack(fill="x", pady=10, padx=10)


        btn_main = tk.Button(menu_frame, text="Go to Main Window", fg="white", bg="#555",
                             command=self.go_to_main_window, relief="flat")
        btn_main.pack(fill="x", pady=10, padx=10)

        menu_frame.pack_propagate(False) 

        bottom_frame = tk.Frame(menu_frame, bg="#333")
        bottom_frame.pack(side="bottom", fill="x", pady=20)

        logout_btn = tk.Button(bottom_frame, text='Logout', command=self.logout, bg="#444", fg="white", relief="flat")
        logout_btn.pack(fill="x", padx=10)

        self.content_frame = tk.Frame(self, bg="#111")
        self.content_frame.pack(side="right", expand=True, fill="both")

        self.show_appointments_panel()
        
    def generate_random_password(self, length=12):
        """Generates a random password for new users."""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for i in range(length))

    def hash_password(self, password):
        """Hashes a password using SHA-256 for secure storage."""
        
        return hashlib.sha256(password.encode()).hexdigest()

    def get_db_connection(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return None

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


    def show_users_panel(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Users", bg="#111", fg="white", font=("Arial", 16, "bold")).pack(pady=10)

        columns = ("ID", "Full name", "Username", "email", "Role") 

        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, anchor="center", width=120 if col in ("ID", "Role") else 150)
        tree.pack(expand=True, fill="both", padx=20, pady=10)

        conn = self.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fullname, username, email, role FROM tbl_users") 
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            cursor.close()
            conn.close()

        update_frame = tk.Frame(self.content_frame, bg="#222")
        update_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(update_frame, text="Full Name:", bg="#222", fg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        fullname_entry = tk.Entry(update_frame, width=30)
        fullname_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(update_frame, text="Username:", bg="#222", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        username_entry = tk.Entry(update_frame, width=30)
        username_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(update_frame, text="Email:", bg="#222", fg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        email_entry = tk.Entry(update_frame, width=30)
        email_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(update_frame, text="Role:", bg="#222", fg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        role_var = tk.StringVar()
        role_dropdown = ttk.Combobox(update_frame, textvariable=role_var, values=["User", "Admin"], state="readonly", width=28)
        role_dropdown.grid(row=3, column=1, padx=5, pady=5)
        role_dropdown.set("User")

        def on_user_select(event):
            selected = tree.selection()
            if selected:
                values = tree.item(selected[0], "values")
                fullname_entry.delete(0, tk.END); fullname_entry.insert(0, values[1])
                username_entry.delete(0, tk.END); username_entry.insert(0, values[2])
                email_entry.delete(0, tk.END); email_entry.insert(0, values[3])
                role_var.set(values[4])
        
        tree.bind("<<TreeviewSelect>>", on_user_select)


        def add_user():
            top = tk.Toplevel(self)
            top.title("Add New User")
            
            labels = ["Full Name", "Username", "Email", "Role"]
            entries = {}
            for i, label in enumerate(labels):
                tk.Label(top, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
                if label == "Role":
                    role_var_new = tk.StringVar(value="User")
                    ent = ttk.Combobox(top, textvariable=role_var_new, values=["User", "Admin"], state="readonly", width=28)
                    entries[label] = role_var_new
                else:
                    ent = tk.Entry(top, width=30)
                
                ent.grid(row=i, column=1, padx=10, pady=5)
                if label != "Role":
                    entries[label] = ent 

            def submit_add():
                fullname = entries["Full Name"].get().strip()
                username = entries["Username"].get().strip()
                email = entries["Email"].get().strip()
                role = entries["Role"].get() 
                
                if not all([fullname, username, email, role]):
                    messagebox.showerror("Error", "All fields are required.")
                    return
                
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    messagebox.showerror("Error", "Invalid email format.")
                    return

                conn = self.get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    try:

                        cursor.execute(
                            "SELECT id FROM tbl_users WHERE username = %s OR email = %s",
                            (username, email)
                        )
                        if cursor.fetchone():
                            messagebox.showerror("Error", "Username or Email already exists.")
                            return
                        
                        temp_pass = self.generate_random_password()
                        hashed_pass = self.hash_password(temp_pass)

                        query = ("INSERT INTO tbl_users (fullname, username, email, hash_pass, role) "
                                 "VALUES (%s, %s, %s, %s, %s)")
                        cursor.execute(query, (fullname, username, email, hashed_pass, role))
                        conn.commit()
                        
                        messagebox.showinfo("Success", f"User added. Temporary Password: {temp_pass}\n\nPlease inform the user to change their password immediately.")

                        entries["Full Name"].delete(0, tk.END)
                        entries["Username"].delete(0, tk.END)
                        entries["Email"].delete(0, tk.END)
                        entries["Role"].set("User")

                        top.destroy()
                        self.show_users_panel()
                    except mysql.connector.Error as err:
                        messagebox.showerror("DB Error", f"Error adding user: {err}")
                    finally:
                        cursor.close()
                        conn.close()

            tk.Button(top, text="Create User", command=submit_add).grid(row=len(labels), column=0, columnspan=2, pady=10)

        def update_user_info():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select user", "Please select a user to update.")
                return
            user_id = tree.item(selected[0], "values")[0]
            fullname = fullname_entry.get().strip()
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            role = role_var.get()

            if not fullname or not username or not email or not role:
                messagebox.showerror("Error", "All fields are required.")
                return

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Error", "Invalid email format.")
                return

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "SELECT id FROM tbl_users WHERE (username = %s OR email = %s) AND id != %s",
                        (username, email, user_id)
                    )
                    if cursor.fetchone():
                        messagebox.showerror("Error", "Username or Email already taken by another user.")
                        return

                    cursor.execute(
                        "UPDATE tbl_users SET fullname=%s, username=%s, email=%s, role=%s WHERE id=%s",
                        (fullname, username, email, role, user_id)
                    )
                    conn.commit()
                    messagebox.showinfo("Success", "User info updated.")
                    self.show_users_panel()  # Refresh list
                except mysql.connector.Error as err:
                    messagebox.showerror("DB Error", f"Error updating user: {err}")
                finally:
                    cursor.close()
                    conn.close()

        def delete_user():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select user", "Please select a user to delete.")
                return
            
            user_id = tree.item(selected[0], "values")[0]
            username_to_delete = tree.item(selected[0], "values")[2]
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user: {username_to_delete}?"):
                conn = self.get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("DELETE FROM tbl_users WHERE id = %s", (user_id,))
                        conn.commit()
                        messagebox.showinfo("Success", f"User {username_to_delete} deleted.")
                        
                        # Clear entries and refresh panel
                        fullname_entry.delete(0, tk.END)
                        username_entry.delete(0, tk.END)
                        email_entry.delete(0, tk.END)
                        role_var.set("User")
                        self.show_users_panel() 
                    except mysql.connector.Error as err:
                        messagebox.showerror("DB Error", f"Error deleting user: {err}")
                    finally:
                        cursor.close()
                        conn.close()
        
        
        btn_action_frame = tk.Frame(self.content_frame, bg="#111")
        btn_action_frame.pack(fill="x", padx=20, pady=10)

        insert_btn = tk.Button(btn_action_frame, text="Insert New User", command=add_user, bg="#4CAF50", fg="white")
        insert_btn.pack(side="left", padx=5)

        update_btn = tk.Button(btn_action_frame, text="Update Selected User", command=update_user_info, bg="#555", fg="white")
        update_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(btn_action_frame, text="Delete Selected User", command=delete_user, bg="#F44336", fg="white")
        delete_btn.pack(side="left", padx=5)


    def show_appointments_panel(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Appointments", bg="#111", fg="white",
                font=("Arial", 16, "bold")).pack(pady=10)

        # ✅ Include ID for proper linking
        columns = ("id", "fullname", "service", "appointment_date", "time", "remarks", "status")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col.title())
            width = 120 if col not in ("remarks", "fullname", "service") else 150
            tree.column(col, anchor="center", width=width)

        # ✅ Hide ID visually but keep it accessible
        tree.column("id", width=0, stretch=False)

        tree.pack(expand=True, fill="both", padx=20, pady=20)

        # ✅ Load appointments from database
        conn = self.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, fullname, service, appointment_date, time, remarks, status 
                FROM tbl_appointment
            """)
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            cursor.close()
            conn.close()

        # ✅ Buttons for actions
        btn_frame = tk.Frame(self.content_frame, bg="#111")
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Add Appointment", 
                command=lambda: self.add_appointment(tree), 
                bg="#4CAF50", fg="white").pack(side="left", padx=5)

        tk.Button(btn_frame, text="Update Appointment", 
                command=lambda: self.update_appointment(tree), 
                bg="#555", fg="white").pack(side="left", padx=5)

        tk.Button(btn_frame, text="Approve", 
                command=lambda: self.change_approval(tree, status="Approved"), 
                bg="#0078D7", fg="white").pack(side="left", padx=5)

        tk.Button(btn_frame, text="Deny", 
                command=lambda: self.change_approval(tree, status="Denied"), 
                bg="#F44336", fg="white").pack(side="left", padx=5)


    def add_appointment(self, tree):
        top = tk.Toplevel(self)
        top.title("Add Appointment")

        labels = ["Fullname", "Service", "Date", "Time", "Remarks"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(top, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ent = tk.Entry(top, width=30)
            ent.grid(row=i, column=1, padx=10, pady=5)
            entries[label] = ent

        def submit_add():
            fullname = entries["Fullname"].get().strip()
            service = entries["Service"].get().strip()
            date = entries["Date"].get().strip()
            time_val = entries["Time"].get().strip()
            remarks = entries["Remarks"].get().strip()

            if not all([fullname, service, date, time_val]):
                messagebox.showerror("Error", "Fullname, Service, Date, and Time are required.")
                return

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    query = ("INSERT INTO tbl_appointment "
                             "(fullname, service, appointment_date, time, remarks, status) "
                             "VALUES (%s, %s, %s, %s, %s, %s)")
                    cursor.execute(query, (fullname, service, date, time_val, remarks, "Pending"))
                    conn.commit()
                    messagebox.showinfo("Success", "Appointment added.")

                    entries["Fullname"].delete(0, tk.END)
                    entries["Service"].delete(0, tk.END)
                    entries["Date"].delete(0, tk.END)
                    entries["Time"].delete(0, tk.END)
                    entries["Remarks"].delete(0, tk.END)
            
                    top.destroy()
                    self.show_appointments_panel()
                except mysql.connector.Error as err:
                    messagebox.showerror("DB Error", f"Error adding appointment: {err}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(top, text="Submit", command=submit_add).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def update_appointment(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an appointment to update.")
            return
        values = tree.item(selected[0], "values")
        top = tk.Toplevel(self)
        top.title("Update Appointment")

        labels = ["Fullname", "Service", "Date", "Time", "Remarks", "Status"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(top, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ent = tk.Entry(top, width=30)
            ent.grid(row=i, column=1, padx=10, pady=5)
            ent.insert(0, values[i])
            entries[label] = ent

        def submit_update():
            fullname = entries["Fullname"].get().strip()
            service = entries["Service"].get().strip()
            date = entries["Date"].get().strip()
            time_val = entries["Time"].get().strip()
            remarks = entries["Remarks"].get().strip()
            status = entries["Status"].get().strip()

            if not all([fullname, service, date, time_val]):
                messagebox.showerror("Error", "Fullname, Service, Date, and Time are required.")
                return

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    query = ("UPDATE tbl_appointment SET fullname=%s, service=%s, appointment_date=%s, time=%s, remarks=%s, status=%s "
                              "WHERE fullname=%s AND appointment_date=%s AND time=%s")
                    cursor.execute(query, (fullname, service, date, time_val, remarks, status,
                                             values[0], values[2], values[3]))
                    conn.commit()
                    messagebox.showinfo("Success", "Appointment updated.")
                    top.destroy()
                    self.show_appointments_panel()
                except mysql.connector.Error as err:
                    messagebox.showerror("DB Error", f"Error updating: {err}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(top, text="Update", command=submit_update).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def change_approval(self, tree, status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an appointment first.")
            return

        values = tree.item(selected[0], "values")
        appointment_id = values[0]  # ✅ Now correctly gets ID
        fullname, service, date, time_val = values[1], values[2], values[3], values[4]

        conn = self.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # ✅ Get user_id & fullname from appointment
                cursor.execute("SELECT user_id, fullname FROM tbl_appointment WHERE id = %s", (appointment_id,))
                result = cursor.fetchone()

                if not result:
                    messagebox.showerror("Error", "Appointment not found.")
                    return

                user_id, appointment_fullname = result

                # ✅ Handle missing user_id (fallback to name search)
                if user_id is None:
                    cursor.execute("SELECT id, email, fullname FROM tbl_users WHERE fullname = %s", (appointment_fullname,))
                    user_result = cursor.fetchone()

                    if not user_result:
                        messagebox.showerror("Error", "No linked user or matching name found.")
                        return

                    user_id, user_email, fullname = user_result

                    # Permanently link the appointment to this user
                    cursor.execute("UPDATE tbl_appointment SET user_id = %s WHERE id = %s", (user_id, appointment_id))
                    conn.commit()
                else:
                    # ✅ Get user email using the existing user_id
                    cursor.execute("SELECT email, fullname FROM tbl_users WHERE id = %s", (user_id,))
                    user_result = cursor.fetchone()

                    if not user_result:
                        messagebox.showerror("Error", "User not found in tbl_users.")
                        return

                    user_email, fullname = user_result

                # ✅ Update appointment status
                cursor.execute("UPDATE tbl_appointment SET status = %s WHERE id = %s", (status, appointment_id))
                conn.commit()

                messagebox.showinfo("Success", f"Appointment {status} successfully!")

                # ✅ Send notification email
                self.send_decision_email(user_email, fullname, service, date, time_val, status)

                # ✅ Refresh table
                self.show_appointments_panel()

            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", f"Error changing approval: {err}")
            finally:
                cursor.close()
                conn.close()

    def send_decision_email(self, email, name, service, date, time, decision):
        subject = f"Your Appointment has been {decision}"

        # 1. Plain Text Body (Fallback for non-HTML email clients)
        text_body = f"""
        Hello {name},

        Your appointment for {service} on {date} at {time} has been {decision}.

        Regards,
        Marmu Barber & Tattoo Shop
        """

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                
                <h2 style="color: #0078d7; text-align: center;">Marmu Barber & Tattoo Shop</h2>
                
                <p style="font-size: 16px; color: #333;">Hello {name},</p>
                
                <p style="font-size: 16px; color: #333;">
                    We are writing to inform you about the status of your appointment.
                </p>

                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 18px; color: #333; margin-bottom: 10px;">
                        Your appointment status is:
                    </p>
                    <span style="font-size: 24px; font-weight: bold; 
                                color: {'white' if decision == 'Approved' else '#333'}; 
                                background-color: {'#4CAF50' if decision == 'Approved' else '#F44336' if decision == 'Denied' else '#FFC107'}; 
                                padding: 10px 20px; border-radius: 4px; display: inline-block;">
                        {decision}
                    </span>
                </div>
                
                <p style="font-size: 16px; color: #333;">
                    **Details:**
                    <ul>
                        <li>**Service:** {service}</li>
                        <li>**Date:** {date}</li>
                        <li>**Time:** {time}</li>
                    </ul>
                </p>

                <p style="font-size: 16px; color: #333;">
                    {'Thank you for booking! We look forward to seeing you.' if decision == 'Approved' else 'Please feel free to reschedule at a different time.'}
                </p>
                
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="font-size: 14px; color: #999; text-align: center;">Regards,<br>Marmu Barber & Tattoo Shop</p>
                
            </div>
        </body>
        </html>
        """

        try:
            # Use 'alternative' to include both plain text and HTML
            msg = MIMEMultipart('alternative')
            msg['From'] = YOUR_GMAIL
            msg['To'] = email
            msg['Subject'] = subject
            
            # Attach parts into message container.
            # The client (Gmail, Outlook, etc.) chooses the best option.
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(YOUR_GMAIL, YOUR_APP_PASSWORD)
            server.sendmail(YOUR_GMAIL, email, msg.as_string())
            server.quit()
            print(f"✅ Email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    def go_to_main_window(self):
        from main_window import MainWindow
        self.withdraw()
        main_win = MainWindow(self, self.username, is_admin=self.is_admin)
        main_win.grab_set()

    def logout(self):
        self.destroy() 
        if hasattr(self.parent, 'clear_login_fields'):
            self.parent.clear_login_fields()
        self.parent.deiconify()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
