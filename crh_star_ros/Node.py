#To keep with topological_navigation, this will remain as Node)
class Node():
    def __init__(self, prettyName, position):
        #self.id

        #self.name
        self.prettyName = prettyName

        self.position = position

        self.neighbour_list = []
        #self.neighbourPrettyName
