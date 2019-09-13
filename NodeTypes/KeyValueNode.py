from SchemaNode import SchemaNode

class KeyValueNode(SchemaNode):
    """! @brief This class is used to represent Key-Value pairs of JSON Schema Documents as nodes in
                the schema graph
        A key-value pair looks as follows in the schema document:
        @code{.json}
            "type" : "string"
        @endcode
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.nodeID = 0 

    def getName(self):
        return self.name

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def accept(self, visitor):
        visitor.visit(self)

    def getID(self):
        return self.nodeID

    def setID(self, id):
        self.nodeID = id


