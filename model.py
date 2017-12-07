import random as rnd


HEADER_SIZE = 20
PACKET_SIZE = 100


class Node:

    def __init__(self, node_id=0):
        self.channels_list = []
        self.channels_queues = []
        # self.routing_table = []
        self.id = node_id
        self.buffer_size = 10
        self.disabled = False
        # self.send_packets_counter = 0
        # self.received_packets_counter = 0

    def add_channel(self, channel):
        self.channels_list.append(channel)
        self.channels_queues.append([])

    def send(self, packet):
        channel, queue = min(zip(self.channels_list, self.channels_queues), key=lambda pair: len(pair[1]))
        queue.append(packet)

    def receive(self, packet, from_channel):
        from_channel_index = self.channels_list.index(from_channel)
        self.channels_list.remove(from_channel)
        from_channel_queue = self.channels_queues.pop(from_channel_index)

        # to process all possible situation
        # if packet.destination_node == self:
        #     if packet.type == ''
        #     self.confirm()

        self.channels_list.append(from_channel)
        self.channels_queues.append(from_channel_queue)

    def connect(self, node):
        self.send(Packet(self, node, 'connect'))

    def accept_connection(self, node):
        self.send(Packet(self, node, 'accept_connection'))

    def confirm(self, node):
        self.send(Packet(self, node, 'confirm'))

    def disconnect(self, node):
        self.send(Packet(self, node, 'disconnect'))

    def accept_disconnection(self, node):
        self.send(Packet(self, node, 'accept_disconnection'))


CHANNEL_WEIGHTS = (2, 4, 7, 8, 11, 15, 17, 20, 24, 25, 28)


class InformationChannel:

    def __init__(self, first_node, second_node, error_prob=0.05, channel_type='duplex'):
        self.first_node = first_node
        self.second_node = second_node
        self.weight = CHANNEL_WEIGHTS[rnd.randint(0, len(CHANNEL_WEIGHTS) - 1)]
        self.transfer_time_left = self.weight
        self.error_prob = error_prob
        self.type = channel_type
        self.available_from_first_to_second = True
        self.available_from_second_to_first = True
        self.disabled = False

    def available(self, node):
        if node == self.first_node and self.available_from_first_to_second:
            return True
        if node == self.second_node and self.available_from_second_to_first:
            return True
        return False

    def set_status_for_node(self, node, status):
        if self.type == 'half-duplex':
            self.available_from_first_to_second = status
            self.available_from_second_to_first = status
        else:
            if node == self.first_node:
                self.available_from_first_to_second = status
            elif node == self.second_node:
                self.available_from_second_to_first = status

    def transfer_iteration(self, packet, from_node, to_node):
        if self.transfer_time_left == self.weight:
            self.set_status_for_node(from_node, False)
        if self.transfer_time_left > 1:
            self.transfer_time_left -= 1
        else:
            to_node.receive(packet, self)
            self.set_status_for_node(from_node, True)


class Packet:

    def __init__(self, source_node, destination_node, packet_type, data_size=0):
        self.size = HEADER_SIZE
        self.source_node = source_node
        self.destination_node = destination_node
        if packet_type == 'info':
            self.size += data_size
