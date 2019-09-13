import abc

class SchemaNode(abc.ABC):
    """! @brief Abstract class Schema Node for nodes in schema_graph."""

    @abc.abstractmethod
    def getName(self):
        pass

    @abc.abstractmethod
    def getValue(self):
        pass
    @abc.abstractclassmethod
    def setValue(self, value):
        pass

    @abc.abstractmethod
    def accept(self, visitor):
        pass 

    @abc.abstractmethod
    def getID(self):
        pass

    @abc.abstractmethod
    def setID(self, id):
        pass




