class Edge():

    def __init__(self, node1, node2)
        #print(node1.id + " - " + node2.id);
        self.node1 = node1;
        self.node2 = node2;
        self.weight = sqrt(power(node1.position(1)-node2.position(1),2)...
                         + power(node1.position(2)-node2.position(2),2));

    def Plot(self)
        self.edgePlot = plot([self.node1.position[1], self.node2.position[1]],...
                             [self.node1.position[2], self.node2.position[2]],...
                             'k')

    def ChangeState(self, state)
        colours = {"closed": [1,0,0],
                   "open": [0,1,0],
                   "current":[0,0,1],
                   "null": [0,0,0],
                   "selected": [1,0,1]}
        self.edgePlot.Color = colours[state]
        #pause(.2)
