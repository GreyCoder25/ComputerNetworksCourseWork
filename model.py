import random as rnd


HEADER_SIZE = 20
PACKET_SIZE = 100


class Node:

    def __init__(self, node_id=0):
        self.channels_list = []
        self.channels_queues = []
        self.connected = set([])
        self.confirmed = {}
        self.id = node_id
        self.buffer_size = 10
        self.disabled = False

    def add_channel(self, channel):
        self.channels_list.append(channel)
        self.channels_queues.append([])

    def connected(self, node):
        return node.id in self.connected

    def packet_confirmed(self, node):
        return self.confirmed[node.id]

    def reset_confirmation(self, node):
        self.confirmed[node.id] = False

    def send_packet(self, packet):
        channel, queue = min(zip(self.channels_list, self.channels_queues), key=lambda pair: len(pair[1]))
        queue.append(packet)

    def receive(self, packet, from_channel):
        if packet.destination_node == self:
            if packet.type == 'connect':
                self.accept_connection(packet.source_node)
            elif packet.type == 'accept_connection':
                self.connected.add(packet.source_node.id)
                self.confirmed[packet.source_node.id] = False
            elif packet.type == 'info':
                self.confirm(packet.source_node)
            elif packet.type == 'confirm':
                self.confirmed[packet.source_node.id] = True
            elif packet.type == 'disconnect':
                self.accept_disconnection(packet.source_node)
            elif packet.type == 'accept_disconnection':
                self.connected.remove(packet.source_node.id)
                self.confirmed.pop(packet.source_node.id)
        else:
            from_channel_index = self.channels_list.index(from_channel)
            self.channels_list.remove(from_channel)
            from_channel_queue = self.channels_queues.pop(from_channel_index)

            self.send_packet(packet)

            self.channels_list.append(from_channel)
            self.channels_queues.append(from_channel_queue)

    def connect(self, node):
        self.send_packet(Packet(self, node, 'connect'))

    def accept_connection(self, node):
        self.send_packet(Packet(self, node, 'accept_connection'))

    def confirm(self, node):
        self.send_packet(Packet(self, node, 'confirm'))

    def disconnect(self, node):
        self.send_packet(Packet(self, node, 'disconnect'))

    def accept_disconnection(self, node):
        self.send_packet(Packet(self, node, 'accept_disconnection'))

    def iteration(self):
        for channel, queue in zip(self.channels_list, self.channels_queues):
            if channel.available(self):
                if queue:
                    channel.transfer_init(self)
            else:
                if channel.transfer_finished(self):
                    channel.transfer_finish(queue.pop(0), self, channel.other_node(self))
                else:
                    channel.transfer_iteration()


CHANNEL_WEIGHTS = (2, 4, 7, 8, 11, 15, 17, 20, 24, 25, 28)


class InformationChannel:

    def __init__(self, first_node, second_node, error_prob=0.05, channel_type='duplex'):
        self.first_node = first_node
        self.second_node = second_node
        self.weight = CHANNEL_WEIGHTS[rnd.randint(0, len(CHANNEL_WEIGHTS) - 1)]
        self.transfer_time_from_first_to_second = 0
        self.transfer_time_from_second_to_first = 0
        self.error_prob = error_prob
        self.type = channel_type
        self.available_from_first_to_second = True
        self.available_from_second_to_first = True
        self.disabled = False

    def other_node(self, node):
        if node == self.first_node:
            return self.second_node
        elif node == self.second_node:
            return self.first_node

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

    def transfer_init(self, from_node):
        if from_node == self.first_node:
            self.transfer_time_from_first_to_second = self.weight
        elif from_node == self.second_node:
            self.transfer_time_from_second_to_first = self.weight
        self.set_status_for_node(from_node, False)

    def transfer_iteration(self):
        if self.transfer_time_from_first_to_second > 0:
            self.transfer_time_from_first_to_second -= 1
        if self.transfer_time_from_second_to_first > 0:
            self.transfer_time_from_second_to_first -= 1

    def transfer_finish(self, packet, from_node, to_node):
        to_node.receive(packet, self)
        self.set_status_for_node(from_node, True)

    def transfer_finished(self, from_node):
        if from_node == self.first_node and self.transfer_time_from_first_to_second == 0:
            return True
        if from_node == self.second_node and self.transfer_time_from_second_to_first == 0:
            return True
        return False


class Packet:

    def __init__(self, source_node, destination_node, packet_type, data_size=0):
        self.size = HEADER_SIZE
        self.source_node = source_node
        self.destination_node = destination_node
        if packet_type == 'info':
            self.size += data_size


class MessageTransfer:

    def __init__(self, message_size, source_node, destination_node):
        self.source_node = source_node
        self.destination_node = destination_node
        self.packets_to_send = []
        self.status = 'connecting'
        size = message_size
        data_size = PACKET_SIZE - HEADER_SIZE
        while size > 0:
            if size >= data_size:
                self.packets_to_send.append(Packet(self.source_node, self.destination_node, 'info', data_size))
                size -= data_size
            else:
                self.packets_to_send.append(Packet(self.source_node, self.destination_node, 'info', size))
                size = 0
        source_node.connect(self.destination_node)

    def iteration(self):
        if self.status == 'connecting':
            if self.source_node.connected(self.destination_node):
                self.status = 'transferring'
                if self.packets_to_send:
                    self.source_node.send(self.packets_to_send.pop(0))
        elif self.status == 'transferring':
            if self.source_node.packet_confirmed(self.destination_node):
                if self.packets_to_send:
                    self.source_node.send(self.packets_to_send.pop(0))
                    self.source_node.reset_confirmation(self.destination_node)
                else:
                    self.source_node.disconnect(self.destination_node)
                    self.status = 'disconnecting'
        elif self.status == 'disconnecting':
            if not self.source_node.connected(self.destination_node):
                self.status = 'finished'


