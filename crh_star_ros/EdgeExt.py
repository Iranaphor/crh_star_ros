class EdgeExt():

    def __init__(self, edge):
        self.edge = edge
        self.time_weight = floor(edge.weight * 10) #this can be changed later
        self.reservations = [] %[agent, start_time, end_time]
        self.total_reservations = 0;
        self.total_conflicts = 0;
        self.deadlock_overcome = false;

    def AddReservation(self, agent, start_time, end_time, CRH, position, uuid):
		self.reservations = [self.reservations; [agent, start_time, end_time, CRH, position, uuid]]
        self.total_reservations = self.total_reservations + 1

    def Purge(self):
		self.reservations = []
        self.total_reservations = 0
        self.total_conflicts = 0

    def PurgeAgent(self, agent_id):
        if not isempty(self.reservations):
            self.reservations[self.reservations[:,1] == agent_id,:] = []

    def PurgeOld(self, t):
        if not isempty(self.reservations):
            self.reservations[self.reservations[:,3] <= t,:] = []

    def IsEmpty(self, fromT, tillT):
        result = IsEmpty2(self, fromT, tillT, self.edge.node1.id);
        return result

    def IsEmpty2(self, fromT, tillT, fromID):
        """
        res.timefrom[======================]res.timetill
                 |----------------------------|
              |-----------|          |----------|
          |-----|        |------------|        |------|
               tillT                        fromT

          if not (tillT < res.timefrom | fromT > res.timetill)
              bad
        """
        res = self.reservations;
        if isempty(res), result = []; return, end

        BEFORE = tillT <= res(:,2);
        AFTER = fromT >= res(:,3);
        conflicts = res(not ( BEFORE | AFTER),:);

        edgeNames = [self.edge.node1.id, self.edge.node2.id];

        for i in range(1, size(conflicts,1))
            r=num2cell([fromID, edgeNames(edgeNames!=fromID),\
                conflicts[i,[2,3,1,4,5]]]);
            result[i] = Reservation(r[:]);
            result[i].uuid = conflicts[i,6];

        if not exist('result','var'):
            result = []
            return result

    def FindAvailablePeriod(self, fromT, tillT):
        if isempty(self.reservations):
            newFromT=fromT
            return newFromT

        #Sort reservations
        R = self.reservations
        [_ ,g]=sort(R(:,3))
        R=R(g,:)

        #Remove any reservations before the current request
        R[R(:,3) <= fromT,:] = [] #R[R(:,3) < fromT,:] = []

        #If no more reservations, return (this should never be hit)
        if isempty(R):
            newFromT=fromT
            return newFromT

        #Identify space required
        duration=tillT-fromT

        #Identify spaces available
        spaces=[R(2:end,2);inf]-R(:,3)

        #Find next space available greater than the space required
        if spaces[find(spaces>duration,1)] == Inf:
            #If no space between reservations, take exit from last
            newFromT = R(end,3)+1
        else:
            newFromT = R(find(spaces>duration,1),3)+1
        return newFromT

    def IsEqual(self, e):
        EEnames = [self.edge.node1.id, self.edge.node2.id]
        enames = [e.node1.id, e.node2.id]

        booll = any([all(EEnames == enames), all(EEnames == flip(enames))])
        return booll
