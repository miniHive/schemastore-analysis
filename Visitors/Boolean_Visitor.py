from Visitor import Visitor
from KeyValueNode import KeyValueNode

class Boolean_Visitor(Visitor):
    """! @brief Visitor to count the boolean type keyword in the Schema

        This visitor counts all appearances of the boolean type keyword in the schema.

        A boolean type keyword in a JSON Schema document looks as follows:
        @code{.json}
            "type" : "boolean"
        @endcode
    """

    def __init__(self):
        """! @brief Constructor of Boolean_Visitor.

            It sets the boolean type count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a boolean type keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "type" and str(node.getValue()) == "boolean"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of boolean type keyword in the Schema
        """
        return self.cnt
