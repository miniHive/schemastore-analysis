from Visitor import Visitor
from KeyValueNode import KeyValueNode

class AllOf_Visitor(Visitor):
    """! @brief Visitor to count the allOf keyword in the Schema

        This visitor counts all appearances of the allOf keyword in the schema.
    """
    def __init__(self):
        """! @brief Constructor of AllOf_Visitor.

            It sets the allOf count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a allOf keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "allOf"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of allOf keyword in the Schema
        """
        return self.cnt
