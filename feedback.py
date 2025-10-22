import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import *
from datetime import datetime

class Feedback(tk.Toplevel):
    def __init__(self, parent, username, is_admin=False, mode="dark"):
        super().__init__(parent)
        self.username = username
        self.is_admin = is_admin
        self.mode = mode
        self.title("Feedback Form")
        self.geometry("700x600")
        self.configure(bg="#222")

        # 🧾 Create scrollable canvas for ENTIRE form
        self.canvas = tk.Canvas(self, bg="#222", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#222")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Now add all content to scrollable_frame instead of self
        
        # 🌟 Title
        tk.Label(self.scrollable_frame, text="Rate Our Service", fg="white", bg="#222",
                 font=("Arial", 18, "bold")).pack(pady=10)

        # ⭐ Interactive Stars
        self.rating = 0
        self.stars_frame = tk.Frame(self.scrollable_frame, bg="#222")
        self.stars_frame.pack(pady=10)
        self.stars = []
        for i in range(1, 6):
            lbl = tk.Label(self.stars_frame, text="☆", font=("Arial", 40), fg="gray", bg="#222", cursor="hand2")
            lbl.pack(side="left", padx=5)
            lbl.bind("<Enter>", lambda e, x=i: self.preview_stars(x))
            lbl.bind("<Leave>", lambda e: self.preview_stars(self.rating))
            lbl.bind("<Button-1>", lambda e, x=i: self.set_rating(x))
            self.stars.append(lbl)

        # 💬 Feedback Input
        tk.Label(self.scrollable_frame, text="Your Feedback:", fg="white", bg="#222", font=("Arial", 12)).pack(pady=(20, 5))
        
        # Create a frame to center the text widget
        input_frame = tk.Frame(self.scrollable_frame, bg="#222")
        input_frame.pack(pady=5)
        
        self.message_entry = tk.Text(input_frame, width=60, height=6, wrap="word", bg="#333", fg="white", insertbackground="white")
        self.message_entry.pack()

        # ✅ Submit Button
        tk.Button(self.scrollable_frame, text="Submit Feedback", command=self.submit_feedback,
                  bg="#007ACC", fg="white", relief="flat", font=("Arial", 12), width=20).pack(pady=15)

        # 📜 Label
        tk.Label(self.scrollable_frame, text="User Reviews", fg="#aaa", bg="#222",
                 font=("Arial", 12, "bold")).pack(pady=(20, 5))

        # 🧾 Container for feedback cards
        self.feedback_container = tk.Frame(self.scrollable_frame, bg="#222")
        self.feedback_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_feedback()

    def _on_mousewheel(self, event):
        """Enable mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # 🌟 Star Rating Methods
    def preview_stars(self, count):
        for i, lbl in enumerate(self.stars, start=1):
            lbl.config(text="★" if i <= count else "☆", fg="gold" if i <= count else "gray")

    def set_rating(self, value):
        self.rating = value
        self.preview_stars(self.rating)

    # 🗄️ Database Connection
    def db_connect(self):
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

    # ✅ Submit Feedback
    def submit_feedback(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        stars = self.rating

        if stars == 0 or not message:
            messagebox.showwarning("Incomplete", "Please rate and write a message.")
            return

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tbl_users WHERE username = %s", (self.username,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "User not found in database.")
                return
            user_id = result[0]

            cursor.execute("""
                INSERT INTO tbl_feedback (user_id, username, stars, message)
                VALUES (%s, %s, %s, %s)
            """, (user_id, self.username, stars, message))
            conn.commit()

            messagebox.showinfo("Success", "Thank you for your feedback!")
            self.message_entry.delete("1.0", tk.END)
            self.rating = 0
            self.preview_stars(0)
            self.load_feedback()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to submit feedback:\n{e}")
        finally:
            if conn:
                conn.close()

    # 🧾 Load Feedback as Cards (Shopee-style)
    def load_feedback(self):
        for widget in self.feedback_container.winfo_children():
            widget.destroy()

        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, stars, message, COALESCE(reply, ''), 
                       DATE_FORMAT(date_submitted, '%Y-%m-%d %H:%i:%s')
                FROM tbl_feedback
                ORDER BY date_submitted DESC
            """)

            for username, stars, message, reply, date in cursor.fetchall():
                self.create_feedback_card(username, stars, message, reply, date)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load feedback: {e}")
        finally:
            if conn:
                conn.close()

    def create_feedback_card(self, username, stars, message, reply, date):
        # 🪧 Card frame with fixed width to match text entry
        card = tk.Frame(self.feedback_container, bg="#333", bd=1, relief="solid", padx=15, pady=10)
        card.pack(pady=8)
        
        # Set fixed width to match the Text widget
        card_width = 485  # Matches 60-char Text widget

        # 🧾 Username + Date
        tk.Label(card, text=username, fg="white", bg="#333", font=("Arial", 11, "bold"), width=60, anchor="w").pack(fill="x")
        tk.Label(card, text=date, fg="#aaa", bg="#333", font=("Arial", 9), width=60, anchor="w").pack(fill="x")

        # ⭐ Star rating
        star_text = "★" * stars + "☆" * (5 - stars)
        tk.Label(card, text=star_text, fg="gold", bg="#333", font=("Arial", 14), width=60, anchor="w").pack(fill="x", pady=3)

        # 💬 Message
        msg_label = tk.Label(card, text=message, fg="white", bg="#333", font=("Arial", 11),
                wraplength=450, justify="left", anchor="w")
        msg_label.pack(fill="x", pady=5)

        # 🛠️ Admin Reply (if any)
        if reply.strip():
            reply_frame = tk.Frame(card, bg="#222", padx=10, pady=6)
            reply_frame.pack(fill="x", pady=(5, 0))
            tk.Label(reply_frame, text="Seller Response:", fg="#00BFFF", bg="#222",
                    font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
            tk.Label(reply_frame, text=reply, fg="white", bg="#222",
                    font=("Arial", 10), wraplength=420, justify="left", anchor="w").pack(fill="x")