from Visitor import Visitor
from KeyValueNode import KeyValueNode

class CountReferences_Visitor(Visitor):
    """! @brief Visitor to count the $ref keyword in the Schema

        This visitor counts all appearances of the $ref keyword in the schema.
    """
    def __init__(self):
        """! @brief Constructor of CountReference_Visitor.

            It sets the $ref count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a $ref keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if node.getName() == "$ref":
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of $ref keyword in the Schema
        """
        return self.cnt
