class NodeInfo:

    def __init__(self, id=0):
        self.input_channels_list = []
        self.output_channels_list = []
        self.routing_table = []
        self.id = id
        self.disabled = False


class InformationChannelInfo:

    def __init__(self, first_node, second_node, weight=2, error_prob=0.0, channel_type='duplex'):
        self.first_node = first_node
        self.second_node = second_node
        self.weight = weight
        self.error_prob = error_prob
        self.type = channel_type
        self.disabled = False


class Packet:

    def __init__(self):
        pass
