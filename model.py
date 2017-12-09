import random as rnd
from dijkstra import *

HEADER_SIZE = 20
PACKET_SIZE = 100


class Graph:

    def __init__(self):
        self.edges = []

    def add_edge(self, v1, v2, weight):
        self.edges.append((v1, v2, weight))
        self.edges.append((v2, v1, weight))

    def remove_edge(self, v1, v2):
        to_delete = []
        for edge in self.edges:
            if (edge[0], edge[1]) == (v1, v2) or (edge[0], edge[1]) == (v2, v1):
                to_delete.append(edge)

        for edge in to_delete:
            self.edges.remove(edge)

    def remove_vertex(self, v):
        to_delete = []
        for edge in self.edges:
            if edge[0] == v or edge[1] == v:
                to_delete.append(edge)

        for edge in to_delete:
            self.edges.remove(edge)

    def shortest_path(self, v1, v2):
        cost, tmp = dijkstra(self.edges, v1, v2)
        path = [tmp[0]]
        while tmp[1]:
            tmp = tmp[1]
            path.append(tmp[0])

        return cost, list(reversed(path))

    # def test(self):
    #     self.add_edge(1, 2, 7)
    #     self.add_edge(1, 3, 9)
    #     self.add_edge(1, 6, 14)
    #     self.add_edge(2, 3, 10)
    #     self.add_edge(2, 4, 15)
    #     self.add_edge(3, 4, 11)
    #     self.add_edge(3, 6, 2)
    #     self.add_edge(5, 4, 6)
    #     self.add_edge(5, 6, 9)
    #
    #     print(self.shortest_path(1, 4))

network_graph = Graph()


class RoutingTableRecord:

    def __init__(self, time, next_node):
        self.time = time
        self.next_node = next_node


def update_routing_tables(nodes_list):



class Node:

    def __init__(self, node_id=0):
        self.channels_list = []
        self.channels_queues = []
        self.connected_nodes = set([])
        self.routing_table = None
        self.confirmed = {}
        self.id = node_id
        self.buffer_size = 10
        self.disabled = False
        print('New node with id %d created' % self.id)

    def add_channel(self, channel):
        self.channels_list.append(channel)
        self.channels_queues.append([])

    def connected(self, node):
        return node.id in self.connected_nodes

    def packet_confirmed(self, node):
        return self.confirmed[node.id]

    def reset_confirmation(self, node):
        self.confirmed[node.id] = False

    def send_packet(self, packet):
        print('Node %d send %s-packet from %d to %d'% (self.id, packet.type, packet.source_node.id,
                                                       packet.destination_node.id))
        channel, queue = min(zip(self.channels_list, self.channels_queues), key=lambda pair: len(pair[1]))
        queue.append(packet)

    def receive(self, packet, from_channel):
        print('Node %d receiving %s-packet from %d to %d ' % (self.id, packet.type, packet.source_node.id,
                                                              packet.destination_node.id))
        if packet.destination_node == self:
            if packet.type == 'connect':
                self.accept_connection(packet.source_node)
            elif packet.type == 'accept_connection':
                self.connected_nodes.add(packet.source_node.id)
                self.confirmed[packet.source_node.id] = False
            elif packet.type == 'info':
                self.confirm(packet.source_node)
            elif packet.type == 'confirm':
                self.confirmed[packet.source_node.id] = True
            elif packet.type == 'disconnect':
                self.accept_disconnection(packet.source_node)
            elif packet.type == 'accept_disconnection':
                self.connected_nodes.remove(packet.source_node.id)
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
        # print('Node %d iteration' % self.id)
        for channel, queue in zip(self.channels_list, self.channels_queues):
            if channel.available(self):
                if queue:
                    channel.transfer_init(self, queue[0])
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
        # self.weight = CHANNEL_WEIGHTS[rnd.randint(0, len(CHANNEL_WEIGHTS) - 1)]
        self.weight = 5
        self.transfer_time_from_first_to_second = 0
        self.transfer_time_from_second_to_first = 0
        self.packet_from_first_to_second = None
        self.packet_from_second_to_first = None
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

    def transfer_init(self, from_node, packet):
        print('Channel from %d to %d transfer_init' % (from_node.id, self.other_node(from_node).id))
        if from_node == self.first_node:
            self.transfer_time_from_first_to_second = self.weight
            self.packet_from_first_to_second = packet
        elif from_node == self.second_node:
            self.transfer_time_from_second_to_first = self.weight
            self.packet_from_second_to_first = packet
        self.set_status_for_node(from_node, False)

    def transfer_iteration(self):
        if self.transfer_time_from_first_to_second > 0:
            self.transfer_time_from_first_to_second -= 1
            print('Channel from %d to %d transfer_iteration %d' % (self.first_node.id, self.second_node.id,
                                                                   self.weight - self.transfer_time_from_first_to_second))
        if self.transfer_time_from_second_to_first > 0:
            self.transfer_time_from_second_to_first -= 1
            print('Channel from %d to %d transfer_iteration %d' % (self.second_node.id, self.first_node.id,
                                                                   self.weight - self.transfer_time_from_second_to_first))

    def transfer_finish(self, packet, from_node, to_node):
        print('Channel from %d to %d transfer_finish' % (from_node.id, to_node.id))
        to_node.receive(packet, self)
        self.set_status_for_node(from_node, True)
        if from_node == self.first_node:
            self.packet_from_first_to_second = None
        elif from_node == self.second_node:
            self.packet_from_second_to_first = None

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
        self.type = packet_type
        if self.type == 'info':
            self.size += data_size


class MessageTransferWithConnection:

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
        self.source_node.connect(self.destination_node)
        print('New message transfer with message size %d created' % message_size)

    def iteration(self):
        # print('Iteration')
        if self.status == 'connecting':
            if self.source_node.connected(self.destination_node):
                self.status = 'transferring'
                if self.packets_to_send:
                    self.source_node.send_packet(self.packets_to_send.pop(0))
        elif self.status == 'transferring':
            if self.source_node.packet_confirmed(self.destination_node):
                if self.packets_to_send:
                    self.source_node.send_packet(self.packets_to_send.pop(0))
                    self.source_node.reset_confirmation(self.destination_node)
                else:
                    self.source_node.disconnect(self.destination_node)
                    self.status = 'disconnecting'
        elif self.status == 'disconnecting':
            if not self.source_node.connected(self.destination_node):
                self.status = 'finished'


