class Coordinator():
    #Network
    #Overlay
    #ROS
    #OverlayUUID = 0;

    def __init__(self, ROS):
        self.ROS=ROS


    def Subscribe_ReservationsUpdate(self, reservation_list):
        aid=reservation_list[1].agent_id

        print("Agent "+aid+" reserved "+len(reservation_list)+" edges.")

        notifications = []
        agents = []

        #Remove existing reservations by the agent publishing the path
        self.Overlay.RemovePath(aid)

        #For each edge taken by reservation
        for r in reservation_list:

            #Manage Extra Delay Reservation
            if r.fromID == r.toID:
                continue

            #Identify edge and conflicts
            EExt = self.Overlay.findEdgeExt(r.fromID, r.toID)
            existingConflicts = EExt.IsEmpty(r.time_in, r.time_out)

            #Add conflict details to list
            if not isempty(existingConflicts):
                for oldR in existingConflicts:
                    EExt.total_conflicts = EExt.total_conflicts + 1
                    notifications[end+1] = oldR
                    agents[end+1] = oldR.agent_id

            #Add the new reservation
            EExt.AddReservation(r.agent_id, r.time_in, r.time_out, r.CRH, r.position, r.uuid)

        #Get list of unique agents to notify
        agents = set(agents)
        if not isempty(agents):
            print("Agent "+aid+" caused "+len(notifications) + \
                " conflicts with agents: " + \
                "["+', '.join(agents)+"]")
        else:
            print("Agent "+aid+" caused no conflicts.")


        #Update overlay UUID to show change in reservations. (unused)
        self.OverlayUUID += 1

        #For each unique agent which has lost a reservation
        for a in agents:

            #Identify failed reservations to send to agent
            agent_failed_reservations = []
            for n in notifications:
                if n[1].agent_id == a:
                    if C.existsConflict(n[1], aid):
                        agent_failed_reservations[end+1] = n[1]

            #Notify agent of its failed reservations
            if not isempty(agent_failed_reservations):
                self.publishNotifications(a, agent_failed_reservations)

    def existsConflict(self, n, aid):
        EExt = self.Overlay.findEdgeExt(n.fromID, n.toID)
        existingConflicts = EExt.IsEmpty(n.time_in, n.time_out)

        # < 2 reservation <== conflict impossible <= replan not needed
        conflictExists = len(existingConflicts) >= 2;

        if conflictExists:
            ec=[existingConflicts.agent_id]
            conflictExists = all([any(ec==n.agent_id),any(ec==aid)])

        """
        The point is to only allow reservations to be used for
        replanning if the reservation is still valid

        it is still valid if the edge has the reservation and the
        request in place

        so existingConflicts must contain a reservation with the id of
        the one requesting the edge, and the id of the agent who is
        being overtaken

        must it also have no other reservations present? it will not in
        the end
        """

        if len(existingConflicts) > 2:
            print("This is probably an issue\ shouldnt exceed 2 reservations")
        return conflictExists

    def publishNotifications(self, agent_id, reservations):
        self.ROS.Topic_publishFailedReservations(agent_id, reservations)
