import customtkinter as ctk
from PIL import Image, ImageDraw
import subprocess
import os
import glob

# --- Window setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class HaircutStyles(ctk.CTkToplevel):
    def __init__(self , parent, username, is_admin=False):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        self.title("Haircut Styles")
        self.geometry("1000x650")
        self.configure(fg_color="#111")

        # --- Title ---
        title_label = ctk.CTkLabel(self, text="Haircut Styles", font=("Segoe UI", 28, "bold"))
        title_label.pack(pady=(30, 15))

        # --- Scrollable Frame for Haircut Cards ---
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#000")
        scrollable_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # --- Load haircut images automatically ---
        self.haircut_images = []
        self.haircut_names = []

        image_folder = "haircut_images"  # folder name
        valid_exts = ("*.png", "*.jpg", "*.jpeg")
        image_files = []
        for ext in valid_exts:
            image_files.extend(glob.glob(os.path.join(image_folder, ext)))

        if not image_files:
            print("⚠️ No images found in /images folder!")

        for path in sorted(image_files):
            name = os.path.splitext(os.path.basename(path))[0].capitalize()
            try:
                img = Image.open(path)
                img = img.resize((160, 200))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 200))
                self.haircut_images.append(ctk_img)
                self.haircut_names.append(name)
            except Exception as e:
                print(f"Error loading {path}: {e}")

        # --- Create cards in grid ---
        cols = 4
        for index, (img, name) in enumerate(zip(self.haircut_images, self.haircut_names)):
            r, c = divmod(index, cols)
            card = self.create_haircut_card(scrollable_frame, name, img)
            card.grid(row=r, column=c, padx=15, pady=15)

        # --- Book Now button ---
        book_btn = ctk.CTkButton(
            self,
            text="Book Now",
            width=150,
            height=40,
            fg_color="#444",
            hover_color="#555",
            corner_radius=8,
            command=lambda: self.open_book_now
        )
        book_btn.pack(pady=20)

    def open_book_now(self):
        from book_now import BookNowPage
        self.withdraw()
        sub_win = BookNowPage(self, self.username, is_admin=self.is_admin, mode=self.current_mode)
        self.open_sub_windows.append(sub_win)

    # --- Create haircut card with real image ---
    def create_haircut_card(self, parent, name, image):
        card_frame = ctk.CTkFrame(parent, fg_color="#111", corner_radius=10)
        img_label = ctk.CTkLabel(card_frame, image=image, text="")
        img_label.pack(padx=10, pady=(10, 5))
        name_label = ctk.CTkLabel(card_frame, text=name, font=("Segoe UI", 14, "bold"))
        name_label.pack(pady=(0, 10))
        return card_frame

    # --- Create placeholder gray image (for missing files) ---
    def create_placeholder_image(self, width, height, color, text):
        from PIL import ImageDraw
        img = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width - w) / 2, (height - h) / 2), text, fill="black")
        return ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))


# if __name__ == "__main__":
#     app = HaircutStyles()
#     app.mainloop()
