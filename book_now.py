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

    def __init__(self, parent, username, is_admin=False, mode="dark"):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        self.mode = mode
        
        self.apply_theme_vars()
        
        self.fullname = self.fetch_fullname_by_username(self.username)
        if not self.fullname:
            self.fullname = self.username.capitalize()
            messagebox.showwarning("User Name Missing", f"Could not retrieve full name for '{self.username}'. Using '{self.fullname}'.")

        self.title("Book an Appointment")
        self.geometry("600x500")
        self.after(0, self.center_window)
        self.configure(bg=self.bg) 
        self.resizable(False, False)

        # CHANGE: Set back_btn background to self.bg for transparency
        back_btn = tk.Button(self, text="← Back", font=("Arial", 12),
                             bg=self.bg, fg=self.fg, relief="flat", padx=10, pady=5,
                             command=self.go_back, activebackground=self.bg, activeforeground=ACCENT_COLOR)
        back_btn.place(x=10, y=10)
        
        title = tk.Label(self, text="Book Your Appointment", font=("Arial", 20, "bold"),
                         fg=self.fg, bg=self.bg)
        title.pack(pady=(20, 25))

        form_frame = tk.Frame(self, bg=self.bg)
        form_frame.pack(pady=10, padx=20, fill='x')
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Full Name:", font=("Arial", 12), fg=self.fg, bg=self.bg).grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.name_entry = tk.Entry(form_frame, font=("Arial", 12), fg=self.entry_bg, bg=self.entry_fg, insertbackground="black", width=37)
        self.name_entry.grid(row=0, column=1, pady=10, padx=10, sticky="we")

        self.name_entry.insert(0, self.fullname)
        self.name_entry.config(state="readonly", disabledbackground=self.disabled_bg, disabledforeground=self.fg)


        tk.Label(form_frame, text="Service:", font=("Arial", 12), fg=self.fg, bg=self.bg).grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.service_combo = ttk.Combobox(form_frame, values=["Haircut", "Tattoo"], state="readonly", font=("Arial", 12))
        self.service_combo.grid(row=1, column=1, pady=10, padx=10, sticky="we")
        
        tk.Label(form_frame, text="Date:", font=("Arial", 12), fg=self.fg, bg=self.bg).grid(row=2, column=0, sticky="w", pady=10, padx=10)
        
        date_control_frame = tk.Frame(form_frame, bg=self.bg)
        date_control_frame.grid(row=2, column=1, pady=10, padx=10, sticky="we")
        date_control_frame.columnconfigure(0, weight=1)

        self.date_entry = tk.Entry(date_control_frame, 
                                  state="readonly", 
                                  font=("Arial", 12), 
                                  fg="black",  
                                  bg=self.bg,    
                                  insertbackground="black") 
        self.date_entry.grid(row=0, column=0, sticky="we", padx=(0, 5)) 

        date_btn = tk.Button(date_control_frame, text="📅 Pick Date", command=self.open_calendar_popup, 
                              bg=ACCENT_COLOR, fg="black", relief="flat", font=("Arial", 10, "bold"), activebackground=ACCENT_COLOR_DARK)
        date_btn.grid(row=0, column=1, sticky="e")
        tk.Label(form_frame, text="Time:", font=("Arial", 12), fg=self.fg, bg=self.bg).grid(row=3, column=0, sticky="w", pady=10, padx=10)
        
        self.time_combo = ttk.Combobox(form_frame, state="readonly", font=("Arial", 12))
        self.time_combo.grid(row=3, column=1, pady=10, padx=10, sticky="we")
        self.date_entry.bind('<<DateSelected>>', self.update_available_times)

        self.time_combo['values'] = ["- Select a Date First -"]
        self.time_combo.set("- Select a Date First -")

        tk.Label(form_frame, text="Remarks:", font=("Arial", 12), fg=self.fg, bg=self.bg).grid(row=4, column=0, sticky="nw", pady=10, padx=10)
        self.remarks_text = tk.Text(form_frame, width=30, height=4, font=("Arial", 12), fg=self.text_fg, bg=self.text_bg, insertbackground=self.text_fg)
        self.remarks_text.grid(row=4, column=1, pady=10, padx=10, sticky="we")
        self.remarks_text.bind('<Return>', lambda event: (self.confirm_booking(), "break")[1])
        
        submit_btn = tk.Button(self, text="Confirm Booking", font=("Arial", 14, "bold"),
                               bg=ACCENT_COLOR, fg="black", relief="flat", padx=15, pady=10,
                               command=self.confirm_booking, activebackground=ACCENT_COLOR_DARK)
        submit_btn.pack(pady=30)
        self.bind('<Return>', lambda event: self.confirm_booking())
        
        self.apply_ttk_style()


    def apply_theme_vars(self):
        if self.mode == "light":
            self.bg = BG_COLOR_LIGHT
            self.fg = FG_COLOR_LIGHT
            self.entry_bg = "#E0E0E0"
            self.entry_fg = "black"
            self.text_bg = "#E0E0E0"
            self.text_fg = "black"
            self.disabled_bg = "#C0C0C0" 
        else:
            self.bg = BG_COLOR_DARK
            self.fg = FG_COLOR_DARK
            self.entry_bg = "#333"
            self.entry_fg = "white"
            self.text_bg = "#222"
            self.text_fg = "white"
            self.disabled_bg = "#444" 
            
    def apply_ttk_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TCombobox", 
                        fieldbackground=self.entry_bg, 
                        background=self.entry_bg, 
                        foreground=self.entry_fg,
                        selectbackground=self.entry_bg,
                        selectforeground=self.entry_fg,
                        arrowsize=18,
                        relief="flat")
        style.map("TCombobox",
                  fieldbackground=[('readonly', self.entry_bg)],
                  selectbackground=[('readonly', self.entry_bg)],
                  selectforeground=[('readonly', self.entry_fg)])

    def fetch_fullname_by_username(self, username):
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
        
    def fetch_user_id_by_username(self, username):
        user_id = None
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="marmudb"
            )
            cursor = conn.cursor()
            query = "SELECT id FROM tbl_users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if result:
                user_id = result[0]
                
        except mysql.connector.Error as err:
            print(f"Database error fetching user ID for {username}: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        
        return user_id

    def center_window(self):
        width = 600
        height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def open_calendar_popup(self):
        top = tk.Toplevel(self)
        top.title("Select Date")
        
        cal_bg = self.fg
        cal_fg = self.bg
        cal_select_bg = ACCENT_COLOR
        
        today = date.today()
        cal = Calendar(top, 
                       selectmode='day',
                       date_pattern='yyyy-mm-dd',
                       mindate=today,
                       background=cal_bg, 
                       foreground=cal_fg, 
                       bordercolor=cal_fg,
                       headersbackground=cal_bg,
                       normalbackground=cal_bg,
                       selectedbackground=cal_select_bg,
                       selectedforeground='black',
                       othermonthbackground=cal_bg,
                       othermonthforeground='#888',
                       weekendbackground=cal_bg,
                       weekendforeground=cal_fg)
        cal.pack(padx=10, pady=10)

        def set_date():
            selected_date = cal.get_date()
            self.date_entry.config(state=tk.NORMAL, bg=self.entry_bg)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, selected_date)
            self.date_entry.config(state="readonly", bg=self.disabled_bg)
            
            self.update_available_times() 
            top.destroy()

        tk.Button(top, text="Select", command=set_date, bg=ACCENT_COLOR, fg="black", activebackground=ACCENT_COLOR_DARK).pack(pady=10)

    def get_booked_times(self, selected_date):
        booked_times = []
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="marmudb"
            )
            cursor = conn.cursor()
            
            query = "SELECT time FROM tbl_appointment WHERE appointment_date = %s AND status != 'Denied'"
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
        selected_date = self.date_entry.get()
        
        if not selected_date:
            self.time_combo['values'] = ["- Select a Date First -"]
            self.time_combo.set("- Select a Date First -")
            self.time_combo.config(state="disabled")
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

        user_id = self.fetch_user_id_by_username(self.username)
        if not user_id:
            messagebox.showerror("User ID Error", f"Could not fetch user ID for '{self.username}'. Booking failed.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="marmudb"
            )
            cursor = conn.cursor()
            query = """
                INSERT INTO tbl_appointment (fullname, service, appointment_date, time, user_id, remarks) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, service, date_val, time_val, user_id, remarks))
            conn.commit()

            messagebox.showinfo("Booking Confirmed", f"Thank you {name}, your {service} is booked for {date_val} at {time_val}. Your appointment status is currently PENDING.")
            
            self.service_combo.set("")
            self.date_entry.config(state=tk.NORMAL, bg=self.entry_bg)
            self.date_entry.delete(0, tk.END)
            self.date_entry.config(state="readonly", bg=self.disabled_bg)
            self.time_combo.set("- Select a Date First -")
            self.time_combo['values'] = ["- Select a Date First -"]
            self.remarks_text.delete('1.0', tk.END)
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to save booking: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()