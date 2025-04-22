import tkinter as tk
from PIL import Image, ImageDraw
import os


class DrawingTool:
    def __init__(self, width=800, height=600):
        self.root = tk.Tk()
        self.root.title("Python Drawing Tool")

        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.pack()

        # Tools
        self.setup_toolbar()

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.last_x, self.last_y = None, None
        self.color = "black"
        self.line_width = 2
        self.drawing = False

    def setup_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X)

        colors = ["black", "red", "blue", "green", "yellow"]
        for color in colors:
            btn = tk.Button(toolbar, bg=color, width=3, command=lambda c=color: self.set_color(c))
            btn.pack(side=tk.LEFT, padx=2)

        tk.Scale(toolbar, from_=1, to=10, orient=tk.HORIZONTAL,
                 command=lambda val: self.set_line_width(val)).pack(side=tk.LEFT)

        tk.Button(toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Save", command=self.save_drawing).pack(side=tk.LEFT)

    def set_color(self, color):
        self.color = color

    def set_line_width(self, width):
        self.line_width = int(width)

    def draw(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.line_width, fill=self.color, capstyle=tk.ROUND, smooth=True
            )
        self.last_x, self.last_y = event.x, event.y

    def reset(self, event):
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        self.canvas.delete("all")

    def save_drawing(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension=".png")
        if filename:
            # Convert canvas to image
            self.canvas.postscript(file="tmp.eps", colormode="color")
            img = Image.open("tmp.eps")
            img.save(filename, "PNG")
            os.remove("tmp.eps")

    def run(self):
        self.root.mainloop()


# Example usage:
if __name__ == "__main__":
    app = DrawingTool()
    app.run()