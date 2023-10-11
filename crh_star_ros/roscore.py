def roscore(Config=None):

    ## Load Configuration File
    if not Config:
        addpath(genpath('./YAMLMatlab_0.4.3'))
        Config = ReadYaml('configuration_files/meta.yaml')

    Config['meta']['total_cycles'] = 5000
    Config['meta']['pointset'] = 'riseholme_poly_act_sim.tmap'

    for heur in Config['heuristics']['independent_heuristic']:
        heur = str(heur)

    Config['heuristics']['independent_heuristic'] = \
        [Config['heuristics']['independent_heuristic']]

    ## Define random seed
    import random
    if Config['meta']['rng_seed'] != -1:
        random.seed(Config['meta']['rng_seed'])
    else:
        random.random()


    ## Load Map File
    print("Loading Map: "+str(Config['meta']['pointset']))
    try:
        pointset = Config['meta'][Config['meta']['pointset'].split('.')[0]]
        Config['meta']['storageNodes']   = pointset['storageNodes']
        Config['meta']['rowNodes_start'] = pointset['rowNodes_start']
        Config['meta']['rowNodes_end']   = pointset['rowNodes_end']
        Config['meta']['cropNodes']  = pointset['cropNodes']
        Config['meta']['bad_order']  = pointset['bad_order']
    except Exception as e:
        print(e)
    Meta = Config['meta']
    Heuristics = Config['heuristics']

    from crh_star_ros.ReadTmap import ReadTmap
    [NodeList, NodeNameList, AdjacencyMatrix] = ReadTmap(Meta['pointset'])


    ## Launch ROS Core
    from crh_star_ros.ROSSim import ROSSim
    ROSCore = ROSSim(NodeList, NodeNameList, AdjacencyMatrix)

    #printlay map based on Config file demands
    if Meta['show_map_on_startup']:
        if Meta['show_node_names']:
            ROSCore.Show_Map
        else:
            ROSCore.Coordinator.Network.quickPlot

    del NodeList, NodeNameList, AdjacencyMatrix


    ## Launch Agents
    A[Meta.total_agents] = 0
    Type_Count=[Meta.total_logistics, Meta.total_crop_monitoring, Meta.total_row_monitoring]
    Type_Label=["logistics","crop_monitoring","row_monitoring"]
    Types = repelem(Type_Label,Type_Count)
    for i in range(1,len(Types)):
        ROSCore.Launch_TaskAgent(ROSCore.getRandomNode, Heuristics, Types[i])
        A[(Meta.total_agents-i)+1] = ROSCore.Agent_List[-1]


    ## Set initial navigation target for each Agent
    for i in range(1, len(ROSCore.Agent_List)):
        A[i].NavigateTo_static(ROSCore.getMeaningfulNode(A[i], Config), 0)
        Path_Log[i][1] = A[i].reservations

    del aid

    ## Begin Simulation
    T = 0
    AFin = [0]*len(A)
    Idle = false(1,len(A))
    Planned = true(1,len(A))
    [TotalReplans, TotalDelay, AgentID, Deadlocks, Times] = deal([0]*Meta.total_cycles)

    for cycle in range(1, Meta.total_cycles):
        t=tic

        #Find next timestep
        for i in range(1, len(ROSCore.Agent_List)):
            AFin[i] = A[i].Overlay.findNodeExt(A[i].targetID).arrival_time
            try:
                Idle[i] = A[i].idle
            except:
                print("Hi")

            if not isempty(A[i].reservations):
                Path_Log[i][end+1] = A[i].reservations



        #Move to next timestep with event
        if Heuristics.use_continuous_assignment:
            [_,m]=min(AFin)
            T = ROSCore.TimeStep(AFin(m)-T)

        else:

            if all(Planned):
                T = ROSCore.TimeStep((max(AFin)-T))
                print("NEW BATCH STARTED")
                Planned = false(1,len(A))
                cycle = cycle - 1
                continue
            else:
                T = ROSCore.TimeStep(0)
                [_,m]=min(AFin)
                Planned[m] = true




        #Save details
        TotalReplans[cycle] = A[m].total_replans
        TotalDelay[cycle] = (T - A[m].optimal_arrival_time)
        AgentID[cycle] = m
        Deadlocks[cycle] = A[m].total_deadlocks_overcome
        Times[cycle] = min(AFin)-A[m].start_time

        #Navigate to new random target
        if T >= A[m].Overlay.findNodeExt(A[m].targetID).arrival_time:
            A[m].NavigateTo_static(ROSCore.getMeaningfulNode(A[m], Config), T)


        print("Time taken to define new goal: "+toc(t))


    #Show Route Details
    #ROSCore.Show_PredMovement(Path_Log, 0, 10, T)

	#Show Reservation Details
    ROSCore.Analyse_ReservationActivity
    #ROSCore.Analyse_ConflictActivity
    return [TotalDelay, TotalReplans, AgentID, Deadlocks, Times, T]


