class Node:

    def __init__(self):
        self.input_channels_list = []
        self.output_channels_list = []
        self.routing_table = []
        # self.address = ''


class InformationChannel:

    def __init__(self, first_node, second_node, weight, error_prob):
        self.first_node = first_node
        self.second_node = second_node
        self.weight = weight
        self.error_prob = error_prob


class Packet:

    def __init__(self):
        pass
