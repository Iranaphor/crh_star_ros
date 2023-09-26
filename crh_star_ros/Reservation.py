class Reservation():

    def __init__(self, node1, node2, time_in, time_out, agent_id, CRH, position):
        self.fromID = node1
        self.toID = node2
        self.time_in = time_in
        self.time_out = time_out
        self.agent_id = agent_id
        self.CRH = CRH
        self.position = position
        self.delayed = 0
