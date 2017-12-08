# import matplotlib as mpl
# mpl.use("TkAgg")
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import model


class NodeView:

    def __init__(self, x, y, node, canvas):
        self.x = x
        self.y = y
        self.radius = 15
        self.node = node
        self.color = 'white'
        self.outline = 'gray'
        self.active_color = 'cyan'
        self.disabled_color = 'black'
        self.activeoutline = self.active_color
        self.width = 2
        self.canvas = canvas
        self.highlighted = False
        self.draw()
        self.set_user_controls()
        self.selected_for_creating_channel_view = False
        self.channel_views_list = []

    def draw(self):
        x1 = self.x - self.radius
        x2 = self.x + self.radius
        y1 = self.y - self.radius
        y2 = self.y + self.radius
        self.image = self.canvas.create_oval(x1, y1, x2, y2, tag='node', outline=self.outline,
                                             activeoutline=self.activeoutline, width=self.width, fill=self.color,
                                             activefill=self.active_color)
        self.text = self.canvas.create_text(self.x, self.y, font=("Arial", 10), text=str(self.node.id))

    def move(self, event):
        self.canvas.move(self.image, event.x - self.x, event.y - self.y)
        self.canvas.move(self.text, event.x - self.x, event.y - self.y)
        for channel_view in self.channel_views_list:
            if (channel_view.x1, channel_view.y1) == (self.x, self.y):
                self.canvas.coords(channel_view.image, event.x, event.y, channel_view.x2, channel_view.y2)
                channel_view.x1 = event.x
                channel_view.y1 = event.y
            elif (channel_view.x2, channel_view.y2) == (self.x, self.y):
                self.canvas.coords(channel_view.image, channel_view.x1, channel_view.y1, event.x, event.y)
                channel_view.x2 = event.x
                channel_view.y2 = event.y
        self.x = event.x
        self.y = event.y

    def select(self, event):
        if self.highlighted:
            self.canvas.itemconfig(self.image, fill=self.color, outline=self.outline)
            self.highlighted = False
        else:
            self.canvas.itemconfig(self.image, fill=self.active_color, outline=self.activeoutline)
            self.highlighted = True

    def select_for_creating_channel_view(self, event):
        self.highlighted = True
        if self.selected_for_creating_channel_view:
            self.selected_for_creating_channel_view = False
            self.canvas.itemconfig(self.image, outline=self.activeoutline, fill=self.active_color)
        else:
            self.selected_for_creating_channel_view = True
            self.canvas.itemconfig(self.image, outline='red', fill=self.active_color)

    def delete(self):
        for channel_view in self.channel_views_list:
            channel_view.highlighted = True
        self.canvas.delete(self.image)
        self.canvas.delete(self.text)

    def deactivate(self):
        if self.node.disabled:
            self.node.disabled = False
            self.color = self.color
            self.active_color = self.active_color
        else:
            self.node.disabled = True
            self.color = self.disabled_color
            self.active_color = self.disabled_color
        self.canvas.itemconfig(self.image, fill=self.active_color)

    def set_user_controls(self):
        self.canvas.tag_bind(self.image, '<B1-Motion>', self.move)
        self.canvas.tag_bind(self.image, '<Button-1>', self.select)
        self.canvas.tag_bind(self.image, '<Button-3>', self.select_for_creating_channel_view)

    def add_channel_view(self, channel_view):
        self.channel_views_list.append(channel_view)
        self.node.add_channel(channel_view.channel)

    def delete_channel_view(self, channel_view):
        self.node.channels_list.remove(channel_view.channel)
        self.channel_views_list.remove(channel_view)


class InformationChannelView:

    def __init__(self, nodes, channel, canvas):
        self.adjacent_nodes = list(nodes)
        node1, node2 = self.adjacent_nodes
        self.x1 = node1.x
        self.y1 = node1.y
        self.x2 = node2.x
        self.y2 = node2.y
        self.channel = channel
        self.canvas = canvas
        self.color = 'gray'
        self.active_color = 'red'
        self.disabled_color = 'black'
        self.current_color = self.color
        self.width = 2
        self.active_width = 3
        self.highlighted = False
        self.arrow = 'last'
        self.draw()
        self.set_user_controls()

    def draw(self):
        if self.channel.type == 'duplex':
            self.arrow = 'both'
        self.image = self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, arrow=self.arrow,
                                             fill=self.current_color, activefill=self.active_color,
                                             width=self.width, activewidth=self.active_width)

    def select(self, event):
        if self.highlighted:
            self.canvas.itemconfig(self.image, fill=self.color, width=self.width)
            self.highlighted = False
        else:
            self.canvas.itemconfig(self.image, fill=self.active_color, width=self.active_width)
            self.highlighted = True

    def change_type(self):
        if self.highlighted:
            if self.channel.type == 'duplex':
                self.channel.type = 'half-duplex'
                self.canvas.itemconfigure(self.image, arrow='last')
            else:
                self.channel.type = 'duplex'
                self.canvas.itemconfigure(self.image, arrow='both')

    def delete(self):
        for node in self.adjacent_nodes:
            node.delete_channel_view(self)
        self.canvas.delete(self.image)

    def deactivate(self):
        if self.channel.disabled:
            self.channel.disabled = False
            self.color = self.color
            self.active_color = self.active_color
        else:
            self.channel.disabled = True
            self.color = self.disabled_color
            self.active_color = self.disabled_color

    def set_user_controls(self):
        self.canvas.tag_bind(self.image, '<Button-1>', self.select)


