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
YOUR_APP_PASSWORD = os.getenv("GMAIL_APP")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

class AdminWindow(tk.Toplevel):

    def __init__(self, parent, username, is_admin=False):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        self.title("Admin Panel - Logged in as: " + username)
        self.geometry("950x650")
        self.configure(bg="#212121")
        self.after(0, self.center_window)

        self.db_config = {
            "host": DB_HOST,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "database": DB_NAME
        }

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#444", foreground="white")
        self.style.configure("Treeview", background="#333", foreground="white", fieldbackground="#333", rowheight=25)
        self.style.map("Treeview", background=[('selected', '#007ACC')], foreground=[('selected', 'white')])

        self.style.configure("Sidebar.TButton", font=("Arial", 9), foreground="white", background="#424242", 
                             relief="flat", padding=[15, 10])
        self.style.map("Sidebar.TButton", background=[('active', '#5A5A5A')])


        menu_frame = tk.Frame(self, bg="#333", width=200)
        menu_frame.pack(side="left", fill="y")
        menu_frame.pack_propagate(False)

        tk.Label(menu_frame, text="Admin Menu", font=("Arial", 14, "bold"), fg="#007ACC", bg="#333").pack(fill="x", pady=(20, 15), padx=10)


        ttk.Button(menu_frame, text="📅 Manage Appointments", style="Sidebar.TButton",
                     command=self.show_appointments_panel).pack(fill="x", pady=(5, 2), padx=10)

        ttk.Button(menu_frame, text="👤 Manage Users", style="Sidebar.TButton",
                     command=self.show_users_panel).pack(fill="x", pady=(5, 2), padx=10)
        
        ttk.Button(menu_frame, text="⭐ View Feedback", style="Sidebar.TButton",
           command=self.show_feedback_panel).pack(fill="x", pady=(5, 2), padx=10)

        ttk.Button(menu_frame, text="🏠 Go to Main Window", style="Sidebar.TButton",
                     command=self.go_to_main_window).pack(fill="x", pady=(5, 2), padx=10)

        logout_btn = tk.Button(menu_frame, text="🚫 Logout", command=self.logout, 
                               bg="#DC3545", fg="white", relief="flat", activebackground="#A71D2A",
                               font=("Arial", 11, "bold"))
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)

        self.content_frame = tk.Frame(self, bg="#212121")
        self.content_frame.pack(side="right", expand=True, fill="both")

        self.show_appointments_panel()

    def generate_random_password(self, length=12):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def get_db_connection(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect to database: {err}")
            return None

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_users_panel(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Manage Users", bg="#212121", fg="#FFFFFF",
                 font=("Arial", 18, "bold")).pack(pady=(20, 10))

        btn_frame = tk.Frame(self.content_frame, bg="#212121")
        btn_frame.pack(fill="x", pady=10, padx=20)

        tk.Button(btn_frame, text="➕ Add New User", command=lambda: self.add_user(tree),
                      bg="#28A745", fg="white", relief="flat", activebackground="#1e7e34").pack(side="left", padx=5, ipadx=5, ipady=3)
        
        tk.Button(btn_frame, text="🔄 Change Role", command=lambda: self.change_user_role(tree),
                      bg="#FF9800", fg="white", relief="flat", activebackground="#cc7a00").pack(side="left", padx=5, ipadx=5, ipady=3)
                      
        tk.Button(btn_frame, text="🗑️ Delete Selected User", command=lambda: self.delete_user(tree),
                      bg="#F44336", fg="white", relief="flat", activebackground="#dc3545").pack(side="left", padx=5, ipadx=5, ipady=3)
        
        columns = ("ID", "Full name", "Username", "Email", "Role")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150 if col != "ID" else 50)
        tree.column("ID", width=0, stretch=False)
            
        tree.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        conn = self.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fullname, username, email, role FROM tbl_users")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            cursor.close()
            conn.close()


    def add_user(self, tree):
        top = tk.Toplevel(self)
        top.title("Add New User")
        top.configure(bg="#F0F0F0")
        top.transient(self)
        top.grab_set()
        
        top.update_idletasks()
        w, h = top.winfo_width(), top.winfo_height()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        top.geometry(f"+{x}+{y}")
        
        form_frame = tk.Frame(top, padx=15, pady=15, bg="#F0F0F0")
        form_frame.pack(fill="both", expand=True)

        labels = ["Full Name", "Username", "Email", "Role"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=f"{label}:", bg="#F0F0F0", font=("Arial", 10)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            if label == "Role":
                var = tk.StringVar(value="User")
                cb = ttk.Combobox(form_frame, textvariable=var, values=["User", "Admin"], state="readonly", width=28)
                cb.grid(row=i, column=1, padx=10, pady=5)
                entries[label] = var
            else:
                ent = tk.Entry(form_frame, width=30)
                ent.grid(row=i, column=1, padx=10, pady=5)
                entries[label] = ent

        def submit():
            fullname, username, email, role = (entries["Full Name"].get().strip(),
                                                entries["Username"].get().strip(),
                                                entries["Email"].get().strip(),
                                                entries["Role"].get())
            if not all([fullname, username, email, role]):
                messagebox.showerror("Error", "All fields are required.", parent=top)
                return
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Error", "Invalid email format.", parent=top)
                return

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT id FROM tbl_users WHERE username=%s OR email=%s", (username, email))
                    if cursor.fetchone():
                        messagebox.showerror("Error", "Username or email already exists.", parent=top)
                        return
                    temp_pass = self.generate_random_password()
                    hashed = self.hash_password(temp_pass)
                    cursor.execute("INSERT INTO tbl_users (fullname, username, email, hash_pass, role) VALUES (%s, %s, %s, %s, %s)",
                                   (fullname, username, email, hashed, role))
                    conn.commit()
                    messagebox.showinfo("Success", f"User added.\nTemporary Password: {temp_pass}", parent=top)
                    top.destroy()
                    self.show_users_panel()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to add user: {e}", parent=top)
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(form_frame, text="Submit", command=submit, bg="#007ACC", fg="white", relief="flat", activebackground="#005bb5").grid(row=len(labels), column=0, columnspan=2, pady=15, sticky="ew")

    def delete_user(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a user to delete.")
            return
        user_id = tree.item(selected[0], "values")[0]
        username = tree.item(selected[0], "values")[2]
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete user: {username}?"):
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM tbl_appointment WHERE user_id=%s", (user_id,)) 
                    cursor.execute("DELETE FROM tbl_users WHERE id=%s", (user_id,))
                    conn.commit()
                    messagebox.showinfo("Success", f"User {username} and associated appointments deleted.")
                    self.show_users_panel()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to delete user: {e}")
                finally:
                    cursor.close()
                    conn.close()
    
    def change_user_role(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a user to change the role.")
            return
            
        user_values = tree.item(selected[0], "values")
        user_id, fullname, username, email, current_role = user_values[0], user_values[1], user_values[2], user_values[3], user_values[4]

        top = tk.Toplevel(self)
        top.title(f"Change Role for {username}")
        top.configure(bg="#F0F0F0")
        top.transient(self)
        top.grab_set()

        tk.Label(top, text=f"User: {fullname} ({username})", font=("Arial", 12, "bold"), bg="#F0F0F0").grid(row=0, column=0, columnspan=2, padx=15, pady=10)
        tk.Label(top, text="Current Role:", bg="#F0F0F0").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Label(top, text=current_role, font=("Arial", 10, "italic"), bg="#F0F0F0").grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        tk.Label(top, text="New Role:", bg="#F0F0F0").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        role_var = tk.StringVar(value=current_role)
        role_cb = ttk.Combobox(top, textvariable=role_var, values=["User", "Admin"], state="readonly", width=20)
        role_cb.grid(row=2, column=1, padx=10, pady=5)
        
        def update_role():
            new_role = role_var.get()
            if new_role == current_role:
                messagebox.showwarning("No Change", "The selected role is the same as the current role.", parent=top)
                return
            
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE tbl_users SET role=%s WHERE id=%s", (new_role, user_id))
                    conn.commit()
                    messagebox.showinfo("Success", f"Role for {username} updated to {new_role}.", parent=top)
                    top.destroy()
                    self.show_users_panel()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to update role: {e}", parent=top)
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(top, text="Update Role", command=update_role, bg="#007ACC", fg="white", relief="flat", activebackground="#005bb5").grid(row=3, column=0, columnspan=2, pady=15, sticky="ew", padx=10)


    def show_appointments_panel(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Manage Appointments", bg="#212121", fg="#FFFFFF",
                 font=("Arial", 20, "bold")).pack(pady=(20, 10))
                 
        btn_frame = tk.Frame(self.content_frame, bg="#212121")
        btn_frame.pack(fill="x", pady=10, padx=20)

        tk.Button(btn_frame, text="➕ Add Appointment", command=lambda: self.add_appointment(tree),
                      bg="#28A745", fg="white", relief="flat", activebackground="#1e7e34").pack(side="left", padx=5, ipadx=5, ipady=3)
        tk.Button(btn_frame, text="✅ Approve Selected", command=lambda: self.change_approval(tree, "Approved"),
                      bg="#007ACC", fg="white", relief="flat", activebackground="#005bb5").pack(side="left", padx=5, ipadx=5, ipady=3)
        tk.Button(btn_frame, text="❌ Deny Selected", command=lambda: self.change_approval(tree, "Denied"),
                      bg="#F44336", fg="white", relief="flat", activebackground="#dc3545").pack(side="left", padx=5, ipadx=5, ipady=3)


        columns = ("id", "fullname", "service", "appointment_date", "time", "remarks", "status")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col.title().replace("_", " "))
            width = 130 if col not in ["remarks", "id"] else 180 if col == "remarks" else 0
            tree.column(col, anchor="center", width=width, stretch=False if col == "id" else True)
        tree.column("id", width=0, stretch=False)
        tree.column("status", width=80, stretch=False)
        tree.column("time", width=80, stretch=False)
        
        tree.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        conn = self.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fullname, service, appointment_date, time, remarks, status FROM tbl_appointment")
            for row in cursor.fetchall():
                if row[6] == "Approved":
                    tag = 'approved'
                elif row[6] == "Denied":
                    tag = 'denied'
                else:
                    tag = 'pending'
                tree.insert("", "end", values=row, tags=(tag,))
            
            self.style.configure("approved", foreground="#28A745", font=("Arial", 10, "bold"))
            self.style.configure("denied", foreground="#F44336", font=("Arial", 10, "bold"))
            self.style.configure("pending", foreground="#FFC107", font=("Arial", 10, "bold"))

            cursor.close()
            conn.close()

    def add_appointment(self, tree):
        top = tk.Toplevel(self)
        top.title("Add Appointment")
        top.configure(bg="#F0F0F0")
        top.transient(self)
        top.grab_set()
        
        top.update_idletasks()
        w, h = top.winfo_width(), top.winfo_height()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        top.geometry(f"+{x}+{y}")
        
        form_frame = tk.Frame(top, padx=15, pady=15, bg="#F0F0F0")
        form_frame.pack(fill="both", expand=True)

        labels = ["Fullname", "Service", "Date (YYYY-MM-DD)", "Time (HH:MM)", "Remarks"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=f"{label}:", bg="#F0F0F0", font=("Arial", 10)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ent = tk.Entry(form_frame, width=30)
            ent.grid(row=i, column=1, padx=10, pady=5)
            entries[label.split(' ')[0]] = ent

        def submit_add():
            fullname = entries["Fullname"].get().strip()
            service = entries["Service"].get().strip()
            date = entries["Date"].get().strip()
            time_val = entries["Time"].get().strip()
            remarks = entries["Remarks"].get().strip()

            if not all([fullname, service, date, time_val]):
                messagebox.showerror("Error", "Fullname, Service, Date, and Time are required.", parent=top)
                return

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO tbl_appointment (fullname, service, appointment_date, time, remarks, status) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (fullname, service, date, time_val, remarks, "Pending"))
                    conn.commit()
                    messagebox.showinfo("Success", "Appointment added.", parent=top)
                    top.destroy()
                    self.show_appointments_panel()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to add appointment: {e}", parent=top)
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(form_frame, text="Submit", command=submit_add, bg="#007ACC", fg="white", relief="flat", activebackground="#005bb5").grid(row=len(labels), column=0, columnspan=2, pady=15, sticky="ew")

    def change_approval(self, tree, status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an appointment first.")
            return

        values = tree.item(selected[0], "values")
        appointment_id = values[0]
        
        if not messagebox.askyesno("Confirm Status Change", f"Do you want to change the status of Appointment ID {appointment_id} to {status}?"):
            return

        conn = self.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT user_id, fullname FROM tbl_appointment WHERE id = %s", (appointment_id,))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Appointment not found.")
                    return

                user_id, appointment_fullname = result
                email = None
                
                if user_id is None:
                    cursor.execute("SELECT id, email FROM tbl_users WHERE fullname = %s", (appointment_fullname,))
                    user_result = cursor.fetchone()
                    if user_result:
                        user_id, email = user_result
                        cursor.execute("UPDATE tbl_appointment SET user_id=%s WHERE id=%s", (user_id, appointment_id))
                    else:
                        messagebox.showwarning("Warning", "No linked user found with that full name. Status updated, but no email sent.")
                        email = None
                else:
                    cursor.execute("SELECT email FROM tbl_users WHERE id=%s", (user_id,))
                    email = cursor.fetchone()[0]

                cursor.execute("UPDATE tbl_appointment SET status=%s WHERE id=%s", (status, appointment_id))
                conn.commit()
                messagebox.showinfo("Success", f"Appointment status changed to {status} successfully!")
                
                if email:
                    self.send_decision_email(email, appointment_fullname, status)
                
                self.show_appointments_panel()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update appointment: {e}")
            finally:
                cursor.close()
                conn.close()

    def send_decision_email(self, email, name, decision):
        subject = f"Your Appointment has been {decision}"
        text_body = f"Hello {name},\n\nYour appointment has been {decision}.\n\nService: {self.get_appointment_details(email)['service']}\nDate: {self.get_appointment_details(email)['appointment_date']}\nTime: {self.get_appointment_details(email)['time']}\n\nRegards,\nMarmu Barber & Tattoo Shop"

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = YOUR_GMAIL
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(text_body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(YOUR_GMAIL, YOUR_APP_PASSWORD)
            server.sendmail(YOUR_GMAIL, email, msg.as_string())
            print(f"✅ Email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
        finally:
            if 'server' in locals() and server:
                server.quit()

    def get_appointment_details(self, email):
        conn = self.get_db_connection()
        if not conn: return {}
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM tbl_users WHERE email = %s", (email,))
            user_id_result = cursor.fetchone()
            if not user_id_result:
                return {}
            user_id = user_id_result['id']
            
            cursor.execute("SELECT service, appointment_date, time FROM tbl_appointment WHERE user_id = %s ORDER BY appointment_date DESC, time DESC LIMIT 1", (user_id,))
            return cursor.fetchone() or {}
        except Exception as e:
            print(f"Error fetching appointment details for email: {e}")
            return {}
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()

    def show_feedback_panel(self):
        self.clear_content()

        # Main container with scrollable canvas
        main_container = tk.Frame(self.content_frame, bg="#212121")
        main_container.pack(fill="both", expand=True)

        tk.Label(main_container, text="User Feedback Management", bg="#212121", fg="#FFFFFF",
                font=("Arial", 18, "bold")).pack(pady=(20, 10))

        # Control panel frame
        control_frame = tk.Frame(main_container, bg="#212121")
        control_frame.pack(fill="x", padx=20, pady=10)

        # Filter by star rating
        tk.Label(control_frame, text="Filter by Stars:", bg="#212121", fg="white", 
                font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        star_filter = tk.StringVar(value="All")
        star_dropdown = ttk.Combobox(control_frame, textvariable=star_filter, 
                                    values=["All", "5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"],
                                    state="readonly", width=12)
        star_dropdown.pack(side="left", padx=5)

        # Sort options
        tk.Label(control_frame, text="Sort by:", bg="#212121", fg="white", 
                font=("Arial", 10)).pack(side="left", padx=(20, 5))
        
        sort_option = tk.StringVar(value="Newest First")
        sort_dropdown = ttk.Combobox(control_frame, textvariable=sort_option,
                                    values=["Newest First", "Oldest First", "Highest Rating", "Lowest Rating"],
                                    state="readonly", width=15)
        sort_dropdown.pack(side="left", padx=5)

        # Search functionality
        tk.Label(control_frame, text="Search:", bg="#212121", fg="white", 
                font=("Arial", 10)).pack(side="left", padx=(20, 5))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(control_frame, textvariable=search_var, width=20, bg="#333", 
                            fg="white", insertbackground="white")
        search_entry.pack(side="left", padx=5)

        # Scrollable feedback container
        canvas = tk.Canvas(main_container, bg="#212121", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#212121")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def load_feedback():
            # Clear existing feedback cards
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            conn = self.get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            
            # Build query based on filters
            query = """
                SELECT f.id, f.username, f.stars, f.message, COALESCE(f.reply, ''), 
                    DATE_FORMAT(f.date_submitted, '%Y-%m-%d %H:%i:%s'),
                    f.resolved, u.email
                FROM tbl_feedback f
                LEFT JOIN tbl_users u ON f.username = u.username
            """
            
            conditions = []
            params = []
            
            # Star filter
            star_val = star_filter.get()
            if star_val != "All":
                star_num = int(star_val.split()[0])
                conditions.append("f.stars = %s")
                params.append(star_num)
            
            # Search filter
            search_text = search_var.get().strip()
            if search_text:
                conditions.append("(f.username LIKE %s OR f.message LIKE %s)")
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Sort order
            sort_val = sort_option.get()
            if sort_val == "Newest First":
                query += " ORDER BY f.date_submitted DESC"
            elif sort_val == "Oldest First":
                query += " ORDER BY f.date_submitted ASC"
            elif sort_val == "Highest Rating":
                query += " ORDER BY f.stars DESC, f.date_submitted DESC"
            elif sort_val == "Lowest Rating":
                query += " ORDER BY f.stars ASC, f.date_submitted DESC"
            
            try:
                cursor.execute(query, params)
                feedbacks = cursor.fetchall()
                
                if not feedbacks:
                    tk.Label(scrollable_frame, text="No feedback found matching your filters.", 
                            bg="#212121", fg="#aaa", font=("Arial", 12)).pack(pady=50)
                else:
                    for feedback in feedbacks:
                        create_feedback_card(feedback)
                        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load feedback: {e}")
            finally:
                cursor.close()
                conn.close()

        def create_feedback_card(feedback):
            feedback_id, username, stars, message, reply, date, resolved, email = feedback
            
            # Card frame
            card = tk.Frame(scrollable_frame, bg="#333", bd=2, relief="solid", padx=15, pady=12)
            card.pack(pady=10, fill="x", padx=10)
            
            # Header frame (username, email, date, resolved status)
            header_frame = tk.Frame(card, bg="#333")
            header_frame.pack(fill="x", pady=(0, 5))
            
            tk.Label(header_frame, text=username, fg="white", bg="#333", 
                    font=("Arial", 12, "bold")).pack(side="left")
            
            if email:
                tk.Label(header_frame, text=f"({email})", fg="#aaa", bg="#333", 
                        font=("Arial", 9)).pack(side="left", padx=(5, 0))
            
            tk.Label(header_frame, text=date, fg="#888", bg="#333", 
                    font=("Arial", 9)).pack(side="right")
            
            # Resolved badge
            if resolved:
                resolved_badge = tk.Label(header_frame, text="✓ RESOLVED", fg="#28A745", bg="#333", 
                                        font=("Arial", 9, "bold"))
                resolved_badge.pack(side="right", padx=(0, 10))
            
            # Star rating
            star_frame = tk.Frame(card, bg="#333")
            star_frame.pack(fill="x", pady=3)
            star_text = "★" * stars + "☆" * (5 - stars)
            tk.Label(star_frame, text=star_text, fg="gold", bg="#333", 
                    font=("Arial", 16)).pack(side="left")
            
            # Message
            tk.Label(card, text=message, fg="white", bg="#333", font=("Arial", 11),
                    wraplength=650, justify="left", anchor="w").pack(fill="x", pady=8)
            
            # Admin reply section (if exists)
            if reply:
                reply_frame = tk.Frame(card, bg="#1a1a1a", bd=1, relief="solid", padx=10, pady=8)
                reply_frame.pack(fill="x", pady=(5, 0))
                
                tk.Label(reply_frame, text="Admin Response:", fg="#00BFFF", bg="#1a1a1a",
                        font=("Arial", 10, "bold")).pack(anchor="w")
                tk.Label(reply_frame, text=reply, fg="white", bg="#1a1a1a",
                        font=("Arial", 10), wraplength=630, justify="left", 
                        anchor="w").pack(anchor="w", pady=(3, 0))
            
            # Action buttons
            btn_frame = tk.Frame(card, bg="#333")
            btn_frame.pack(fill="x", pady=(10, 0))
            
            # Reply button
            reply_btn = tk.Button(btn_frame, text="💬 Reply" if not reply else "✏️ Edit Reply",
                                command=lambda: reply_to_feedback(feedback_id, username, message, 
                                                                stars, reply, email),
                                bg="#007ACC", fg="white", relief="flat", 
                                activebackground="#005bb5", font=("Arial", 9))
            reply_btn.pack(side="left", padx=(0, 5))
            
            # Mark as resolved/unresolved button
            resolve_text = "❌ Mark Unresolved" if resolved else "✅ Mark Resolved"
            resolve_btn = tk.Button(btn_frame, text=resolve_text,
                                command=lambda: toggle_resolved(feedback_id, not resolved),
                                bg="#28A745" if not resolved else "#FFC107", 
                                fg="white", relief="flat",
                                activebackground="#1e7e34" if not resolved else "#cc9a00",
                                font=("Arial", 9))
            resolve_btn.pack(side="left", padx=5)
            
            # Delete button
            delete_btn = tk.Button(btn_frame, text="🗑️ Delete",
                                command=lambda: delete_feedback(feedback_id),
                                bg="#F44336", fg="white", relief="flat",
                                activebackground="#dc3545", font=("Arial", 9))
            delete_btn.pack(side="left", padx=5)

        def reply_to_feedback(feedback_id, username, user_message, stars, existing_reply, email):
            top = tk.Toplevel(self)
            top.title(f"Reply to {username}'s Feedback")
            top.geometry("500x550")
            top.configure(bg="#f0f0f0")
            top.transient(self)
            top.grab_set()

            # Show user's feedback
            info_frame = tk.Frame(top, bg="#e0e0e0", padx=15, pady=15)
            info_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(info_frame, text=f"User: {username}", font=("Arial", 11, "bold"), 
                    bg="#e0e0e0").pack(anchor="w")
            
            if email:
                tk.Label(info_frame, text=f"Email: {email}", font=("Arial", 9), 
                        fg="#555", bg="#e0e0e0").pack(anchor="w")
            
            star_text = "★" * stars + "☆" * (5 - stars)
            tk.Label(info_frame, text=star_text, fg="gold", bg="#e0e0e0", 
                    font=("Arial", 14)).pack(anchor="w", pady=3)
            
            tk.Label(info_frame, text="User's Feedback:", font=("Arial", 10, "bold"), 
                    bg="#e0e0e0").pack(anchor="w", pady=(5, 2))
            tk.Label(info_frame, text=user_message, font=("Arial", 10), bg="#e0e0e0",
                    wraplength=450, justify="left").pack(anchor="w")

            # Reply section
            tk.Label(top, text="Your Reply:", font=("Arial", 12, "bold"), 
                    bg="#f0f0f0").pack(pady=(10, 5), padx=15, anchor="w")
            
            reply_box = tk.Text(top, width=55, height=10, wrap="word", bg="white", 
                            font=("Arial", 10))
            reply_box.pack(pady=5, padx=15)
            
            if existing_reply:
                reply_box.insert("1.0", existing_reply)

            # Email checkbox
            send_email_var = tk.BooleanVar(value=True if email else False)
            email_check = tk.Checkbutton(top, text="Send reply via email", 
                                        variable=send_email_var, bg="#f0f0f0",
                                        font=("Arial", 10))
            email_check.pack(pady=5)
            
            if not email:
                email_check.config(state="disabled")
                tk.Label(top, text="(No email associated with this user)", 
                        fg="red", bg="#f0f0f0", font=("Arial", 8)).pack()

            def send_reply():
                reply_text = reply_box.get("1.0", tk.END).strip()
                if not reply_text:
                    messagebox.showwarning("Empty", "Reply cannot be empty.", parent=top)
                    return
                
                conn = self.get_db_connection()
                if not conn:
                    return
                    
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE tbl_feedback SET reply=%s WHERE id=%s", 
                                (reply_text, feedback_id))
                    conn.commit()
                    
                    # Send email if checkbox is checked and email exists
                    if send_email_var.get() and email:
                        self.send_feedback_reply_email(email, username, user_message, 
                                                    stars, reply_text)
                    
                    messagebox.showinfo("Success", "Reply sent successfully!", parent=top)
                    top.destroy()
                    self.show_feedback_panel()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send reply: {e}", parent=top)
                finally:
                    cursor.close()
                    conn.close()

            tk.Button(top, text="Send Reply", command=send_reply,
                    bg="#007ACC", fg="white", relief="flat", 
                    font=("Arial", 11, "bold"), pady=8).pack(pady=15, padx=15, fill="x")

        def toggle_resolved(feedback_id, new_status):
            conn = self.get_db_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE tbl_feedback SET resolved=%s WHERE id=%s", 
                            (new_status, feedback_id))
                conn.commit()
                load_feedback()  # Refresh the display
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {e}")
            finally:
                cursor.close()
                conn.close()

        def delete_feedback(feedback_id):
            if not messagebox.askyesno("Confirm Delete", 
                                    "Are you sure you want to delete this feedback?"):
                return
            
            conn = self.get_db_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM tbl_feedback WHERE id=%s", (feedback_id,))
                conn.commit()
                messagebox.showinfo("Success", "Feedback deleted successfully!")
                load_feedback()  # Refresh the display
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete feedback: {e}")
            finally:
                cursor.close()
                conn.close()

        # Apply filters button
        apply_btn = tk.Button(control_frame, text="🔍 Apply Filters", 
                            command=load_feedback, bg="#007ACC", fg="white", 
                            relief="flat", font=("Arial", 9))
        apply_btn.pack(side="left", padx=20)

        # Refresh button
        refresh_btn = tk.Button(control_frame, text="🔄 Refresh", 
                            command=lambda: [star_filter.set("All"), 
                                            sort_option.set("Newest First"),
                                            search_var.set(""),
                                            load_feedback()],
                            bg="#28A745", fg="white", relief="flat", 
                            font=("Arial", 9))
        refresh_btn.pack(side="left", padx=5)

        # Initial load
        load_feedback()

    def send_feedback_reply_email(self, email, username, user_message, stars, admin_reply):
        """Send email with user's feedback and admin's reply"""
        subject = f"Response to Your Feedback - Marmu Barber & Tattoo Shop"
        
        star_text = "★" * stars + "☆" * (5 - stars)
        
        text_body = f"""Hello {username},

    Thank you for your feedback! We appreciate you taking the time to share your thoughts with us.

    Your Feedback ({star_text}):
    "{user_message}"

    Our Response:
    {admin_reply}

    We value your opinion and hope to serve you better in the future.

    Best regards,
    Marmu Barber & Tattoo Shop Team
    """

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = YOUR_GMAIL
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(text_body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(YOUR_GMAIL, YOUR_APP_PASSWORD)
            server.sendmail(YOUR_GMAIL, email, msg.as_string())
            print(f"✅ Feedback reply email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send feedback reply email: {e}")
            messagebox.showwarning("Email Error", 
                                f"Reply saved but email failed to send: {e}")
        finally:
            if 'server' in locals() and server:
                server.quit()

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
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")