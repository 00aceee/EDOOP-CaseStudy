from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar 
import mysql.connector
import time
from config import *
from utils import load_image

class BookNowPage(tk.Toplevel):
    AVAILABLE_TIMES = [
        "09:00", "10:00", "11:00", "12:00", 
        "13:00", "14:00", "15:00", "16:00", "17:00"
    ]

    def __init__(self, parent, username, is_admin=False):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        
        self.fullname = self.fetch_fullname_by_username(self.username)
        if not self.fullname:
            self.fullname = self.username.capitalize()
            messagebox.showwarning("User Name Missing", f"Could not retrieve full name for '{self.username}'. Using '{self.fullname}'.")

        self.title("Book an Appointment")
        self.geometry("600x500")
        self.after(0, self.center_window)
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        title = tk.Label(self, text="Book Your Appointment", font=("Arial", 20, "bold"),
                         fg="white", bg=BG_COLOR)
        title.pack(pady=20)

        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(pady=10)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Full Name:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.name_entry = tk.Entry(form_frame, font=("Arial", 12), fg="black", bg="#333", insertbackground="white")
        self.name_entry.grid(row=0, column=1, pady=10, padx=10, sticky="we")

        self.name_entry.insert(0, self.fullname)
        self.name_entry.config(state="readonly", disabledbackground="#222", disabledforeground=FG_COLOR)


        tk.Label(form_frame, text="Service:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.service_combo = ttk.Combobox(form_frame, values=["Haircut", "Tattoo"], width=37, state="readonly", font=("Arial", 12))
        self.service_combo.grid(row=1, column=1, pady=10, padx=10, sticky="we")
        
        tk.Label(form_frame, text="Date:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=10, padx=10)
        
        date_control_frame = tk.Frame(form_frame, bg=BG_COLOR)
        date_control_frame.grid(row=2, column=1, pady=10, padx=10, sticky="we")
        date_control_frame.columnconfigure(0, weight=1)

        self.date_entry = tk.Entry(date_control_frame, state="readonly", font=("Arial", 12), fg="black", bg="#333", insertbackground="white")
        self.date_entry.grid(row=0, column=0, sticky="we", padx=(0, 5)) 

        date_btn = tk.Button(date_control_frame, text="📅 Pick Date", command=self.open_calendar_popup, 
                             bg=ACCENT_COLOR, fg="black", relief="flat", font=("Arial", 10, "bold"))
        date_btn.grid(row=0, column=1, sticky="e")
        
        tk.Label(form_frame, text="Time:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).grid(row=3, column=0, sticky="w", pady=10, padx=10)
        
        self.time_combo = ttk.Combobox(form_frame, width=37, state="readonly", font=("Arial", 12))
        self.time_combo.grid(row=3, column=1, pady=10, padx=10, sticky="we")
        self.date_entry.bind('<<DateSelected>>', self.update_available_times)

        self.time_combo['values'] = ["- Select a Date First -"]
        self.time_combo.set("- Select a Date First -")

        tk.Label(form_frame, text="Additional Remarks:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).grid(row=4, column=0, sticky="nw", pady=10, padx=10)
        self.remarks_text = tk.Text(form_frame, width=30, height=4, font=("Arial", 12), fg="black", bg="white", insertbackground="black")
        self.remarks_text.grid(row=4, column=1, pady=10, padx=10, sticky="we")
        self.remarks_text.bind('<Return>', lambda event: (self.confirm_booking(), "break")[1])

        submit_btn = tk.Button(self, text="Confirm Booking", font=("Arial", 12, "bold"),
                               bg=ACCENT_COLOR, fg="black", relief="flat", padx=10, pady=8,
                               command=self.confirm_booking)
        submit_btn.pack(pady=30)
        self.bind('<Return>', lambda event: self.confirm_booking())

        back_btn = tk.Button(self, text="← Back", font=("Arial", 12),
                             bg="#555", fg="white", relief="flat", padx=10, pady=5,
                             command=self.go_back)
        back_btn.pack(pady=5)
        back_btn.place(x=10, y=450)

    def fetch_fullname_by_username(self, username):
        """Fetches the user's full name from tbl_users using their username."""
        fullname = None
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="marmudb"
            )
            cursor = conn.cursor()
            query = "SELECT fullname FROM tbl_users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if result:
                fullname = result[0]
                
        except mysql.connector.Error as err:
            print(f"Database error fetching user data for {username}: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        
        return fullname

    def center_window(self):
        width = 600
        height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def open_calendar_popup(self):
        """Opens a top-level window with the Calendar widget for date selection."""
        top = tk.Toplevel(self)
        top.title("Select Date")
        
        today = date.today()
        cal = Calendar(top, 
                       selectmode='day',
                       date_pattern='yyyy-mm-dd',
                       mindate=today)
        cal.pack(padx=10, pady=10)

        def set_date():
            selected_date = cal.get_date()
            self.date_entry.config(state=tk.NORMAL)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, selected_date)
            self.date_entry.config(state="readonly")
            
            self.update_available_times() 
            top.destroy()

        tk.Button(top, text="Select", command=set_date, bg=ACCENT_COLOR, fg="white").pack(pady=10)

    def get_booked_times(self, selected_date):
        """Fetches all booked times for a specific date from the database."""
        booked_times = []
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="marmudb"
            )
            cursor = conn.cursor()
            
            query = "SELECT time FROM tbl_appointment WHERE appointment_date = %s"
            cursor.execute(query, (selected_date,))
            
            for (time_str,) in cursor.fetchall():
                
                if isinstance(time_str, time.struct_time):
                    
                    booked_times.append(time.strftime("%H:%M", time_str))
                elif len(time_str) > 5 and time_str[2] == ':':
                    booked_times.append(time_str[:5])
                else:
                    booked_times.append(time_str)
                    
        except mysql.connector.Error as err:
            print(f"Database error fetching booked times: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        
        return [t.strip() for t in booked_times]


    def update_available_times(self, event=None):
        """Calculates and sets the available time slots in the combobox."""
        selected_date = self.date_entry.get()
        
        if not selected_date:
            self.time_combo['values'] = ["- Select a Date First -"]
            self.time_combo.set("- Select a Date First -")
            return
            
        booked_times = self.get_booked_times(selected_date)
        
        available_times = [
            t for t in self.AVAILABLE_TIMES if t not in booked_times
        ]

        if available_times:
            self.time_combo['values'] = available_times
            self.time_combo.set(available_times[0])
            self.time_combo.config(state="readonly")
        else:
            self.time_combo['values'] = ["- NO SLOTS AVAILABLE -"]
            self.time_combo.set("- NO SLOTS AVAILABLE -")
            self.time_combo.config(state="disabled") 

    def go_back(self):
        from main_window import MainWindow
        self.withdraw()
        main_win = MainWindow(self.parent, username=self.username, is_admin=self.is_admin)
        main_win.grab_set()

    def confirm_booking(self):
        name = self.name_entry.get().strip()
        service = self.service_combo.get().strip()
        date_val = self.date_entry.get().strip()
        time_val = self.time_combo.get().strip()
        remarks = self.remarks_text.get("1.0", tk.END).strip()

        if not service or not date_val or not time_val or time_val in ["- Select a Date First -", "- NO SLOTS AVAILABLE -"]:
            messagebox.showerror("Missing Info", "Service, Date, and a valid Time must be selected.")
            return

        
        booked = self.get_booked_times(date_val)
        if time_val in booked:
            messagebox.showerror("Booking Conflict", f"The slot {time_val} on {date_val} was just booked. Please select another time.")
            self.update_available_times()
            return

        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="marmudb"
            )
            cursor = conn.cursor()
            query = "INSERT INTO tbl_appointment (fullname, service, appointment_date, time, remarks) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, service, date_val, time_val, remarks))
            conn.commit()

            messagebox.showinfo("Booking Confirmed", f"Thank you {name}, your {service} is booked for {date_val} at {time_val}.")
            
            self.service_combo.set("")
            self.date_entry.config(state=tk.NORMAL)
            self.date_entry.delete(0, tk.END)
            self.date_entry.config(state="readonly")
            self.time_combo.set("- Select a Date First -")
            self.time_combo['values'] = ["- Select a Date First -"]
            self.remarks_text.delete('1.0', tk.END) 
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to save booking: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
