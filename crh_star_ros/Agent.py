class Agent():

    properties
        agent_id

        #Movement Information
        startID
        targetID
        reservations
        planningType

        #Heuristic Meta
        heuristic_details
        use_continuous_assignment
        use_dynamic_scoring
        use_context_dependent_heuristics
        independent_heuristic
        dependent_heuristic
        include_irritation

        # Context-Independent | Static | Heuristic Data
        direct_euclidian_distance
        optimal_route_length
        optimal_planning_time
        random_score
        irritation

        # Context-Dependent | Static | Heuristic Data
        task_details
        agentType
        taskType
        load
        randomCropNode1
        randomCropNode2
        row_to_monitor
        randomRowNode1
        randomRowNode2
        task_importance


    def __init__(ROSSim, currentName, Network):
        self.ROS = ROSSim
        self.Network = Network #This should be constructed here
        self.Overlay = self.DownloadOverlay()
        self.currentID = self.Overlay.findNodeExt(currentName).id
        self.reservation_uuid = 0
        self.targetNumber = 0
        self.idle = 1
        self.total_replans = 0
        self.optimal_arrival_time = 0
        self.total_deadlocks_overcome = 0
        self.start_time = 0

    def SetupHeuristics(self, heuristic_details):
        self.heuristic_details = heuristic_details

        self.use_continuous_assignment = heuristic_details.use_continuous_assignment
        self.use_dynamic_scoring = heuristic_details.use_dynamic_scoring
        self.use_context_dependent_heuristics = heuristic_details.use_context_dependent_heuristics

        self.independent_heuristic = heuristic_details.independent_heuristic
        self.dependent_heuristic = heuristic_details.dependent_heuristic

        self.include_irritation = heuristic_details.include_irritation

    def SetupTask(self, agent_type):
        self.agentType = agent_type

        if self.agentType == "logistics"
            self.taskType = "move_to_picker"
            self.load = 0
            self.task_importance = 3
        elif self.agentType == "crop_monitoring"
            self.taskType = "move_to_edge"
            self.task_importance = 2
        elif self.agentType == "row_monitoring"
            self.taskType = "move_to_row_start"
            self.task_importance = 1




    # Planning Scripts
    def NavigateTo_static(self, targetID, start_time):

        #Identify start and target nodes
        self.start_time = start_time
        self.startID = self.currentID
        self.targetID = targetID
        self.targetNumber = self.targetNumber + 1


        #Return if already at target node
        if self.targetID == self.startID
            self.reservations = Reservation(...
                             self.startID, self.targetID, ...
                             start_time, start_time, ...
                             self.agent_id, 0, 1)
            self.reservations.delayed = 0
            return



        #Identify planning will commence
        self.idle = false
        self.planningType = "initial planning."


        #Download latest map
        NewOverlay = self.DownloadOverlay()
        Start = NewOverlay.findNodeExt(self.startID)
        Target = NewOverlay.findNodeExt(self.targetID)


        #Initialise heuristic information
        self.irritation = 0
        self.total_replans = 0
        optimal_planning_timer = tic
        self.optimal_route_length = self.OptimalRoute(self.currentID,self.targetID)
        self.optimal_planning_time = toc(optimal_planning_timer)
        self.optimal_arrival_time = self.optimal_route_length + self.start_time
        self.random_score = rand()
        self.direct_euclidian_distance = self.pythag(Start.node, Target.node)
        self.total_deadlocks_overcome = 0

        #Identify route
        disp(newline+"Agent "+self.agent_id+" begins planning to node "...
            +Target.name+"n ("+Target.id+"i)")
        [Reservation_List, NewOverlay] = self.astar_modified(...
            self.currentID, self.targetID, NewOverlay, start_time, true)
        self.reservations = Reservation_List
        self.Overlay = NewOverlay

        #Publish reservation details
        #self.showReservationDetails(Reservation_List)
        self.ReserveEdges(Reservation_List)

    def Replan(self, failed_reservations):
        #Takes list of reservation objects beaten in battle.
        disp(newline+"Agent " + self.agent_id + " begins replanning.")

        #Infinite loop detector
        if length(dbstack) > (length(self.ROS.Agent_List)*150)
            disp("we in trouble... long dbstack")
            bp=psuedo_breakpoint # <- breakpoint


        # Update Heuristic information
        self.irritation = self.irritation + 1
        self.total_replans = self.total_replans + 1


        # Identify Start Node [sN is node at start of conflict edge]
        # Find first path component reached
        failed_reservation_mat=[failed_reservations{:}]
        failed_reservation_mat([failed_reservation_mat.uuid]~=self.reservation_uuid)=[]
        early = min([failed_reservation_mat.position])

        if length(failed_reservations) ~= length(failed_reservation_mat):
            disp("")


        if ~isempty(failed_reservation_mat):
            disp("Reservations Valid")

            #Find associated reservation
            InitialPath = self.reservations
            if early~=1:
                sN = InitialPath(early).fromID
            else:
                sN = self.currentID

            IPe = InitialPath(early)



        # Replan Paths

        if ~isempty(failed_reservation_mat):

            # Plan Path from Conflict
            #TODO: add condition to only do if (sN ~= self.currentID)
            [ReservationList1, Overlay1] = self.replan_from_conflict(...
                sN, IPe, InitialPath, early)


            # Plan Path from Conflict (with delay)
            [ReservationList2, Overlay2, delay] = self.replan_with_delay(...
                sN, IPe, InitialPath, early)



        # Plan Path from Start
        [ReservationList3, Overlay3] = self.replan_from_start()


        # Use lesser path length

        if isempty(failed_reservation_mat):
            times = [1, 1, 0]
        else:
            times = [ReservationList1(1).time_out, ...
                 ReservationList2(1).time_out, ...
                 ReservationList3(1).time_out]



        #times = [ReservationList1(1).time_out, ...
        #         ReservationList2(1).time_out, ...
        #         ReservationList3(1).time_out]
        [~,smallest]=min(times)


        if smallest == 1:
            disp("Agent "+self.agent_id+" replanning used replan from conflict.")
            self.Overlay = Overlay1
            self.reservations = ReservationList1
        elif smallest == 2:
            disp("Agent "+self.agent_id+" replanning used replan from conflict (with delay of "+delay+").")
            disp("Agent "+self.agent_id+" including delay on edge "+IPe.fromID+"-"+IPe.toID+" of "+delay+"t.")
            self.Overlay = Overlay2
            self.reservations = ReservationList2
        elif smallest == 3:
            disp("Agent "+self.agent_id+" replanning used replan from start.")
            self.Overlay = Overlay3
            self.reservations = ReservationList3


        self.findTimeIssues(self.reservations)

        # Reserve The Edges on the Path
        self.ReserveEdges(self.reservations)


    def OptimalRoute(self, startID, targetID):
        overlay = self.InitialiseOverlay()
        self.astar_modified(startID, targetID, overlay, 0, false)
        score = overlay.findNodeExt(targetID).arrival_time
        return score

    # Replan Functions
    def replan_from_conflict(self, sN, IPe, InitialPath, early):
        self.planningType = "replan from conflict."
        print("Agent "+self.agent_id+" "+self.planningType)

        #Define new Overlay
        Overlay = self.DownloadOverlay()

        #Plan new section of route
        [reservation_list, Overlay] = self.astar_modified(...
            sN, self.targetID, Overlay, IPe.time_in, true)

        #Append new route section to old section
        ReservationList = [InitialPath(1:early-1), reservation_list]
        for i = 1:length(ReservationList):
            ReservationList(i).position = i

        self.findTimeIssues(ReservationList)
        #self.showReservationDetails(ReservationList1)

        return [ReservationList, Overlay]

    def replan_with_delay(self, sN, IPe, InitialPath, early):
        self.planningType = "replan with delay."
        print("Agent "+self.agent_id+" "+self.planningType)

        #Define new Overlay
        Overlay = self.DownloadOverlay()

        #Identify period to delay for
        EExt=Overlay.findEdgeExt(IPe.fromID, IPe.toID)
        timeFrom = EExt.FindAvailablePeriod(IPe.time_in, IPe.time_out)
        delay = timeFrom - IPe.time_in

        #Plan new section of route
        [reservation_list, Overlay] = self.astar_modified(...
            sN, self.targetID, Overlay, timeFrom, true)
        if early > 1:
            InitialPath(early-1).delayed = true


        #Append new route section to old section
        ReservationList = [InitialPath(1:early-1), reservation_list]

        #
        if isempty(InitialPath(1:early-1)):
            r = Reservation(reservation_list(1).fromID, ...
                            reservation_list(1).fromID, ...
                            self.start_time, ...
                            reservation_list(1).time_in, ...
                            self.agent_id, 0, 1)
            r.delayed = true
            ReservationList = [r,ReservationList]


        #Update Positions
        for i = 1:length(ReservationList):
            ReservationList(i).position = i

        self.findTimeIssues(ReservationList)
        #self.showReservationDetails(ReservationList2)

        return [ReservationList, Overlay, delay]

    def replan_from_start(self):
        self.planningType = "replan from start."
        print("Agent "+self.agent_id+" "+self.planningType)

        #Define new Overlay
        Overlay = self.DownloadOverlay()

        #Replan from start
        [ReservationList, Overlay] = self.astar_modified(...
            self.currentID, self.targetID, Overlay, self.start_time, true)
        self.findTimeIssues(ReservationList)
        #self.showReservationDetails(ReservationList3)

        return [ReservationList, Overlay]


    # Overlay Management
    def InitialiseOverlay(self):
        #Create an fresh empty Overlay
        overlay = Overlay(self.Network)
        return overlay

    def DownloadOverlay(self):

        #Initialise Overlay object
        overlay = self.InitialiseOverlay()

        #Fill Overlay with reservation information
        for i = 1:length(overlay.EdgeExtensions):
            overlay.EdgeExtensions(i).reservations = ...
            self.ROS.Coordinator.Overlay.EdgeExtensions(i).reservations


        #Omit reservation details regarding self
        overlay.RemovePath(self.agent_id)

        return overlay

    # Motion Planning Script
    def astar_modified(A, startID, targetID, tmap, start_time, generateScores):
        startNodeExt =  tmap.findNodeExt(startID)
        targetNodeExt = tmap.findNodeExt(targetID)

        OPEN = []
        CLOSED = []
        FAILED = []

        #Add the start node extension to the open list.
        OPEN = [OPEN, startNodeExt]

        #Define the time the agent will begin moving.
        startNodeExt.arrival_time = start_time
        startNodeExt.departure_time = start_time
        startNodeExt.departure_times = [start_time]*startNodeExt.total_neighbours

        #Define end point for path generation
        startNodeExt.parent_id = -1
        while True:

            #Find smallest edge
            if OPEN ~= []:
                currentNodeExt = self.findMin(OPEN)
                print("Node "+ currentNodeExt.name+"n in focus.")
            else:
                [OPEN, FAILED] = self.findMinFailed(FAILED, CLOSED, OPEN, targetID, tmap)
                continue

            #Move currentNode from OPEN to CLOSED
            OPEN(OPEN==currentNodeExt)=[]
            CLOSED = [CLOSED, currentNodeExt.id]
            print("Node "+ currentNodeExt.name+"n moved from OPEN to CLOSED.")

            #If current point is at target, break.
            if currentNodeExt.id == targetNodeExt.id:
                print("Node "+ currentNodeExt.name+"n is at target Node.")
                reservation_list = self.backprop_path_modified(targetNodeExt, tmap)
                self.findTimeIssues(reservation_list)
                return [reservation_list, tmap]

            #Determine costs for each neighbour to the current node.
            neighbour_list = tmap.findNeighbours(currentNodeExt)
            for neighbour_entry= neighbour_list: #add {:}
                neighbourNExt = neighbour_entry{1}
                print("Neighbour " +neighbourNExt.name+ "n is in focus.")

                EExt=tmap.findEdgeExt(currentNodeExt.id, neighbourNExt.id)

                #Early Exit
                if any(neighbourNExt.id == CLOSED):
                    print("Neighbour " +neighbourNExt.name+ "n is already CLOSED.")
                    continue

                #If edge taken and CRH battle unsuccessful, skip edge.
                if generateScores:
                    [available, CRH] = self.CRH_BATTLE(currentNodeExt, neighbourNExt, targetNodeExt, EExt)
                else:
                    available, CRH = 1, 1

                if !available:
                    print("Edge "+currentNodeExt.name+"n-"+neighbourNExt.name+"n is NOT available (taken and CRH cant win)")

                    #Edge is unavailable
                    if neighbourNExt.f_cost == -1: # <--issue? Inf second time doesnt show best parent?
                        print("Edge "+currentNodeExt.name+"n-"+neighbourNExt.name+"n is untouched")

                        #Update details
                        h_cost = self.pythag(neighbourNExt.node, targetNodeExt.node)
                        neighbourNExt.UpdateCosts(Inf, Inf, h_cost)
                        neighbourNExt.UpdateParent(currentNodeExt.id, CRH)
                        neighbourNExt.UpdateTimes(currentNodeExt, EExt)

                        print("Parent of "+neighbourNExt.name+"n set to "+currentNodeExt.name+"n")
                        print("Arrival for neighbour "+neighbourNExt.name+"n @ "+neighbourNExt.arrival_time)
                        print("Departure for neighbour "+neighbourNExt.name+"n @ "+neighbourNExt.departure_time)

                        #Add failed reservation details to list
                        FAILED = [FAILED, [neighbourNExt.id currentNodeExt.id currentNodeExt.f_cost]]
                        print("Edge "+currentNodeExt.name+"n-"+neighbourNExt.name+"n added to FAILED")
                    continue
                else:
                    print("Edge "+currentNodeExt.name+"n-"+neighbourNExt.name+"n is up for grabs (empty or CRH can win)")



                #Calculate distance travelled and distance to target.
                g_cost = currentNodeExt.g_cost + EExt.edge.weight
                h_cost = self.pythag(neighbourNExt.node, targetNodeExt.node)
                f_cost = g_cost + h_cost
                print("Neighbour "+neighbourNExt.name+"n has f_cost of "+round(f_cost,3))

                #If new path is better, update cost and parent.
                if any([f_cost<neighbourNExt.f_cost,~any(neighbourNExt==OPEN)]):

                    neighbourNExt.UpdateCosts(f_cost, g_cost, h_cost)
                    neighbourNExt.UpdateParent(currentNodeExt.id, CRH)
                    neighbourNExt.UpdateTimes(currentNodeExt, EExt)

                    print("Parent of "+neighbourNExt.name+"n set to "+currentNodeExt.name+"n")
                    print("Arrival for neighbour "+neighbourNExt.name+"n @ "+neighbourNExt.arrival_time)
                    print("Departure for neighbour "+neighbourNExt.name+"n @ "+neighbourNExt.departure_time)

                    #Include node in search for smaller routes.
                    if ~any(neighbourNExt == OPEN):
                        print("Neighbour "+ neighbourNExt.name+"n moved to OPEN")
                        OPEN = [OPEN, neighbourNExt]

        return [reservation_list, tmap]




    # CRH Functions
    def CRH_BATTLE(self, currentNExt, neighbourNExt, targetNExt, EExt):
        #Return 1 if CRH edge is up for grabs (empty or CRH can win)
        #Return 0 if edge is unavailable (taken and CRH cant win)


        #Calculate time for use of edge.
        from_time = currentNExt.arrival_time #Use arrival since the delay is not created yet
        time_till = currentNExt.arrival_time+EExt.time_weight #The neighbour arrival_time is not set yet
        print("                  Edge "+currentNExt.name+"n-"+neighbourNExt.name+"n wanted from "+from_time+"->"+time_till)

        #Check if edge is free at time required (no use for EExt.IsEmpty2)
        conflicts_list = EExt.IsEmpty(from_time, time_till)

        #Calculate the CRH score to battle with.
        CRH_Score = self.getCRH(currentNExt, neighbourNExt, targetNExt, EExt)

        #Succeed on edge has no conflicts
        if isempty(conflicts_list):
            success = 1
            return [success, CRH_Score]


        #Extract the local CRH score
        conflicting_CRH = 0
        for R = conflicts_list:
            conflicting_CRH = conflicting_CRH + R.CRH


        #Fail on Maximum CRH met
        if conflicting_CRH > 150: #This must be normalised
            success = 0
            return [success, CRH_Score]


        #If local CRH score is smaller, return failure.
        success = (CRH_Score > conflicting_CRH)
        if success:
            for R = conflicts_list:
                print("Agent " + self.agent_id + " can take edge " + ...
                    EExt.edge.node1.id + "-"+ EExt.edge.node2.id + ...
                    " from Agent " + R.agent_id + " with CRH " + CRH_Score + " using " + self.planningType)
        return [success, CRH_Score]


    def getCRH(self, C, N, T, E):

        #Instantiate empty variable for storing the score.
        CRH = 0

        if self.use_dynamic_scoring:
            #Calculate dynamic CRH score
            CRH = self.GenerateDynamicCRH(C, N, T, E)
        else:
            #Calculate static CRH score
            CRH = self.GenerateStaticCRH(C, N, T, E)


        #If including irritation, increment CRH by its value
        if self.include_irritation:
            CRH = CRH + self.irritation


        if self.use_context_dependent_heuristics:
            CRH = CRH * self.GenerateDependentCRH

        return CRH

    def GenerateDependentCRH(self):
        CRH = self.task_importance
        return CRH

    def GenerateDynamicCRH(self, C, N, T, ~):
        CRH = 0

        #Identify independent heuristic
        if any(self.independent_heuristic == "euclidian_distance"):
            CRH = CRH + self.pythag(N.node, T.node)


        if any(self.independent_heuristic  == "optimal_route_length"):
            CRH = CRH + self.OptimalRoute(C.id,T.id)


        if any(self.independent_heuristic == "random"):
            CRH = CRH + rand()


        if any(self.independent_heuristic == "planning_time"):
            if (CRH==0):
                CRH=1
            tic
            self.OptimalRoute(C.id,T.id)
            CRH = CRH * toc


        if any(self.independent_heuristic == "agent_id"):
            CRH = CRH + self.agent_id


        if any(self.independent_heuristic == "no_replanning"):
            CRH = CRH + 0


        #Inverse Variants
        if any(self.independent_heuristic == "inverse_euclidian_distance"):
            CRH = CRH - self.pythag(N.node, T.node)


        if any(self.independent_heuristic  == "inverse_optimal_route_length"):
            CRH = CRH - self.OptimalRoute(C.id,T.id)


        if any(self.independent_heuristic == "inverse_planning_time"):
            tic
            self.OptimalRoute(C.id,T.id)
            CRH = CRH - toc

        return CRH

    def GenerateStaticCRH(self, ~, ~, ~, ~):
        CRH = 0

        #Identify independent heuristic
        if any(self.independent_heuristic == "euclidian_distance"):
            CRH = CRH + self.direct_euclidian_distance


        if any(self.independent_heuristic  == "optimal_route_length"):
            CRH = CRH + self.optimal_route_length


        if any(self.independent_heuristic == "random"):
            CRH = CRH + self.random_score


        if any(self.independent_heuristic == "planning_time"):
            if (CRH==0):
                CRH=1
            CRH = CRH * self.optimal_planning_time


        if any(self.independent_heuristic == "agent_id"):
            CRH = CRH + self.agent_id


        if any(self.independent_heuristic == "no_replanning"):
            CRH = CRH + 0



        #Inverse Variants
        if any(self.independent_heuristic == "inverse_euclidian_distance"):
            CRH = CRH - self.direct_euclidian_distance


        if any(self.independent_heuristic  == "inverse_optimal_route_length"):
            CRH = CRH - self.optimal_route_length


        if any(self.independent_heuristic == "inverse_planning_time"):
            CRH = CRH - self.optimal_planning_time

        return CRH


    # Motion Planning Tools
    @classmethod
    def findMin(~, OPEN):
        [~,idx] = min([OPEN.f_cost])
        minNode = OPEN(idx)
        return minNode

    def findMinFailed(self, FAILED, CLOSED, OPEN, ~, overlay):

        print("          OPEN List Empty")
        print("          FAILED List:")
        print(round(FAILED',3))

        FAILED(:,any(FAILED(1,:)==CLOSED'))=[]

        smallest = [0,0,0,0,Inf]
        minimal = FAILED(:,FAILED(3,:)==min(FAILED(3,:)))

        T = overlay.findNodeExt(self.targetID)
        for m = minimal: #[neighbour_id, current_id, current_f_cost]

            #Identify nodes
            N = overlay.findNodeExt(m(1)) #neighbour Node
            P = overlay.findNodeExt(m(2)) #parent Node

            #Calculate costs
            EExt = overlay.findEdgeExt(P.id, N.id)
            g_cost = P.g_cost + EExt.edge.weight
            h_cost = self.pythag(N.node, T.node)
            f_cost = g_cost + h_cost

            #Idenfity smallest f_cost
            if f_cost < smallest(5): #Swap this out to just append, and find smallest later on
                smallest=[N.id, P.id, g_cost, h_cost, f_cost]


        #Identify nodes
        N = overlay.findNodeExt(smallest(1))
        P = overlay.findNodeExt(smallest(2))

        #Identify delay time and new arrival time
        EExt = overlay.findEdgeExt(P.id, N.id)
        PArrival = P.arrival_time
        NArrival = PArrival + EExt.time_weight #this must be calculated
        NewPDeparture = EExt.FindAvailablePeriod(PArrival, NArrival)
        PDepartureDelay = NewPDeparture - PArrival

        #Update deadlock count
        EExt.deadlock_overcome = true

        #Save new meta info
        N.UpdateCosts(smallest(3), smallest(4), smallest(5))
        P.departure_time = NewPDeparture
        P.set_departure_times(N.id, NewPDeparture)
        N.UpdateTimes(P, EExt)

        #Log out some information
        print(EExt)
        print(EExt.reservations)
        print("Agent "+self.agent_id+" including local delay on edge "+...
            P.name+"-"+N.name+" of "+PDepartureDelay+"t.")
        print("Agent "+self.agent_id+" entering "+P.name+"n-"+N.name+"n @ t"+P.departure_time)
        print("Agent "+self.agent_id+"  exiting "+P.name+"n-"+N.name+"n @ t"+N.arrival_time)

        #Append neighbour to OPEN list
        print("            FAILED Node "+ N.name+" moved to OPEN.")
        OPEN = [OPEN, N]

        #Remove neighbour from FAILED list
        print("            Edge "+FAILED(1)+"i-"+FAILED(2)+"i removed from FAILED")
        FAILED(:,all(FAILED(1:2,:)==smallest(1:2)')) = []

        return [OPEN, FAILED]

    def pythag(~, nodeA, nodeB):
        Ax = nodeA.position(1)
        Ay = nodeA.position(2)
        Bx = nodeB.position(1)
        By = nodeB.position(2)
        dist = sqrt(power(Ax-Bx,2)+power(Ay-By,2))
        return dist

    def backprop_path_modified(self, endpoint, overlay):
        #TODO: swap this out to make the reservation list incremental
        #for position
        current = endpoint
        path = current

        #Generate list of nodes from endpoint to startpoint
        while current.parent_id ~= -1:

            #Append new path component
            current = overlay.findNodeExt(current.parent_id)
            path(end+1) = current


        #Generate list of Reservation Objects to publish
        #TODO: find a way to not need the following line... {}?
        Reservation_List = Reservation(0,0,0,0,0,0,0)
        for i = 2:length(path):
            Start=path(i)
            Target=path(i-1)

            #Create reservation objects
            Reservation_List(i-1) = Reservation(...
                             Start.id, ...
                             Target.id, ...
                             Start.get_departure_times(Target.id), ...
                             Target.arrival_time, ...
                             self.agent_id, ...
                             Target.CRH, ... #self.getCRH(), ...
                             (length(path)-i)+1)
            Reservation_List(i-1).delayed = Start.arrival_time ~= Start.get_departure_times(Target.id) #Start.departure_time

        Reservation_List = flip(Reservation_List)
        return Reservation_List

    def ReserveEdges(self, reservation_list):
        self.findTimeIssues(reservation_list)

        #Generate and apply uuid to the reservation objects
        self.reservation_uuid = self.reservation_uuid + 1
        for r = reservation_list:
            r.uuid = self.reservation_uuid


        #Count deadlocks overcome
        for i = 2:length(reservation_list):
            r=reservation_list(i)
            if r.fromID ~= r.toID:
                EExt = self.Overlay.findEdgeExt(r.fromID, r.toID)
                self.total_deadlocks_overcome=self.total_deadlocks_overcome...
                    +EExt.deadlock_overcome

        #Publish the list of Reservation objects
        self.ROS.Topic_publishReservations(reservation_list)


    # Display Functions
    def plotRouteTimes(self, reservation_list):

        #If agent has not been given or has reached its goal, return
        if isempty(reservation_list):
            return

        #Define Colour Pallette
        shadeG = linspace(.8, .4, length(reservation_list))'
        shadeR = flip(shadeG)

        #For each node after the first, print the time
        for i = 1:length(reservation_list)-1:
            Res = reservation_list(i)

            #Identify location to print text
            pos=self.Overlay.findNodeExt(Res.toID).node.position-.5

            #Define colour to print times
            colour=[shadeR(i), shadeG(i),0]
            if Res.delayed:
                colour=[1,0,.7]

            #Print time
            text(pos(1),pos(2),string(Res.time_out),"Color", colour)


        #Mark Start Node
        start=reservation_list(1)
        pos=self.Overlay.findNodeExt(start.fromID).node.position-.5
        text(pos(1),pos(2),string(start.time_in), "Color",[0,.7,.8])

        #Mark Target Node
        final=reservation_list(end)
        pos=self.Overlay.findNodeExt(final.toID).node.position-.5
        text(pos(1),pos(2),string(final.time_out), "Color",[1,.3,0])



    def showReservationDetails(~, reservation_list):
        position = [reservation_list.position]'
        path = [reservation_list.fromID, reservation_list.toID]'
        times = [reservation_list.time_in, reservation_list.time_out]'
        delayed_leaving = logical([reservation_list.delayed]')
        T = table(position,path,times,delayed_leaving)
        disp(T)



    # Debug Tools
    def findTimeIssues(self, reservation_list):
        tin= [reservation_list.time_in]
        tout=[reservation_list.time_out]
        err=[0,tout]'>[tin,Inf]'
        if any(err):
            positions_with_err=find(err)
            disp(positions_with_err)
            self.showReservationDetails(reservation_list)
            d=r # <-- this is a breakpoint



    def ddisp(self, msg):
        msg=msg


    def cdisp(~, colour, msg):
        cprintf(colour,msg+"\n")


    # Update Functions
    def UpdateLocation(self, t):
        if self.idle, disp("Agent "+self.agent_id+" is IDLE at TARGET "+self.Overlay.findNodeExt(self.currentID).name):
            return

        #Identify the node the Agent is at at time t.
        tin=[self.reservations.time_in]
        newID = find(tin<=t,1,'last')

        #If t < A,reservations(1).time_in, then the agent is delayed
        if isempty(newID): # && self.reservations(1).delayed
            self.currentID = self.reservations(1).fromID
            self.start_time = t
        else:
            #Set new location
            self.currentID = self.reservations(newID).fromID
            self.start_time = self.reservations(newID).time_in


        if self.reservations(end).time_out <= t:
            self.currentID = self.reservations(end).toID


        """
        T=self.Overlay.findNodeExt(self.targetID)
        if T.arrival_time == t:
            self.currentID = self.targetID
            disp("Agent "+self.agent_id+" has moved to TARGET "+T.name)
            blob = 1
        else:
            for Res = self.reservations:
                if t >= Res.time_in:
                    self.currentID = Res.fromID
                    disp("Agent "+self.agent_id+" has moved to node "+self.Overlay.findNodeExt(self.currentID).name)
                    blob=1
                    break
        """


        #Set Agent to idle if the goal is reached
        newName = self.Overlay.findNodeExt(self.currentID).name
        if self.currentID == self.targetID:
            disp("Agent "+self.agent_id+" has moved to TARGET "+newName)
            self.idle = true
            self.reservations = []
            self.ROS.Coordinator.Overlay.RemovePath(self.agent_id)
        else:
            disp("Agent "+self.agent_id+" has moved to node "+newName)
            self.idle = false


