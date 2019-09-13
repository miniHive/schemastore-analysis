from SchemaNode import SchemaNode

class ArrayNode(SchemaNode):
    """! @brief This class is used to represent JSON Schema arrays as nodes in the schema_graph."""
    
    def __init__(self, name):
        ## Node's name
        self.name = name
        ## ID to unique representation when expanding the tree
        ## it is initialized when needed
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