class PacketView:

    def __init__(self, x, y, packet, canvas, packet_id):
        self.x = x
        self.y = y
        self.height = 10
        self.width = 16
        self.packet = packet
        self.canvas = canvas
        self.id = packet_id

    def draw(self):
        x0, x1, y0, y1 = self.x - self.width/2, self.x + self.width/2, self.y - self.height/2, self.y + self.height/2
        self.image = self.canvas.create_rectangle(x0, y0, x1, y1, fill='blue')
        self.text = self.canvas.create_text(self.x, self.y, font=("Arial", 10), color='white', text=str(self.packet.id))


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
        self.new_node_id = 0
        self.new_packet_id = 0
        self.nodes_set = set([])
        self.nodes_dict = {}
        self.channel_views_set = set([])
        self.messages = []
        self.channel_view_creating = False
        self.canvas.bind('<Double-Button-1>', self.new_node)
        self.canvas.bind('<1>', lambda event: self.canvas.focus_set())
        self.canvas.bind('d', self.delete_elements)
        self.canvas.bind('t', self.change_channels_type)
        self.canvas.bind('<Button-3>', self.new_channel)
        self.canvas.bind('s', self.deactivate_elements)

        # self.canvas.create_line(10, 10, 50, 50, arrow='last')
        # self.send_message(0)

        next_iteration_button = tk.Button(self, text="Next iteration", command=self.next_iteration)
        next_iteration_button.pack(side='left')
        quit_button = tk.Button(self, text="Quit", command=self.quit)
        quit_button.pack(side='right')
        menu = tk.Entry(self)
        menu.pack(side='top')
        menu.bind('<Return>', lambda event: self.fetch(menu))

    def new_node(self, event):
        new_node = NodeView(event.x, event.y, model.Node(self.new_node_id), self.canvas)
        self.nodes_set.add(new_node)
        self.nodes_dict[self.new_node_id] = new_node.node
        self.new_node_id += 1

    def delete_elements(self, event):
        elements_to_delete = []
        for element in self.nodes_set:
            if element.highlighted:
                element.delete()
                elements_to_delete.append(element)
        # don't process in union with self.nodes_set to let some things happen before
        for element in self.channel_views_set:
            if element.highlighted:
                element.delete()
                elements_to_delete.append(element)

        for element in elements_to_delete:
            if element in self.nodes_set:
                self.nodes_set.remove(element)
            elif element in self.channel_views_set:
                self.channel_views_set.remove(element)

    def deactivate_elements(self, event):
        for element in self.nodes_set.union(self.channel_views_set):
            if element.highlighted:
                element.deactivate()

    def change_channels_type(self, event):
        for channel_view in self.channel_views_set:
            if channel_view.highlighted:
                channel_view.change_type()

    def new_channel(self, event):
        nodes_for_channel = []
        for node in self.nodes_set:
            if node.selected_for_creating_channel_view:
                if node not in nodes_for_channel:
                    nodes_for_channel.append(node)
        if len(nodes_for_channel) == 2:
            first_node, second_node = nodes_for_channel
            new_channel_view = InformationChannelView((first_node, second_node),
                                                 model.InformationChannel(first_node.node, second_node.node),
                                                 self.canvas)
            self.channel_views_set.add(new_channel_view)
            first_node.select_for_creating_channel_view(event)
            first_node.select(event)
            first_node.add_channel_view(new_channel_view)
            second_node.select_for_creating_channel_view(event)
            second_node.select(event)
            second_node.add_channel_view(new_channel_view)

    def fetch(self, ent):
        command, arg1, arg2, size = ent.get().split(' ')
        self.send_message(int(arg1), int(arg2), int(size))

    def send_message(self, from_node_id, to_node_id, size):

        print(self.nodes_dict)
        self.messages.append(model.MessageTransfer(size, self.nodes_dict[from_node_id], self.nodes_dict[to_node_id]))

    def next_iteration(self):
        for message in self.messages:
            message.iteration()
        for node in self.nodes_dict.values():
            node.iteration()


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



