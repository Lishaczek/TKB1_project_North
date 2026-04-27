import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# Zákaz .pyc souborů
sys.dont_write_bytecode = True
IMAGE_FOLDER = "images"

VYCHOZI_STAV = {
    "navstiveno": {}, 
    "pouzite_volby": set(), 
    "promenne": {"pokusy": 0, "rozhlizeni": 0} 
}

class NorthGame:
    def __init__(self, root, scenes_data):
        self.root = root
        self.scenes = scenes_data
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.img_dir = os.path.join(self.script_dir, IMAGE_FOLDER)

        self.state = VYCHOZI_STAV.copy()
        self.state["pouzite_volby"] = set()
        
        self.current_pil_image = None
        self.current_tk_image = None
        self.v_menu = True
        self.hud_visible = False
        self.full_text = ""
        self.typing_job = None
        self.is_typing = False

        self.setup_ui()
        self.bind_events()
        self.show_main_menu()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.story_label = tk.Label(
            self.root, text="", fg="white", bg="#0a0a0a",
            justify="left", anchor="nw", font=("Verdana", 14), cursor="hand2"
        )
        self.story_label.bind("<Button-1>", lambda e: self.skip_typing())
        self.btn_cnt = tk.Frame(self.root, bg="#0a0a0a")
        self.menu_frame = tk.Frame(self.root, bg="#111111", padx=40, pady=40)

    def bind_events(self):
        self.root.bind("<Configure>", lambda e: self.redraw())
        self.root.bind_all("<Key>", self.handle_keypress)

    def animate_text(self, text, index):
        if index <= len(text):
            self.story_label.config(text=text[:index])
            # RYCHLOST: 10 ms
            self.typing_job = self.root.after(10, lambda: self.animate_text(text, index + 1))
        else:
            self.finish_typing()

    def skip_typing(self):
        if self.is_typing:
            if self.typing_job: self.root.after_cancel(self.typing_job)
            self.finish_typing()

    def finish_typing(self):
        self.is_typing = False
        self.story_label.config(text=self.full_text)
        self.redraw()

    def show_scene(self, scene_id, reaction="", custom_text=None):
        scene_data = self.scenes.get(scene_id)
        if not scene_data: return

        self.load_scene_image(scene_data["image"])
        
        # Zpracování textu
        main_txt = custom_text(self.state) if callable(custom_text) else (custom_text or scene_data["text"])
        react_txt = reaction(self.state) if callable(reaction) else reaction

        if react_txt:
            self.full_text = f"{react_txt.upper()}\n\n{main_txt}"
        else:
            self.full_text = main_txt

        for w in self.btn_cnt.winfo_children(): w.destroy()
        self.btn_cnt.place_forget()
        self.is_typing = True
        self.animate_text(self.full_text, 0)

        btn_opt = {
            "bg": "#1a1a1a", "fg": "#cccccc", "relief": "flat", 
            "font": ("Verdana", 11), "pady": 12, "cursor": "hand2",
            "activebackground": "#333333", "activeforeground": "white"
        }

        for ch in scene_data["choices"]:
            if ch["once"] and ch["cid"] in self.state["pouzite_volby"]: continue
            if ch.get("condition") and not ch["condition"](self.state): continue

            tk.Button(
                self.btn_cnt, text=ch["label"],
                command=lambda c=ch: self.handle_choice(c),
                **btn_opt
            ).pack(fill="x", pady=5)

        self.redraw()

    def handle_choice(self, choice_data):
        if choice_data["once"]: self.state["pouzite_volby"].add(choice_data["cid"])
        if choice_data["action"]: choice_data["action"](self.state)
        self.show_scene(choice_data["target"], 
                        reaction=choice_data["reaction"], 
                        custom_text=choice_data.get("custom_text"))

    def redraw(self):
        """Responzivní výpočty s dynamickým paddingem."""
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w <= 1 or h <= 1: return

        if self.current_pil_image:
            img_w, img_h = self.current_pil_image.size
            ratio = max(w / img_w, h / img_h)
            nw, nh = int(img_w * ratio), int(img_h * ratio)
            bg = self.current_pil_image.resize((nw, nh), Image.LANCZOS)
            x, y = (nw - w) // 2, (nh - h) // 2
            self.current_tk_image = ImageTk.PhotoImage(bg.crop((x, y, x + w, y + h)))
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.current_tk_image)

        if not self.v_menu and self.hud_visible:
            hud_h = int(h * 0.3)
            right_w = int(w * 0.3)
            
            # DYNAMICKÝ PADDING: 4 % šířky/výšky okna
            px = int(w * 0.04)
            py = int(h * 0.04)
            
            self.canvas.create_rectangle(0, h - hud_h, w, h, fill="#0a0a0a", outline="")
            
            # Label se umístí s dynamickým paddingem
            self.story_label.place(x=px, y=h - hud_h + py, width=w - right_w - (2 * px), height=hud_h - (2 * py))
            self.story_label.config(wraplength=w - right_w - (2 * px))
            
            if not self.is_typing:
                self.btn_cnt.place(x=w - right_w - px, y=h - hud_h + py, width=right_w, height=hud_h - (2 * py))
        elif self.v_menu:
            self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.story_label.place_forget()
            self.btn_cnt.place_forget()

    def load_scene_image(self, filename):
        path = os.path.join(self.img_dir, filename)
        if os.path.exists(path):
            self.current_pil_image = Image.open(path).convert("RGB")
            self.redraw()

    def show_main_menu(self):
        self.v_menu, self.hud_visible = True, False
        self.load_scene_image("title_screen.png")
        for w in self.menu_frame.winfo_children(): w.destroy()
        tk.Label(self.menu_frame, text="N O R T H", fg="white", bg="#111111", font=("Verdana", 40, "bold")).pack(pady=20)
        tk.Button(self.menu_frame, text="Spustit hru", command=self.start_game, bg="#333333", fg="white", font=("Verdana", 12), padx=20, pady=10).pack()
        self.redraw()

    def start_game(self):
        self.v_menu, self.hud_visible = False, True
        self.menu_frame.place_forget()
        self.show_scene("plan")

    def handle_keypress(self, event):
        k = event.keysym.lower()
        if k == "h": self.hud_visible = not self.hud_visible; self.redraw()
        elif k == "escape": self.root.destroy()

if __name__ == "__main__":
    from scenes import SCENES
    root = tk.Tk()
    root.title("North: FrostBound Adventure")
    root.geometry("1280x720")
    NorthGame(root, SCENES)
    root.mainloop()