import matplotlib as mpl
mpl.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

import model


class Node:

    def __init__(self, x, y, node_params, canvas):
        self.x = x
        self.y = y
        self.radius = 10
        self.node_info = node_params
        self.color = 'white'
        self.active_color = 'cyan'
        self.canvas = canvas
        self.highlighted = False
        self.draw()
        self.set_user_controls()
        self.selected_for_creating_channel = False

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

    def select(self, event):
        if self.highlighted:
            self.canvas.itemconfig(self.image, fill=self.color)
            self.highlighted = False
        else:
            self.canvas.itemconfig(self.image, fill=self.active_color)
            self.highlighted = True

    def select_for_creating_channel(self, event):
        self.highlighted = True
        if self.selected_for_creating_channel:
            self.selected_for_creating_channel = False
            self.canvas.itemconfig(self.image, outline='black', fill=self.active_color)
        else:
            self.selected_for_creating_channel = True
            self.canvas.itemconfig(self.image, outline='red', fill=self.active_color)

    def delete(self):
        self.canvas.delete(self.image)

    def set_user_controls(self):
        self.canvas.tag_bind(self.image, '<B1-Motion>', self.move)
        self.canvas.tag_bind(self.image, '<Button-1>', self.select)
        self.canvas.tag_bind(self.image, '<Button-3>', self.select_for_creating_channel)


class InformationChannel:

    def __init__(self, x1, y1, x2, y2, channel_params, canvas):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.channel_params = channel_params
        self.canvas = canvas
        self.color = 'black'
        self.active_color = 'red'
        self.width = 2
        self.active_width = 3
        self.highlighted = False
        self.arrow = 'last'
        self.draw()
        self.set_user_controls()

    def draw(self):
        if self.channel_params.type == 'duplex':
            self.arrow = 'both'
        self.image = self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, arrow=self.arrow,
                                             fill=self.color, activefill=self.active_color,
                                             activewidth=self.active_width)

    def select(self, event):
        if self.highlighted:
            self.canvas.itemconfig(self.image, fill=self.color, width=self.width)
            self.highlighted = False
        else:
            self.canvas.itemconfig(self.image, fill=self.active_color, width=self.active_width)
            self.highlighted = True

    def delete(self):
        self.canvas.delete(self.image)

    def set_user_controls(self):
        self.canvas.tag_bind(self.image, '<Button-1>', self.select)


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

        self.nodes_set = set([])
        self.channels_set = set([])
        self.channel_creating = False
        self.canvas.bind('<Double-Button-1>', self.new_node)
        self.canvas.bind('<1>', lambda event: self.canvas.focus_set())
        self.canvas.bind('d', self.delete_elements)
        self.canvas.bind('<Button-3>', self.new_channel)

        settings_button = tk.Button(self, text="Settings", command=lambda: controller.show_frame(SettingsPage))
        settings_button.pack()
        quit_button = tk.Button(self, text="Quit", command=self.quit)
        quit_button.pack()

    def new_node(self, event):
        new_node = Node(event.x, event.y, model.Node(), self.canvas)
        self.nodes_set.add(new_node)

    def delete_elements(self, event):
        elements_to_delete = []
        for element in self.nodes_set.union(self.channels_set):
            if element.highlighted:
                element.delete()
                elements_to_delete.append(element)

        for element in elements_to_delete:
            if element in self.nodes_set:
                self.nodes_set.remove(element)
            elif element in self.channels_set:
                self.channels_set.remove(element)

    def new_channel(self, event):
        nodes_for_channel = []
        for node in self.nodes_set:
            if node.selected_for_creating_channel:
                if node not in nodes_for_channel:
                    nodes_for_channel.append(node)
        if len(nodes_for_channel) == 2:
            first_node, second_node = nodes_for_channel
            new_channel = InformationChannel(first_node.x, first_node.y, second_node.x, second_node.y,
                                             model.InformationChannel(first_node.node_info, second_node.node_info),
                                             self.canvas)
            self.channels_set.add(new_channel)
            first_node.select_for_creating_channel(event)
            second_node.select_for_creating_channel(event)


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



