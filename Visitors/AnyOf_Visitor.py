from Visitor import Visitor
from KeyValueNode import KeyValueNode

class AnyOf_Visitor(Visitor):
    """! @brief Visitor to count the anyOf keyword in the Schema

        This visitor counts all appearances of the anyOf keyword in the schema.
    """
    def __init__(self):
        """! @brief Constructor of AnyOf_Visitor.

            It sets the anyOf count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a anyOf keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "anyOf"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of anyOf keyword in the Schema
        """
        return self.cnt
