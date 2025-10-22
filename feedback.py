import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import *

class Feedback(tk.Toplevel):
    def __init__(self, parent, username, is_admin=False, mode="dark"):
        super().__init__(parent)
        self.username = username
        self.is_admin = is_admin
        self.mode = mode
        self.title("Feedback Form")
        self.geometry("700x600")
        self.configure(bg="#222")

        # -----------------------------
        # 🌟 TITLE
        # -----------------------------
        tk.Label(self, text="Rate Our Service", fg="white", bg="#222",
                 font=("Arial", 18, "bold")).pack(pady=10)

        # -----------------------------
        # 🌟 STAR RATING (Interactive)
        # -----------------------------
        self.rating = 0
        self.stars_frame = tk.Frame(self, bg="#222")
        self.stars_frame.pack(pady=10)
        self.stars = []

        for i in range(1, 6):
            lbl = tk.Label(self.stars_frame, text="☆", font=("Arial", 40), fg="gray", bg="#222", cursor="hand2")
            lbl.pack(side="left", padx=5)
            lbl.bind("<Enter>", lambda e, x=i: self.preview_stars(x))
            lbl.bind("<Leave>", lambda e: self.preview_stars(self.rating))
            lbl.bind("<Button-1>", lambda e, x=i: self.set_rating(x))
            self.stars.append(lbl)

        # -----------------------------
        # 💬 FEEDBACK MESSAGE
        # -----------------------------
        tk.Label(self, text="Your Feedback:", fg="white", bg="#222",
                 font=("Arial", 12)).pack(pady=(20, 5))
        self.message_entry = tk.Text(self, width=60, height=6, wrap="word", bg="#333", fg="white", insertbackground="white")
        self.message_entry.pack(pady=5)

        # -----------------------------
        # ✅ SUBMIT BUTTON
        # -----------------------------
        tk.Button(self, text="Submit Feedback", command=self.submit_feedback,
                  bg="#007ACC", fg="white", relief="flat", font=("Arial", 12), width=20).pack(pady=15)

        # -----------------------------
        # 📜 FEEDBACK LIST
        # -----------------------------
        tk.Label(self, text="Other User Feedback", fg="#aaa", bg="#222",
                 font=("Arial", 12, "bold")).pack(pady=(20, 5))

        self.tree = ttk.Treeview(self, columns=("user", "stars", "message", "reply"), show="headings")
        for col in ("user", "stars", "message", "reply"):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100 if col != "message" else 200)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.load_feedback()

    # -----------------------------
    # ⭐ STAR LOGIC
    # -----------------------------
    def preview_stars(self, count):
        """Highlight stars on hover or after selection."""
        for i, lbl in enumerate(self.stars, start=1):
            lbl.config(text="★" if i <= count else "☆", fg="gold" if i <= count else "gray")

    def set_rating(self, value):
        """Set permanent rating when clicked."""
        self.rating = value
        self.preview_stars(self.rating)

    # -----------------------------
    # 🗄️ DATABASE
    # -----------------------------
    def db_connect(self):
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

    def submit_feedback(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        stars = self.rating

        if stars == 0 or not message:
            messagebox.showwarning("Incomplete", "Please rate and write a message.")
            return

        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # Fetch user_id using username
            cursor.execute("SELECT id FROM tbl_users WHERE username = %s", (self.username,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "User not found in database.")
                return
            user_id = result[0]

            # Insert feedback
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

    # -----------------------------
    # 📋 LOAD FEEDBACKS
    # -----------------------------
    def load_feedback(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT username, stars, message, COALESCE(reply, '') FROM tbl_feedback ORDER BY date_submitted DESC")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load feedback: {e}")
        finally:
            if conn:
                conn.close()
