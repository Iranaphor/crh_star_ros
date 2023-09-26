class NodeExt():

    def __init__(node):
        self.node = node
        self.total_neighbours = length(self.node.neighbour_list)
        self.departure_times = zeros(self.total_neighbours,1)
        self.CRH = 0
        self.Purge()

    def id(self):
        nodeID = self.node.id
        return nodeID

    def name(self):
        nodeName = self.node.name
        return nodeName

    def Purge(self): #Most of these may be unnecessary
        self.f_cost = -1 #Score
        self.g_cost = 0 #Path Cost
        self.h_cost = -1 #Dist to target
        self.parent_id = 0

        self.arrival_time = 0 #Previously entry_time
        self.departure_time = 0
        self.departure_times = zeros(self.total_neighbours,1)

    def UpdateCosts(self, f_cost, g_cost, h_cost):
        self.f_cost = f_cost
        self.g_cost = g_cost
        self.h_cost = h_cost

    def UpdateParent(self, parent_id, CRH):
        self.parent_id = parent_id
        self.CRH = CRH

    def UpdateTimes(self, current, edge):
        dpt=current.get_departure_times(NExt.id)
        self.arrival_time = dpt + edge.time_weight
        self.departure_times = ones(self.total_neighbours,1)*self.arrival_time

    def set_departure_times(self, neighbourID, time):
        self.departure_times(self.node.neighbour_list==neighbourID) = time

    def get_departure_times(self, neighbourID):
        time = self.departure_times(self.node.neighbour_list==neighbourID)
        return time

    def setDelay(self, delay):
        self.departure_time = self.arrival_time + delay
        self.set_departure_times(current.id, self.arrival_time + delay)

    def Plot(self):
        self.nodePlot = scatter(self.node.position(1), ...
                                self.node.position(2),'k','filled')

    def ChangeState(self, state):
        colours = {"closed": [1,0,0],
                   "open": [0,1,0],
                   "current": [0,0,1],
                   "null": [0,0,0],
                   "start": [1,.5,0],
                   "target": [1,.5,0],
                   "selected": [1,0,1]}
        self.nodePlot.MarkerFaceColor = colours[state]

