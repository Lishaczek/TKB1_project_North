import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# 1. KYBERBEZPEČNOST: Zákaz tvorby .pyc souborů
sys.dont_write_bytecode = True

# --- KONSTANTY ---
WINDOW_W, WINDOW_H = 1280, 720
TEXTBOX_HEIGHT = 190
RIGHT_PANEL_WIDTH = 280
IMAGE_FOLDER = "images"

VYCHOZI_STAV = {
    "kapitola": 1,
    "pokusy_priblizeni": 0,
    "nikol_duvera": 0
}


class NorthGame:
    def __init__(self, root, scenes_data):
        self.root = root
        self.scenes = scenes_data

        # OPRAVA CEST: Najdeme absolutní cestu k obrázkům
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.img_dir = os.path.join(self.script_dir, IMAGE_FOLDER)

        self.state = VYCHOZI_STAV.copy()
        self.current_pil_image = None
        self.current_tk_image = None
        self.hud_visible = False
        self.v_menu = True

        self.setup_ui()
        self.bind_events()

        # Pojistka pro Linux: Vynutíme vykreslení okna před načtením menu
        self.root.update()
        self.show_main_menu()

    def setup_ui(self):
        self.canvas = tk.Canvas(
            self.root, bg="black", highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.textbox_frame = tk.Frame(
            self.root, bg="#111111", height=TEXTBOX_HEIGHT
        )
        self.left_frame = tk.Frame(self.textbox_frame, bg="#111111")
        self.left_frame.pack(
            side="left", fill="both", expand=True, padx=20, pady=15
        )

        self.story_label = tk.Label(
            self.left_frame, text="", bg="#111111", fg="#f2f2f2",
            justify="left", anchor="nw", font=("Arial", 14)
        )
        self.story_label.pack(fill="both", expand=True)

        self.right_frame = tk.Frame(
            self.textbox_frame, bg="#111111", width=RIGHT_PANEL_WIDTH
        )
        self.right_frame.pack(side="right", fill="y", padx=15, pady=15)
        self.right_frame.pack_propagate(False)

        self.menu_frame = tk.Frame(self.root, bg="#111111", padx=30, pady=30)

    def bind_events(self):
        self.root.bind("<Configure>", lambda e: self.redraw())
        # Agresivní bind pro zachycení kláves kdekoli v aplikaci
        self.root.bind_all("<Key>", self.handle_keypress)
        self.root.focus_force()

    def handle_keypress(self, event):
        """Univerzální handler pro klávesy."""
        key = event.keysym.lower()
        if key == "h":
            self.toggle_hud()
        elif key == "escape":
            self.root.destroy()

    def show_main_menu(self):
        self.v_menu = True
        self.hud_visible = False
        self.textbox_frame.place_forget()
        self.load_scene_image("title_screen.png")

        for w in self.menu_frame.winfo_children():
            w.destroy()

        tk.Label(
            self.menu_frame, text="N O R T H", fg="white", bg="#111111",
            font=("Arial", 40, "bold")
        ).pack(pady=(0, 40))

        btn_opt = {"bg": "#1b1b1b", "fg": "white", "relief": "flat",
                   "font": ("Arial", 12), "pady": 10, "cursor": "hand2"}

        tk.Button(self.menu_frame, text="Nová hra",
                  command=self.start_game, **btn_opt).pack(fill="x", pady=5)
        tk.Button(self.menu_frame, text="Ukončit",
                  command=self.root.destroy, **btn_opt).pack(fill="x", pady=5)

        self.menu_frame.lift()
        self.redraw()

    def start_game(self):
        self.v_menu = False
        self.hud_visible = True
        self.menu_frame.place_forget()
        self.state = VYCHOZI_STAV.copy()
        self.show_scene("plan")

    def show_scene(self, scene_id):
        if scene_id == "main_menu":
            self.show_main_menu()
            return

        if scene_id == "nikol_ustup":
            self.state["pokusy_priblizeni"] += 1

        scene_data = self.scenes.get(scene_id)
        if not scene_data:
            return

        self.load_scene_image(scene_data["image"])
        self.story_label.config(text=scene_data["text"])

        for w in self.right_frame.winfo_children():
            w.destroy()

        # KONTEJNER PRO VYCENTROVÁNÍ TLAČÍTEK
        btn_cnt = tk.Frame(self.right_frame, bg="#111111")
        btn_cnt.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        btn_opt = {"bg": "#1b1b1b", "fg": "white", "relief": "flat",
                   "font": ("Arial", 11), "pady": 8, "cursor": "hand2"}

        for ch in scene_data["choices"]:
            tk.Button(
                btn_cnt, text=ch["label"],
                command=lambda t=ch["target"]: self.show_scene(t),
                **btn_opt
            ).pack(fill="x", pady=4)

        u_nikol = (scene_id == "nikol_setkani")
        dost_pokusu = (self.state["pokusy_priblizeni"] >= 2)
        if u_nikol and dost_pokusu:
            tk.Button(
                btn_cnt, text="Zkusit hrabat ve sněhu",
                command=lambda: self.show_scene("nikol_hrabani"),
                **btn_opt
            ).pack(fill="x", pady=4)

        self.redraw()
        self.root.focus_set()

    def load_scene_image(self, filename):
        path = os.path.join(self.img_dir, filename)
        if os.path.exists(path):
            self.current_pil_image = Image.open(path).convert("RGB")
            self.redraw()

    def fit_image_cover(self, image, target_w, target_h):
        img_w, img_h = image.size
        ratio = max(target_w / img_w, target_h / img_h)
        nw, nh = int(img_w * ratio), int(img_h * ratio)
        resized = image.resize((nw, nh), Image.LANCZOS)
        x, y = (nw - target_w) // 2, (nh - target_h) // 2
        return resized.crop((x, y, x + target_w, y + target_h))

    def redraw(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        if w <= 1 or h <= 1:
            return

        self.canvas.delete("all")
        if self.current_pil_image:
            bg = self.fit_image_cover(self.current_pil_image, w, h)
            self.current_tk_image = ImageTk.PhotoImage(bg)
            self.canvas.create_image(0, 0, anchor="nw",
                                     image=self.current_tk_image)

        if self.v_menu:
            self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.menu_frame.lift()
        elif self.hud_visible:
            self.canvas.create_rectangle(
                0, h - TEXTBOX_HEIGHT, w, h, fill="#000000", stipple="gray50"
            )
            self.textbox_frame.place(
                x=0, y=h - TEXTBOX_HEIGHT, width=w, height=TEXTBOX_HEIGHT
            )
            self.textbox_frame.lift()
            self.story_label.config(wraplength=w - RIGHT_PANEL_WIDTH - 60)
        else:
            self.textbox_frame.place_forget()

    def toggle_hud(self):
        if not self.v_menu:
            self.hud_visible = not self.hud_visible
            self.redraw()


def main():
    from scenes import SCENES
    root = tk.Tk()
    NorthGame(root, SCENES)
    root.mainloop()


if __name__ == "__main__":
    main()