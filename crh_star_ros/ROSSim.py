from crh_star_ros.Coordinator import Coordinator
from crh_star_ros.Network import Network
from crh_star_ros.Overlay import Overlay
from crh_star_ros.Agent import Agent

class ROSSim():

    #properties
    #    Agent_List = []
    #    Reservations_temp
    #    target_list



    def __init__(self, NodeList, NodeNameList, AdjacencyMatrix):
        #Setup Coordinator Map
        self.Coordinator = Coordinator(self)
        self.Coordinator.Network = Network(NodeList, NodeNameList, AdjacencyMatrix)
        self.Coordinator.Overlay = Overlay(self.Coordinator.Network)
        self.time = 0


    def Launch_Agent(self, node_id, heuristic_details):
        A = Agent(self, node_id, self.Coordinator.Network)
        A.SetupHeuristics(heuristic_details)
        A.agent_id = len(self.Agent_List)+1
        self.Agent_List = [self.Agent_List, A]


    def Launch_TaskAgent(self, node_id, heuristic_details, agent_type):
        A = Agent(self, node_id, self.Coordinator.Network)
        A.SetupHeuristics(heuristic_details)
        A.SetupTask(agent_type)
        A.agent_id = len(self.Agent_List)+1
        self.Agent_List = [self.Agent_List, A]


    def Action_getMap(self, aid): #Agent_ID
        self.Agent_List[aid].Network = self.Coordinator.Network


    def Topic_publishReservations(self, reservation_list):
        self.Coordinator.Subscribe_ReservationsUpdate(reservation_list)


        """
        This will be used to updte specific elements of the map, the
        list of changes will be encoded in a way that can offer
        consistencey.

        Before we detail the changes, we need to think about the
        specific message contents.

        To improve performance we could have it so that when updated,
        an identifier is changed, so if the map is unchanged it wouldnt
        download the same map unnecessarially.

        Extending this, we could have it so each edge has a uuid, and
        on requesting a new edge, the uuid is compared, if the uid is
        the same as the one offered, no updates are sent.

        In this same manner, we could set up a system to group regions
        of the map so bulk collections of edges are returned together
        is not identical.

        Please note, the use fo the term edge refers to the secondary
        system extending the edge class, not the edge class itself, as
        this would not change throughout the system running.
        """


    def Topic_publishFailedReservations(self, agent_id, reservation_list):
        self.Agent_List(agent_id).Replan(reservation_list)


    ## Time Step
    def TimeStep(self, t):
        newTime = self.time + t
        self.time = newTime
        print(newline + "----- ------------------------------------")
        print(newline+"Moved forward "+t+"t to timestep "+newTime)

        #purge old reservation data
        for EExt in self.Coordinator.Overlay.EdgeExtensions:
            EExt.PurgeOld(t)


        #update agent locations
        for A in self.Agent_List:
            A.UpdateLocation(newTime)

        return newTime


    def getMeaningfulNode(self, A, Config):

        storageNodes = cell2mat(Config.meta.storageNodes)
        rowNodes = cell2mat([Config.meta.rowNodes_start, Config.meta.rowNodes_end]).transpose
        cropNodes = []
        if Config.meta.bad_order:
            cropNodes = cell2mat(Config.meta.cropNodes)
        else:
            for row in rowNodes.transpose:
                cropNodes = [cropNodes, range(min(row),max(row))]



        if A.agentType == "logistics":
            if A.taskType == "move_to_picker":
                randomCropNode = cropNodes(randi(len(cropNodes)))
                nodeID = self.Coordinator.Network.node_list(randomCropNode).id

                #Identify next task
                A.load = A.load + 1
                if A.load >= 5:
                    A.taskType = "move_to_storage"


            elif A.taskType == "move_to_storage":
                randomStorageNode = storageNodes(randi(len(storageNodes)))
                nodeID = self.Coordinator.Network.node_list(randomStorageNode).id

                #Identify next task
                A.taskType = "move_to_picker"
                A.load = 0



        elif A.agentType == "crop_monitoring":

            if A.taskType == "move_to_edge":

                #Identify edge and target
                row_to_monitor = rowNodes[randi(length(rowNodes))][:]

                if Config.meta.bad_order:
                    x1=find(row_to_monitor(1)==cropNodes)
                    x2=find(row_to_monitor(2)==cropNodes)
                    [nodes_in_row,_]=find(row_to_monitor==cropNodes.transpose)
                    node_range = max(nodes_in_row) - min(nodes_in_row)
                    edge_index = randi(node_range-1)+nodes_in_row(1)

                    A.randomCropNode1 = cropNodes(edge_index)
                    A.randomCropNode2 = cropNodes(edge_index+1)
                else:
                    nodes_in_row = range(row_to_monitor[1], row_to_monitor[2])
                    edge_index = randi(len(nodes_in_row)-1)

                    A.randomCropNode1 = nodes_in_row(edge_index)
                    A.randomCropNode2 = nodes_in_row(edge_index+1)


                nodeID = self.Coordinator.Network.node_list(A.randomCropNode1).id

                #Identify next task
                A.taskType = "move_to_connected"

            elif A.taskType == "move_to_connected":

                #Identify edge and target
                randomCropNeighbour = A.randomCropNode2
                nodeID = self.Coordinator.Network.node_list(randomCropNeighbour).id

                #Identify next task
                A.taskType = "move_to_edge"



        elif A.agentType == "row_monitoring":

            if A.taskType == "move_to_row_start":

                #Identify row start and end
                A.row_to_monitor = rowNodes[randi(len(rowNodes))]
                A.randomRowNode1 = A.row_to_monitor[1]
                A.randomRowNode2 = A.row_to_monitor[2]

                nodeID = self.Coordinator.Network.node_list(A.randomRowNode1).id

                #Identify next task
                A.taskType = "move_to_row_end"

            elif A.taskType == "move_to_row_end":

                #Identify row end
                randomRowEnd = A.randomRowNode2
                nodeID = self.Coordinator.Network.node_list(randomRowEnd).id

                #Identify next task
                A.taskType = "move_to_row_start"


        else:

            #If agent has no specific task
            MAXNode = len(self.Coordinator.Network.node_list)
            nodeID = self.Coordinator.Network.node_list[randi(MAXNode)].id

        return nodeID

    def getRandomNode(self):

        if isempty(self.target_list):
            MAXNode = len(self.Coordinator.Network.node_list)
            nodeID = self.Coordinator.Network.node_list[randi(MAXNode)].id
        else:
            nodeID = self.target_list[1]
            self.target_list[1] = []

        return nodeID



    def GenerateTargets(self, total_targets):
        MAXNode = len(self.Coordinator.Network.node_list)
        targets = randi(MAXNode, total_targets, 1)
        nodeID = [0]*total_targets
        for i in range(1, total_targets):
            nodeID[i] = self.Coordinator.Network.node_list[targets[i]].id

        self.target_list = nodeID


    ## printlay Functions

    def Show_Map(self):
        self.Coordinator.Network.quickPlot
        self.Coordinator.Network.plotNodeNames


    def Show_Map_Times(self):
        self.Coordinator.Network.plot
        self.Coordinator.Network.plotNodeNames
        self.Coordinator.Network.plotNodeTimes


    def Show_Agents(self):
        self.Coordinator.Network.plot
        self.Coordinator.Network.plotNodeNames
        for agent in self.Agent_List:
            agent.currentNode.ChangeState("selected")
            pos = agent.currentNode.position
            text(pos[1]-.5, pos[2]+.5, str(agent.agent_id), "Color", [1,0,1])



    def Show_AgentPath(self, agent_id):
        f = figure
        set(f,'WindowStyle','docked')
        cla

        #Define agent plotting from
        A = self.Agent_List(agent_id)

        #Plot network, node names and times to reach each node
        A.Overlay.Network.plot
        A.Overlay.Network.plotNodeNames
        A.plotRouteTimes(A.currentID, A.reservations)

        #Mark reserved path
        for Res in reservation_list:
            EE=A.Overlay.findEdgeExt(Res.node1, Res.node2)
            EE.edge.ChangeState("selected")


        #Mark start and end points
        A.Overlay.findNodeExt(A.targetID).ChangeState('target')
        A.Overlay.findNodeExt(A.targetID).nodePlot.Marker = 'v'
        A.Overlay.findNodeExt(A.currentID).ChangeState('start')
        A.Overlay.findNodeExt(A.currentID).nodePlot.Marker = '^'

        #Format figure
        set(gca,'visible','on')
        axis(square)
        axis(fill)
        title("Agent: " + agent_id)
        set(gca,'visible','off')



    def Show_Movement(self, Reserv_List, time_in, time_out):
        #f = figure
        #set(f,'WindowStyle','docked')
        cla
        Show_Map(self)

        #Plot connections
        for aid in [self.Agent_List.agent_id]:
            self.Show_AgentMovement(Reserv_List[aid], time_in, time_out)


        #Format figure
        set(gca,'visible','on')
        axis(square)
        axis(fill)
        title(time_in +" -> "+time_out)
        set(gca,'visible','off')

    def Show_AgentMovement(self, R, t1, other_stuff_i_guess):

        times=[]
        cs=[]
        for r in R:
            times=[times, [r[1].time_in]]
            cs = [cs, r[1][1].time_in]


        idx_from = find(times<t1, 1, 'last')
        #idx_to   = find(times<t2, 1, 'last')

        idx_r_from = find(cs<t1, 1, 'last')
        #idx_r_to   = find(cs<t2, 1, 'last')

        r1_idx = [R[idx_r_from].time_in]
        #r2_idx = [R[idx_r_to  ].time_in]

        r1 = find(r1_idx < t1, 1, 'last')
        #r2 = find(r2_idx < t2, 1, 'last')

        fromID_1 = R[idx_r_from][r1].fromID
        fromID_2 = R[idx_r_from  ][r1].toID
        #fromID_2 = R[idx_r_to  ][r2].toID

        aid = R[1][1].agent_id
        atotal = len(self.Agent_List)
        self.Coordinator.Network.joinNodes(fromID_1,fromID_2,aid,atotal)

        #print("Agent " + aid + " moved from node:" + fromID_1 +" to node:" + fromID_2)




    def Show_PredMovement(self, Path_Log, from_time, delay, till_time):

        figure('Units','normalized','OuterPosition',[0,0,1,1])
        Show_Map(self)
        axis(image)
        title_obj=title(from_time +" -> "+till_time)
        set(gca,'visible','off')
        set(title_obj,'visible','on')

        plots = []
        scatters = []
        agent_labels = []

        hold(on)
        for i in range(from_time, delay, till_time):
            title_obj.String = i +" -> "+(i+delay)

            for p in plots:
                if p[1]!=0:
                    delete(p[1])
            for s in scatters:
                if s[1]!=0:
                    delete(s[1])
            for an in agent_labels:
                if an[1]!=0:
                    delete(an[1])

            #Plot connections
            for aid in [self.Agent_List.agent_id]:
                [plots[aid], scatters[aid], agent_labels[aid]] = self.Show_PredAgentMovement(Path_Log[aid], i, i+delay)


            pause(0.05)

        hold(off)


    def Show_PredAgentMovement(self, R, t1, t2):

        #Identify starting time for each group of reservations
        start_time=[]
        for r in R:
            start_time = [start_time, r[1](1).time_in]


        # Identify reservation agent is on at time t1
        group_index = find(start_time < t1, 1, 'last')
        if isempty(group_index):
            p=0
            s=0
            al=0
            return [p,s,al]
        group_times = [R[group_index].time_in]
        reservation_index = find(group_times < t1, 1, 'last')
        reserv_1 = R[group_index][reservation_index]
        reserv_total_time = reserv_1.time_out - reserv_1.time_in
        reserv_local_time = t1 - reserv_1.time_in
        t_percent_1 = reserv_local_time / reserv_total_time
        if t1 > reserv_1.time_out:
            t_percent_1 = 1


        # Identify reservation agent is on at time t2
        group_index = find(start_time < t2, 1, 'last')
        if isempty(group_index):
            p=0
            s=0
            al=0
            return [p,s,al]

        group_times = [R[group_index].time_in]
        reservation_index = find(group_times < t2, 1, 'last')
        reserv_2 = R[group_index][reservation_index]
        reserv_total_time = reserv_2.time_out - reserv_2.time_in
        reserv_local_time = t2 - reserv_2.time_in
        t_percent_2 = reserv_local_time / reserv_total_time
        if t2 > reserv_2.time_out:
            t_percent_2 = 1


        # Identify likely coordinates of agent at time t1
        start_pos = self.Coordinator.Overlay.findNode(reserv_1.fromID).position
        targt_pos = self.Coordinator.Overlay.findNode(reserv_1.toID).position
        pos_1=((targt_pos - start_pos) * t_percent_1) + start_pos
        pos_1a = pos_1
        #pos_1(pos_1>targt_pos)=targt_pos(pos_1>targt_pos)

        # Identify likely coordinates of agent at time t2
        start_pos = self.Coordinator.Overlay.findNode(reserv_2.fromID).position
        targt_pos = self.Coordinator.Overlay.findNode(reserv_2.toID).position
        pos_2=((targt_pos - start_pos) * t_percent_2) + start_pos
        pos_2a = pos_2
        #pos_2(pos_2>targt_pos)=targt_pos(pos_2>targt_pos)



        #Identify total number of agents and the agent in question
        aid = R[1][1].agent_id
        atotal = len(self.Agent_List)
        colour = hsv(atotal)

        #Plot the distance moved by the agent, colour coded
        p = plot([pos_1[1], pos_2[1]], [pos_1[2], pos_2[2]], \
            'Color', colour[aid][:], 'LineWidth', 4)

        s = scatter(mean([pos_1[1], pos_2[1]]), \
                    mean([pos_1[2], pos_2[2]]), 100, 'filled', \
                    'MarkerFaceColor', colour[aid][:], \
                    'MarkerEdgeColor', colour[aid][:])

        al = text(mean([pos_1[1], pos_2[1]]), \
                    mean([pos_1[2], pos_2[2]]), \
                    str(aid))

        agent_type = self.Agent_List[aid].agentType
        if agent_type  == "logistics":
            s.Marker = 'o'
        elif agent_type  == "row_monitoring":
            s.Marker = '^'
        elif agent_type  == "crop_monitoring":
            s.Marker = 's'

        return [p,s,al]




    def Show_Path(self, agent_id, reservation_details):

        #Define agent plotting from
        A = self.Agent_List(agent_id)
        currentID = reservation_details[1].fromID
        targetID = reservation_details[end].toID
        reservation_list = reservation_details

        #Mark reserved path
        for Res in reservation_list:
            EE=A.Overlay.findEdgeExt(Res.fromID, Res.toID)
            EE.edge.ChangeState("selected")


        #Mark start and end points
        hold(on)
        targetPos = A.Overlay.findNodeExt(targetID).node.position
        scatter(targetPos[1], targetPos[2],'filled','v','MarkerFaceColor',[1,.5,0])
        currentPos = A.Overlay.findNodeExt(currentID).node.position
        scatter(currentPos[1], currentPos[2],'filled','v','MarkerFaceColor',[1,.5,0])


    def Show_FullAgentPath(self, Reservation_List_List):

        #Identify agent
        agent_id = Reservation_List_List[1][1].agent_id
        A = self.Agent_List[agent_id]

        for i in range(1,len(Reservation_List_List)):
            RL = Reservation_List_List[i]

            #Load figure
            f = figure
            set(f,'WindowStyle','docked')

            #Format figure
            axis(fill)
            title("Agent: " + agent_id + " | Path " + i)

            #Plot network, node names and times to reach each node
            A.Overlay.Network.plot
            #A.Overlay.Network.plotNodeNames
            self.Show_Path(agent_id, RL)
            A.plotRouteTimes(RL)

            pause(1)




    def Run_FullAgentPath(self, Reservation_List_List):
        f = figure
        set(f,'WindowStyle','docked')

        #Identify agent
        agent_id = Reservation_List_List[1][1].agent_id
        A = self.Agent_List[agent_id]

        for i in range(1,len(Reservation_List_List)):
            RL = Reservation_List_List[i]

            #Clear figure
            cla

            #Format figure
            set(gca, 'Position', [0.05, 0.05, 0.9, 0.9], 'visible','off')
            title("Agent: " + agent_id + " | Path " + i)

            #Plot network, node names and times to reach each node
            A.Overlay.Network.quickPlot
            #A.Overlay.Network.plotNodeNames
            self.Show_Path(agent_id, RL)
            A.plotRouteTimes(RL)

            #Pause
            pause(2.5)



    def Analyse_ReservationActivity(self):
        Analyse_EdgeActivity(self, "total_reservations")

    def Analyse_ConflictActivity(self):
        Analyse_EdgeActivity(self, "total_conflicts")


    def Analyse_EdgeActivity(self, type):
        #f = figure
        #set(f,'WindowStyle','docked')
        set(gca, 'Position', [0.05, 0.05, 0.9, 0.9], 'visible','off')
        title("Total Edge Activity")

        #Identify upper bound
        if type == "total_conflicts":
            MX = max([self.Coordinator.Overlay.EdgeExtensions.total_conflicts])
        else:
            MX = max([self.Coordinator.Overlay.EdgeExtensions.total_reservations])


        #Set ColorMap
        j=jet(MX+1)

        #Plot Edges, Nodes & Names
        hold(on)
        for EExt in self.Coordinator.Overlay.EdgeExtensions:
            EExt.edge.Plot()
            EExt.edge.edgePlot.LineWidth = 5

            if type == "total_conflicts":
                EExt.edge.edgePlot.Color = j[EExt.total_conflicts+1][:]
            else:
                EExt.edge.edgePlot.Color = j[EExt.total_reservations+1][:]


        self.Coordinator.Overlay.Network.quickPlotNodes()
        self.Coordinator.Overlay.Network.plotNodeNames
        hold(off)

        #Set ColourBar
        colormap(jet)
        ticksLoc = linspace(0,1,10)
        ticksLabels = linspace(0,MX,10)
        colorbar('Ticks',ticksLoc,'TickLabels',round(ticksLabels))



