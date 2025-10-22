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

        tk.Label(self, text="Rate Our Service", fg="white", bg="#222",
                 font=("Arial", 16, "bold")).pack(pady=10)

        # ⭐ Star Rating
        self.rating = tk.IntVar(value=0)
        stars_frame = tk.Frame(self, bg="#222")
        stars_frame.pack(pady=10)
        for i in range(1, 6):
            tk.Radiobutton(stars_frame, text="⭐" * i, variable=self.rating,
                           value=i, bg="#222", fg="gold", selectcolor="#333",
                           font=("Arial", 14), indicatoron=False).pack(side="left", padx=5)

        # 💬 Message Box
        tk.Label(self, text="Your Feedback:", fg="white", bg="#222",
                 font=("Arial", 12)).pack(pady=10)
        self.message_entry = tk.Text(self, width=50, height=6, wrap="word")
        self.message_entry.pack(pady=10)

        tk.Button(self, text="Submit Feedback", command=self.submit_feedback,
                  bg="#007ACC", fg="white", relief="flat", font=("Arial", 12)).pack(pady=10)

        tk.Label(self, text="Other User Feedback", fg="#aaa", bg="#222",
                 font=("Arial", 12, "bold")).pack(pady=(20, 5))

        self.tree = ttk.Treeview(self, columns=("user", "stars", "message", "reply"), show="headings")
        for col in ("user", "stars", "message", "reply"):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100 if col != "message" else 200)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        self.load_feedback()

    def db_connect(self):
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

    def submit_feedback(self):
        stars = self.rating.get()
        message = self.message_entry.get("1.0", tk.END).strip()

        if stars == 0 or not message:
            messagebox.showwarning("Incomplete", "Please rate and write a message.")
            return

        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # Fetch user_id by username
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

            # Reset form
            self.message_entry.delete("1.0", tk.END)
            self.rating.set(0)
            self.load_feedback()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to submit feedback:\n{e}")
        finally:
            if conn:
                conn.close()

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
