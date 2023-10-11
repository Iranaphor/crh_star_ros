import yaml

def ReadTmap(yaml_file):
    print("Opening File: " + yaml_file)
    with open("./configuration_files/"+yaml_file, 'r') as f:
        data = f.read()
    YamlStruct = Config = yaml.safe_load(data)

    print("Identifying Nodes:")
    NodeList = []
    NodeNameList = []
    for i in range(1, len(YamlStruct)):
        n = YamlStruct[i]
        NodeList += [[i, n['node']['pose']['position']['x'], n['node']['pose']['position']['y']]]
        NodeNameList += [str(n['node']['name'])]

    print("Identifying Edges:")
    AdjacencyMatrix = [[0]*len(YamlStruct)]*len(YamlStruct)
    for i in range(1, len(YamlStruct)):
        n = YamlStruct[i]

        for j in range(1, len(n['node']['edges'])):
            e = n['node']['edges'][j]
            eid = [NodeNameList.index(n['node']['name']),\
                   NodeNameList.index(e['node'])]
            AdjacencyMatrix[min(eid)][max(eid)] = 1

    return [NodeList, NodeNameList, AdjacencyMatrix]
