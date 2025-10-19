import tkinter as tk
from tkinter import ttk
from config import * 
from utils import load_image
from book_now import BookNowPage
from tattoo_designs import TattooDesigns
from haircut_styles import HaircutStyles
from feedback import Feedback

class MainWindow(tk.Toplevel):

    def __init__(self, parent, username, is_admin=False): 
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.is_admin = is_admin
        
        self.title("Barber and Tattoo Shop")
        self.geometry("1000x700") 
        self.after(0, self.center_window)
        self.configure(bg=BG_COLOR)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.grid(row=0, column=0, sticky="nsew") 

        canvas = tk.Canvas(main_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.bind('<Configure>', self.on_canvas_resize)
        
        scrollable_frame.grid_columnconfigure(0, weight=1) 
        
        nav_frame = tk.Frame(scrollable_frame, bg=CARD_COLOR, height=60)
        nav_frame.grid(row=0, column=0, sticky="ew") 

        self.logo_img_ref = load_image(LOGO_FILE_LOGIN, 50, 50)
        logo_img = self.logo_img_ref
        
        if logo_img:
            logo_label = tk.Label(nav_frame, image=logo_img, bg=CARD_COLOR)
            logo_label.pack(side="left", padx=15, pady=5)
        else:
            tk.Label(nav_frame, text="[LOGO]", fg=FG_COLOR, bg=CARD_COLOR, font=("Arial", 12, "bold")).pack(side="left", padx=15)

        menu_frame = tk.Frame(nav_frame, bg=CARD_COLOR)
        menu_frame.pack(side="left", expand=True)

        if is_admin:
            nav_items = {
                "Book Now": lambda: self.open_book_now(),
                "Tattoo Designs": lambda: self.open_tattoo_designs(),
                "Haircut Styles": lambda: self.open_haircut_styles(),
                "Dashboard": lambda: self.back_to_admin(),
                "Logout": lambda: self.logout() 
            }
        else:
            nav_items = {
            "Book Now": lambda: self.open_book_now(),
            "Tattoo Designs": lambda: self.open_tattoo_designs(),
            "Haircut Styles": lambda: self.open_haircut_styles(),
            "Feedback": lambda: self.open_feedback(),
            "Logout": lambda: self.logout() 
            }
        
        for item, command in nav_items.items():
            nav_btn = tk.Label(menu_frame, text=item, fg="white", bg=CARD_COLOR,
                font=("Arial", 12, "bold"), padx=20, cursor="hand2")
            nav_btn.pack(side="left", padx=10, pady=15)
            nav_btn.bind("<Button-1>", lambda e, cmd=command: cmd())

        banner_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        banner_frame.grid(row=1, column=0, sticky="ew", pady=20) 
        banner_frame.grid_columnconfigure(0, weight=1) 
        
        self.banner_img_ref = load_image(LOGO_FILE_MAIN, 400, 200)
        banner_img = self.banner_img_ref
        
        if banner_img:
            banner_label = tk.Label(banner_frame, image=banner_img, bg=BG_COLOR)
            banner_label.pack()
        else:
            title = tk.Label(banner_frame, text="MARMU BARBER & TATTOO SHOP",
                                font=("Times New Roman", 32, "bold"), fg=FG_COLOR, bg=BG_COLOR)
            title.pack()
            subtitle = tk.Label(banner_frame, text="Since 2022",
                                     font=("Arial", 14), fg=ACCENT_COLOR, bg=BG_COLOR)
            subtitle.pack()

        feature_container = tk.Frame(scrollable_frame, bg=BG_COLOR)
        feature_container.grid(row=2, column=0, sticky="ew", padx=20, pady=40)
        
        feature_container.grid_columnconfigure(0, weight=1) 
        feature_container.grid_columnconfigure(1, weight=1) 
        
        haircut_frame = tk.Frame(feature_container, bg=BG_COLOR, pady=30)
        haircut_frame.grid(row=0, column=0, columnspan=2, sticky="ew") 
        
        haircut_frame.grid_columnconfigure(0, weight=1) 
        haircut_frame.grid_columnconfigure(1, weight=1)

        self.haircut_img_ref = load_image(SAMPLE_HAIRCUT, 400, 300)
        haircut_img = self.haircut_img_ref

        if haircut_img:
            haircut_label = tk.Label(haircut_frame, image=haircut_img, bg=BG_COLOR)
            haircut_label.grid(row=0, column=0, padx=(0, 40), sticky="w") 
        else:
            haircut_label = tk.Label(haircut_frame, text="[Haircut Image]",
                                         font=("Arial", 14), fg=FG_COLOR, bg="gray", width=40, height=10)
            haircut_label.grid(row=0, column=0, padx=(0, 40), sticky="w")

        haircut_text = tk.Frame(haircut_frame, bg=BG_COLOR)
        haircut_text.grid(row=0, column=1, padx=20, sticky="e") 

        haircut_title = tk.Label(haircut_text, text="Cuts That Define Confidence",
                                     font=("Arial", 24, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        haircut_title.pack(anchor="w", pady=(10, 5))

        haircut_desc = tk.Label(haircut_text, text="Confidence begins with a fresh cut. Our expert barbers\n"
                                                      "are dedicated to crafting the perfect style for you.",
                                     font=("Arial", 14), fg="white", bg=BG_COLOR, justify="left")
        haircut_desc.pack(anchor="w", pady=10)

        see_haircut_btn = tk.Button(haircut_text, text="See Haircut Styles", font=("Arial", 12, "bold"),
                                         fg="white", bg="#444", relief="flat", padx=15, pady=8)
        see_haircut_btn.pack(anchor="w", pady=15)

        tattoo_frame = tk.Frame(feature_container, bg=BG_COLOR, pady=30)
        tattoo_frame.grid(row=1, column=0, columnspan=2, sticky="ew") 
        
        tattoo_frame.grid_columnconfigure(0, weight=1) 
        tattoo_frame.grid_columnconfigure(1, weight=1) 

        tattoo_text = tk.Frame(tattoo_frame, bg=BG_COLOR)
        tattoo_text.grid(row=0, column=0, padx=20, sticky="w") 

        tattoo_title = tk.Label(tattoo_text, text="Art That Stays With You",
                                     font=("Arial", 24, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        tattoo_title.pack(anchor="w", pady=(10, 5))

        tattoo_desc = tk.Label(
            tattoo_text,
            text="From intricate linework to bold custom pieces,\n"
                  "our tattoos tell stories that last forever. Consult with our artists.",
            font=("Arial", 14), fg=FG_COLOR, bg=BG_COLOR, justify="left"
        )
        tattoo_desc.pack(anchor="w", pady=10)

        explore_tattoo_btn = tk.Button(tattoo_text, text="Explore Tattoo Designs", font=("Arial", 12, "bold"),
                                         fg="white", bg="#444", relief="flat", padx=15, pady=8)
        explore_tattoo_btn.pack(anchor="w", pady=15)

        self.tattoo_img_ref = load_image(SAMPLE_TATTOO, 400, 300)
        tattoo_img = self.tattoo_img_ref
        
        if tattoo_img:
            tattoo_label = tk.Label(tattoo_frame, image=tattoo_img, bg=BG_COLOR)
            tattoo_label.grid(row=0, column=1, padx=(40, 0), sticky="e")
        else:
            tattoo_label = tk.Label(tattoo_frame, text="[Tattoo Image]",
                                         font=("Arial", 14), fg=FG_COLOR, bg="gray", width=40, height=10)
            tattoo_label.grid(row=0, column=1, padx=(40, 0), sticky="e")

        footer_frame = tk.Frame(scrollable_frame, bg=CARD_COLOR, height=80)
        footer_frame.grid(row=3, column=0, sticky="ew", pady=20) 
        
        self.footer_logo_ref = load_image(LOGO_FILE_LOGIN, 120, 40)
        footer_logo = self.footer_logo_ref
        
        if footer_logo:
            footer_logo_label = tk.Label(footer_frame, image=footer_logo, bg=CARD_COLOR)
            footer_logo_label.pack(pady=5)
        else:
            footer_logo_label = tk.Label(footer_frame, text="[LOGO]", fg="white", bg=CARD_COLOR, font=("Arial", 12, "bold"))
            footer_logo_label.pack(pady=5)

        footer = tk.Label(footer_frame, text="Barber Ink © 2022",
                             font=("Arial", 10), fg="gray", bg=CARD_COLOR)
        footer.pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_canvas_resize(self, event):
        self.children['!frame'].children['!canvas'].itemconfig(self.canvas_window, width=event.width)

    def center_window(self):
        width = 1000
        height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def back_to_admin(self):
        from admin_window import AdminWindow
        self.withdraw() 
        admin_win = AdminWindow(self, self.username, is_admin=self.is_admin)
        admin_win.grab_set()

    def on_close(self):
        self.destroy()
        self.parent.destroy()
    
    def open_tattoo_designs(self):
        self.withdraw()
        TattooDesigns(self, self.username, is_admin=self.is_admin)
    
    def open_haircut_styles(self):
        self.withdraw()
        HaircutStyles(self, self.username, is_admin=self.is_admin)

    def open_feedback(self):
        self.withdraw()
        Feedback(self, self.username, is_admin=self.is_admin)

    def open_book_now(self):
        self.withdraw()
        BookNowPage(self, self.username, is_admin=self.is_admin) 
        
    def logout(self):
        self.destroy() 
        if hasattr(self.parent, 'clear_login_fields'):
            self.parent.clear_login_fields()
        self.parent.deiconify()