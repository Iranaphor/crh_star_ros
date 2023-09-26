class Network():

    def __init__(self, node_locations, NodeNameList, adjacency_matrix):
        self.r = rand();

        #Number of Nodes
        self.node_locations = node_locations;
        self.NodeNameList = NodeNameList;

        #Adjacency matrix
        self.adjacency_matrix = adjacency_matrix
        [x,y] = find(self.adjacency_matrix)
        aa=[x,y]'


        #Create the nodes
        self.node_list = Node("", [0,0]); #node_list(1,:) == [nodeName, xpos, ypos]
        nlr = nan(1,max(node_locations(:,1)));
        for i=1:size(node_locations,1)
            nd = node_locations(i,:);
            self.node_list(i) = Node(NodeNameList(i), nd(2:3));
            self.node_list(i).name = nd(1);
            self.node_list(i).id = i;
            nlr(nd(1)) = i;
        Net.nlr = nlr; #node_list(nlr(id),:) == node details for id

        #Identify and store the neighbour identifiers
        for i=1:size(node_locations,1)
            nom=self.node_list(i).name;
            ab=aa(:,any(aa==nom)); ac=ab(:); ac(ac==nom)=[];
            self.node_list(i).neighbour_list = self.nlr(ac);
            neigh = self.node_list(self.nlr(ac));
            for j=1:length(neigh)
                self.node_list(i).neighbourPrettyName(j)=neigh(j).name;
#                self.node_list(i).delays = zeros(1,length(neigh));
#                self.node_list(i).delayed_time = zeros(1,length(neigh));
#            for N=self.node_list
#                ab=aa(:,any(aa==N.name)); ac=ab(:); ac(ac==N.name)=[];
#                N.neighbour_list = self.nlr(ac);
        #neighbourlist is still not generating correctly,
        #O.findNode(76) lists WayPoint43, with neighbour ID 108, but
        #O.findNode(108) lists WayPoint75, not WayPoint106 which is at
        #ID 9 (found using O.findNodeByName(106))
        #43-106 is a pair in O.EER which is generated from the
        #edge_list, so the edges are being generated correctly. Thus
        #the issue lies above.

        #Create the edges
        self.edge_list = Edge(Node("",[0,0]), Node("",[0,0]));
        for j = 1:length(x)
            yj=self.nlr(y(j));
            xj=self.nlr(x(j));
            self.edge_list(j) = Edge(self.node_list(yj),...
                                     self.node_list(xj));


    def plot(self):
        hold on
        for edge = self.edge_list
           edge.Plot()

        for node = self.node_list
            node.Plot();
        hold off

        ax=gca;
        axis(ax,'off');

    def quickPlot(self):
        hold on
        self.slowPlotEdges();
        self.quickPlotNodes();
        hold off
        set(gca, 'Position', [0.05 0.05 0.9 0.9], 'visible','off');

    def slowPlotEdges(self):
        for edge = self.edge_list
           edge.Plot()

    def quickPlotNodes(self):
        scatter(self.node_locations(:,2), self.node_locations(:,3),'k','filled')

    def plotNodeNames(self):
        hold on

        for node = self.node_list
            pos = node.position;
            text(pos(1)+.3,pos(2)-.3,string(node.id),'Color',[0,0,0]);

        hold off

    def plotNodeTimes(self):
        hold on

        for node = self.node_list
            #print(node.time_from)

            pos = node.position;
            text(pos(1)-.5, pos(2)-.5, string(node.time_from),...
                "Color", [0,.7,1]);

        hold off

    def joinNodes(self, nodeID_1, nodeID_2, aid, atotal):
        hold on

        n1 = self.node_locations(nodeID_1,:);
        n2 = self.node_locations(nodeID_2,:);

        p = prism(atotal);
        plot([n1(2), n2(2)], [n1(3), n2(3)], 'Color', p(aid,:), 'LineWidth', 4)

        hold off
