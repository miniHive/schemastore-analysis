from Visitor import Visitor
from KeyValueNode import KeyValueNode

class NullType_Visitor(Visitor):
    """! @brief Visitor to count the null type keyword in the Schema

        This visitor counts all appearances of the null type keyword in the schema.
        A null type in a JSON Schema document looks as follows:
        @code{.json}
            "type" : "null"
        @endcode
    """

    def __init__(self):
        """! @brief Constructor of NullType_Visitor.

            It sets the required count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a null type keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "type" and str(node.getValue()) == "null"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of null type keyword in the Schema
        """
        return self.cnt
