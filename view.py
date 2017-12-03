import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

import model

mpl.use("TkAgg")


class Node:

    def __init__(self, x, y, node_info, canvas):
        self.x = x
        self.y = y
        self.radius = 10
        self.node_info = node_info
        self.color = 'black'
        self.active_color = 'cyan'
        self.canvas = canvas
        self.highlighted = False
        self.draw()
        self.bind_moving_by_mouse()

    def draw(self):
        x1 = self.x - self.radius
        x2 = self.x + self.radius
        y1 = self.y - self.radius
        y2 = self.y + self.radius
        self.image = self.canvas.create_oval(x1, y1, x2, y2, tag='node', fill=self.color, activefill=self.active_color)

    def move(self, event):
        self.canvas.move(self.image, event.x - self.x, event.y - self.y)
        self.x = event.x
        self.y = event.y

    def bind_moving_by_mouse(self):
        self.canvas.tag_bind(self.image, '<B1-Motion>', self.move)


class ComputerNetworksModellingApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", expand=True, fill="both")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainPage, SettingsPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.canvas = tk.Canvas(width=1000, height=600, bg='white')
        self.canvas.pack(expand='YES', fill='both')

        self.nodes_list = []
        # self.canvas.create_line(200, 200, 400, 200, arrow="last", activefill='red', activewidth=2)
        self.canvas.bind('<Double-Button-1>', self.new_node)

        # node1 = Node(100, 100, model.Node(), self.canvas)
        # self.canvas.tag_bind(node1, 'B1-Motion', Node.move)

        settings_button = tk.Button(self, text="Settings", command=lambda: controller.show_frame(SettingsPage))
        settings_button.pack()

        quit_button = tk.Button(self, text="Quit", command=self.quit)
        quit_button.pack()

    def select_node(self, event):
        # for node in self.nodes_list:
        #     if
        pass

    def new_node(self, event):
        new_node = Node(event.x, event.y, model.Node(), self.canvas)
        self.nodes_list.append(new_node)


class SettingsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        main_page_button = tk.Button(self, text="Main page", command=lambda: controller.show_frame(MainPage))
        main_page_button.pack(side="right", expand=True)

        quit_button = tk.Button(self, text="Quit", command=self.quit)
        quit_button.pack(side="right", expand=True)

        self.control_panel = tk.Frame(self)
        self.control_panel_init(self.control_panel)
        self.control_panel.pack(side="left", expand=True)

    def control_panel_init(self, control_panel):
        pass



