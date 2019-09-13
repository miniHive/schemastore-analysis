from Visitor import Visitor
from KeyValueNode import KeyValueNode

class Enum_Visitor(Visitor):
    """! @brief Visitor to count the enum keyword in the Schema

        This visitor counts all appearances of the enum keyword in the schema.
    """
    def __init__(self):
        """! @brief Constructor of Enum_Visitor.

            It sets the enum count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a enum keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "enum"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of enum keyword in the Schema
        """
        return self.cnt
