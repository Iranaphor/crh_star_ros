import yaml

def ReadTmap(yaml_file):
    yaml_file = char("./configuration_files/"+yaml_file)

    print("Opening File: " + string(yaml_file))
    addpath(genpath('./YAMLMatlab_0.4.3'))
    YamlStruct = ReadYaml(yaml_file)

    print("Identifying Nodes:")
    NodeList = []
    NodeNameList = []
    for i = 1:length(YamlStruct):
        n = YamlStruct{i}
        NodeList = [NodeList; i, n.node.pose.position.x, n.node.pose.position.y]
        NodeNameList = [NodeNameList, string(n.node.name)]

    print("Identifying Edges:")
    AdjacencyMatrix = zeros(length(YamlStruct))
    for i = 1:length(YamlStruct):
        n = YamlStruct{i}

        for j = 1:length(n.node.edges)
            e = n.node.edges{j}
            eid = [find(NodeNameList==n.node.name,1),...
                   find(NodeNameList==e.node,1)]
            eid = sort(eid)
            AdjacencyMatrix(eid(1),eid(2)) = 1

    return [NodeList, NodeNameList, AdjacencyMatrix]
