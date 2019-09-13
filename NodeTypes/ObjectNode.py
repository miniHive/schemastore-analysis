from SchemaNode import SchemaNode

class ObjectNode(SchemaNode):
    """! @brief Class to represent objects in JSON Schema Documents as Nodes in the schema graph.
    """
    def __init__(self, name):
        self.name = name
        self.nodeID = 0

    def getName(self):
        return self.name

    def getValue(self):
        return ""

    def setValue(self, value):
        pass

    def accept(self, visitor):
        visitor.visit(self)

    def getID(self):
        return self.nodeID

    def setID(self, id):
        self.nodeID = id