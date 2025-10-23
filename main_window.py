# main_window.py
import tkinter as tk
from tkinter import ttk
from config import * 
from utils import load_image
from book_now import BookNowPage
from tattoo_designs import TattooDesigns
from haircut_styles import HaircutStyles

class MainWindow(tk.Toplevel):
    open_sub_windows = [] 
    current_mode = "dark" 
    
    def __init__(self, parent, username, is_admin=False): 
        super().__init__(parent)
        self.profile_menu_instance = None
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        
        self.title("Barber and Tattoo Shop")
        self.geometry("1000x700") 
        self.after(0, self.center_window)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if self.current_mode == "dark":
            desc_fg_initial = "white"
            button_bg_initial = "#444"
        else:
            desc_fg_initial = "#333"
            button_bg_initial = "#E0E0E0" 

        self.nav_frame = tk.Frame(self, bg=CARD_COLOR, height=60)
        self.nav_frame.grid(row=0, column=0, sticky="ew") 
        
        self.main_frame = tk.Frame(self, bg=BG_COLOR)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.scrollable_frame.grid_columnconfigure(0, weight=1) 
        
        self.logo_img_ref = load_image(LOGO_FILE_LOGIN, 50, 50)
        
        if self.logo_img_ref:
            self.logo_label = tk.Label(self.nav_frame, image=self.logo_img_ref, bg=CARD_COLOR)
            self.logo_label.pack(side="left", padx=15, pady=5)
        else:
            self.logo_label = tk.Label(self.nav_frame, text="[LOGO]", fg=FG_COLOR, bg=CARD_COLOR, font=("Arial", 12, "bold"))
            self.logo_label.pack(side="left", padx=15)

        self.menu_frame = tk.Frame(self.nav_frame, bg=CARD_COLOR)
        self.menu_frame.pack(side="left", expand=True)

        if is_admin:
            nav_items = {
                "Book Now": self.open_book_now,
                "Tattoo Designs": self.open_tattoo_designs,
                "Haircut Styles": self.open_haircut_styles,
                "Dashboard": self.back_to_admin,
            }
        else:
            nav_items = {
                "Book Now": self.open_book_now,
                "Tattoo Designs": self.open_tattoo_designs,
                "Haircut Styles": self.open_haircut_styles,
                "Feedback": self.open_feedback,
            }
        
        self.nav_buttons = []
        for item, command in nav_items.items():
            nav_btn = tk.Label(self.menu_frame, text=item, fg="white", bg=CARD_COLOR,
                               font=("Arial", 12, "bold"), padx=20, cursor="hand2")
            nav_btn.pack(side="left", padx=10, pady=15)
            self.nav_buttons.append(nav_btn)
            
            nav_btn.bind("<Enter>", lambda e, btn=nav_btn: btn.config(bg=ACCENT_COLOR))
            nav_btn.bind("<Leave>", lambda e, btn=nav_btn: btn.config(bg=CARD_COLOR))
            nav_btn.bind("<Button-1>", lambda e, cmd=command: cmd())

        self.profile_btn = tk.Button(self.nav_frame, text="👤", command=self.open_profile_menu,
                                     fg=FG_COLOR, bg=CARD_COLOR, font=("Arial", 16),
                                     relief="flat", width=3, cursor="hand2", activebackground=ACCENT_COLOR)
        self.profile_btn.pack(side="right", padx=10)

        self.banner_frame = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
        self.banner_frame.grid(row=0, column=0, sticky="ew", pady=20) 
        self.banner_frame.grid_columnconfigure(0, weight=1) 
        
        self.banner_img_ref = load_image(LOGO_FILE_MAIN, 400, 200)
        banner_img = self.banner_img_ref
        
        if banner_img:
            self.banner_label = tk.Label(self.banner_frame, image=banner_img, bg=BG_COLOR)
            self.banner_label.pack()
        else:
            self.title_label = tk.Label(self.banner_frame, text="MARMU BARBER & TATTOO SHOP",
                                 font=("Times New Roman", 32, "bold"), fg=FG_COLOR, bg=BG_COLOR)
            self.title_label.pack()
            self.subtitle_label = tk.Label(self.banner_frame, text="Since 2022",
                                     font=("Arial", 14), fg=ACCENT_COLOR, bg=BG_COLOR)
            self.subtitle_label.pack()

        self.feature_container = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
        self.feature_container.grid(row=1, column=0, sticky="ew", padx=20, pady=40)
        self.feature_widgets = []
        self.add_feature(
            self.feature_container, 
            row=0, 
            title="Cuts That Define Confidence", 
            desc="Confidence begins with a fresh cut. Our expert barbers\nare dedicated to crafting the perfect style for you.",
            button_text="See Haircut Styles", 
            button_command=self.open_haircut_styles,
            image_file=SAMPLE_HAIRCUT, 
            image_side="left", 
            desc_fg=desc_fg_initial, 
            button_bg=button_bg_initial
        )
        
        self.add_feature(
            self.feature_container, 
            row=1, 
            title="Art That Stays With You", 
            desc="From intricate linework to bold custom pieces,\nour tattoos tell stories that last forever. Consult with our artists.",
            button_text="Explore Tattoo Designs", 
            button_command=self.open_tattoo_designs,
            image_file=SAMPLE_TATTOO, 
            image_side="right",
            desc_fg=desc_fg_initial, 
            button_bg=button_bg_initial
        )
        
        self.footer_frame = tk.Frame(self.scrollable_frame, bg=CARD_COLOR, height=80)
        self.footer_frame.grid(row=2, column=0, sticky="ew", pady=20) 
        
        self.footer_logo_ref = load_image(LOGO_FILE_LOGIN, 120, 40)
        if self.footer_logo_ref:
            self.footer_logo_label = tk.Label(self.footer_frame, image=self.footer_logo_ref, bg=CARD_COLOR)
            self.footer_logo_label.pack(pady=5)
        else:
            self.footer_logo_label = tk.Label(self.footer_frame, text="[LOGO]", fg="white", bg=CARD_COLOR, font=("Arial", 12, "bold"))
            self.footer_logo_label.pack(pady=5)

        self.footer_label = tk.Label(self.footer_frame, text="Barber Ink © 2022",
                                     font=("Arial", 10), fg="gray", bg=CARD_COLOR)
        self.footer_label.pack(pady=5)
        
        self.profile_menu_instance = None
        
        self.apply_theme()

    def apply_theme(self):
        if self.current_mode == "dark":
            bg = BG_COLOR_DARK
            card = CARD_COLOR_DARK
            fg = FG_COLOR_DARK
            button_bg = "#444"
            button_fg = "white"
            desc_fg = "white"
        else:
            bg = BG_COLOR_LIGHT
            card = CARD_COLOR_LIGHT
            fg = FG_COLOR_LIGHT
            button_bg = "#E0E0E0" # Correcting to the light mode button background
            button_fg = "black"
            desc_fg = "#333"

        self.configure(bg=bg)
        self.main_frame.config(bg=bg)
        self.canvas.config(bg=bg)
        self.scrollable_frame.config(bg=bg)
        self.feature_container.config(bg=bg)

        self.nav_frame.config(bg=card)
        self.menu_frame.config(bg=card)
        self.profile_btn.config(fg=fg, bg=card, activebackground=ACCENT_COLOR)
        if hasattr(self, 'logo_label'):
            self.logo_label.config(bg=card)

        for btn in self.nav_buttons:
            btn.config(bg=card, fg=fg)
            btn.bind("<Leave>", lambda e, b=btn, c=card: b.config(bg=c))

        self.banner_frame.config(bg=bg)
        if hasattr(self, 'banner_label'):
            self.banner_label.config(bg=bg)
        elif hasattr(self, 'title_label'):
            self.title_label.config(bg=bg, fg=fg)
            self.subtitle_label.config(bg=bg, fg=ACCENT_COLOR)

        for widget in self.feature_widgets:
            if isinstance(widget, tk.Frame):
                widget.config(bg=bg)
            elif isinstance(widget, tk.Label):
                if "bold" in widget.cget("font"):
                    widget.config(bg=bg, fg=ACCENT_COLOR)
                elif "Image" in widget.cget("text"):
                    widget.config(bg="gray", fg=fg)
                else:
                    widget.config(bg=bg, fg=desc_fg)
            elif isinstance(widget, tk.Button):
                widget.config(bg=button_bg, fg=button_fg, activebackground=ACCENT_COLOR_DARK)
                # Rebind the Leave event with the current theme's button_bg
                widget.bind("<Leave>", lambda e, b=widget, c=button_bg: b.config(bg=c))

        self.footer_frame.config(bg=card)
        self.footer_logo_label.config(bg=card)
        self.footer_label.config(bg=card, fg="gray" if self.current_mode == "dark" else "#333")

        self.canvas.update_idletasks()

    def toggle_theme(self):
        if self.current_mode == "dark":
            self.current_mode = "light"
        else:
            self.current_mode = "dark"
            
        self.apply_theme()
    
    # FIX: Added 'desc_fg' and 'button_bg' to the method signature
    def add_feature(self, container, row, title, desc, button_text, button_command, image_file, image_side="left", desc_fg="white", button_bg="#444"):
        frame = tk.Frame(container, bg=BG_COLOR, pady=30)
        frame.grid(row=row, column=0, sticky="ew", columnspan=2)
        frame.grid_columnconfigure(0, weight=1) 
        frame.grid_columnconfigure(1, weight=1)

        img_ref = load_image(image_file, 400, 300)

        text_frame = tk.Frame(frame, bg=BG_COLOR)

        title_label = tk.Label(text_frame, text=title, font=("Arial", 24, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        # FIX: Use the 'desc_fg' parameter for the description label
        desc_label = tk.Label(text_frame, text=desc, font=("Arial", 14), fg=desc_fg, bg=BG_COLOR, justify="left")
        # FIX: Use the 'button_bg' parameter for the button background
        button = tk.Button(text_frame, text=button_text, command=button_command,
                            fg="white" if button_bg == "#444" else "black", # Adjust button foreground based on button background
                            bg=button_bg, relief="flat", padx=15, pady=8, cursor="hand2", activebackground=ACCENT_COLOR_DARK)

        title_label.pack(anchor="w", pady=(10, 5))
        desc_label.pack(anchor="w", pady=10)
        button.pack(anchor="w", pady=15)
        
        button.bind("<Enter>", lambda e, btn=button: btn.config(bg=ACCENT_COLOR))
        # FIX: Use the 'button_bg' parameter for the leave event
        button.bind("<Leave>", lambda e, btn=button, c=button_bg: btn.config(bg=c))

        if img_ref:
            img_label = tk.Label(frame, image=img_ref, bg=BG_COLOR)
            img_label.image = img_ref
        else:
            img_label = tk.Label(frame, text=f"[{button_text.split()[1]} Image]",
                                 font=("Arial", 14), fg=FG_COLOR, bg="gray", width=40, height=10)

        if image_side == "left":
            img_label.grid(row=0, column=0, padx=(0, 40), sticky="w")
            text_frame.grid(row=0, column=1, padx=20, sticky="w")
        else:
            text_frame.grid(row=0, column=0, padx=20, sticky="e")
            img_label.grid(row=0, column=1, padx=(40, 0), sticky="e")
            
        self.feature_widgets.extend([frame, text_frame, title_label, desc_label, button, img_label])

    def on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def center_window(self):
        width = 1000
        height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def open_profile_menu(self):
        from user_profile_menu import UserProfileMenu

        if self.profile_menu_instance is not None and self.profile_menu_instance.winfo_exists():
            self.profile_menu_instance.destroy()
            self.profile_menu_instance = None
        else:
            self.profile_menu_instance = UserProfileMenu(
                self,
                self.username,
                self.current_mode,
                self.toggle_theme,
                self.logout
            )

    def _on_mousewheel(self, event):
        """Enable mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def back_to_admin(self):
        from admin_window import AdminWindow
        self.withdraw() 
        admin_win = AdminWindow(self, self.username, is_admin=self.is_admin)
        self.open_sub_windows.append(admin_win)
        admin_win.grab_set()

    def on_close(self):
        self.destroy_all_windows()
        self.parent.destroy()
    
    def open_tattoo_designs(self):
        self.withdraw()
        sub_win = TattooDesigns(self, self.username, is_admin=self.is_admin, mode=self.current_mode)
        self.open_sub_windows.append(sub_win)
    
    def open_haircut_styles(self):
        self.withdraw()
        sub_win = HaircutStyles(self, self.username, is_admin=self.is_admin, mode=self.current_mode)
        self.open_sub_windows.append(sub_win)

    def open_feedback(self):
        from feedback import Feedback
        self.withdraw()
        feed_win = Feedback(self, self.username, is_admin=self.is_admin, mode=self.current_mode)
        self.open_sub_windows.append(feed_win)
        feed_win.grab_set()

    def open_book_now(self):
        self.withdraw()
        sub_win = BookNowPage(self, self.username, is_admin=self.is_admin, mode=self.current_mode)
        self.open_sub_windows.append(sub_win)
        
    def destroy_all_windows(self):
        for win in self.open_sub_windows:
            if win.winfo_exists():
                win.destroy()
        self.open_sub_windows = []

    def logout(self):
        self.destroy_all_windows()
        if self.profile_menu_instance and self.profile_menu_instance.winfo_exists():
            self.profile_menu_instance.destroy()
            
        self.destroy() 
        if hasattr(self.parent, 'clear_login_fields'):
            self.parent.clear_login_fields()
        self.parent.deiconify()