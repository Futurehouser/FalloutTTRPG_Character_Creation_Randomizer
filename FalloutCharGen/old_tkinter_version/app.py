"""Fallout 2d20 random character generator -- one button, one filled sheet."""
import os
import re
import sys
import tkinter as tk

from PIL import ImageTk

from generator import generate
from render import render


def output_dir():
    base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
    d = os.path.join(base, "Fallout Characters")
    os.makedirs(d, exist_ok=True)
    return d


def safe(s):
    return re.sub(r'[^A-Za-z0-9 _-]+', "", s).strip().replace(" ", "_") or "character"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Fallout 2d20 - Random Character Generator")
        root.configure(bg="#1a1a1a")
        root.geometry("1280x900")
        root.minsize(700, 500)

        self.btn = tk.Button(root, text="☢  GENERATE RANDOM CHARACTER  ☢", command=self.make,
                             font=("Segoe UI", 16, "bold"), bg="#f0be28", fg="#1a1a1a",
                             activebackground="#ffd54a", relief="flat", padx=24, pady=10, cursor="hand2")
        self.btn.pack(pady=(14, 6))
        self.status = tk.Label(root, text="Press the button to create a character. Sheets are saved as PNG files.",
                               font=("Segoe UI", 10), bg="#1a1a1a", fg="#cfcfcf")
        self.status.pack()
        self.canvas = tk.Label(root, bg="#1a1a1a")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.show())
        self.img = None
        self.tkimg = None
        self.path = None
        root.bind("<Return>", lambda e: self.make())
        root.bind("<space>", lambda e: self.make())

    def make(self):
        c = generate()
        self.img = render(c)
        n = 1
        while True:
            self.path = os.path.join(output_dir(), f"{safe(c.name)}_{n:03d}.png")
            if not os.path.exists(self.path):
                break
            n += 1
        self.img.save(self.path)
        self.status.config(text=f"{c.name} — {c.origin} ({c.archetype}).  Saved to: {self.path}")
        self.show()

    def show(self):
        if self.img is None:
            return
        w = max(100, self.canvas.winfo_width() - 4)
        h = max(100, self.canvas.winfo_height() - 4)
        r = min(w / self.img.width, h / self.img.height)
        prev = self.img.resize((int(self.img.width * r), int(self.img.height * r)))
        self.tkimg = ImageTk.PhotoImage(prev)
        self.canvas.config(image=self.tkimg)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # headless: python app.py --batch N  -> writes N sheets
        for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 1):
            c = generate()
            p = os.path.join(output_dir(), f"{safe(c.name)}.png")
            render(c).save(p)
            print(p, "|", c.origin, "|", c.pack, "|", c.archetype)
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()
