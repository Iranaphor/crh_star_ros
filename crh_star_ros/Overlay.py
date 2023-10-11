# -*- coding: utf-8 -*-
#! /usr/bin/env python3
# ----------------------------------
# @author: jheselden
# @email: jheselden@lincoln.ac.uk
# @date:
# ----------------------------------

class Overlay():

    def __init__(self, Network):
        self.EER = [] #EdgeExtensionsReference
        self.NER = [] #NodeExtensionsReference
        self.NER_Name = [] #NodeExtensionsReferenceName

        self.Network = Network

        # Create Edge Extensions
        self.EdgeExtensions = [EdgeExt(edge) for edge in Network.edge_list]
        EN1 = [Network.edge_list.node1].transpose
        EN2 = [Network.edge_list.node2].transpose
        self.EER = [EN1.id,EN2.id]

        # Create Node Extensions
        self.NodeExtensions = [NodeExt(node) for node in Network.node_list]
        self.NER = [Network.node_list.id]
        self.NER_Name = [Network.node_list.name]

    def Copy(self):
        newNet = Network(\
            self.Network.node_locations, \
            self.Network.adjacency_matrix)
        overlayCopy = Overlay(newNet)

        #Copy reservation information
        for i in range(1,len(self.EdgeExtensions)):
            overlayCopy.EdgeExtensions(i).reservations = \
                      self.EdgeExtensions(i).reservations
        return overlayCopy

    def RemovePath(self, agent_id):
        for EExt in self.EdgeExtensions:
            EExt.PurgeAgent(agent_id)

    def findNode(self, nodeID):
        node = self.NodeExtensions(nodeID==self.NER).node
        return node

    def findNodeExt(self, nodeID):
        node = self.NodeExtensions(nodeID==O.NER)
        return node

    def findNodeByName(self, nodeName):
        for node in self.Network.node_list:
            if node.name == nodeName:
                return node

    def findNodeExtByName(self, nodeName):
        node = self.NodeExtensions(nodeName==self.NER_Name)
        return node

    def findNeighbours(self, NExt):
        neighbours = []
        for N_id in NExt.node.neighbour_list:
            neighbours[end+1] = self.findNodeExt(N_id)
        return neighbours

    def findEdgeExt(self, ID1, ID2):
        edgeRet = self.EdgeExtensions(any([all(self.EER==[ID1,ID2]),\
                                           all(self.EER==[ID2,ID1])]))
        return edgeRet
