from Visitor import Visitor
from KeyValueNode import KeyValueNode

class Count_String_Visitor(Visitor):
    """! @brief Visitor to count the string type keyword in the Schema

        This visitor counts all appearances of the string type keyword in the schema.

        A string type keyword in a JSON Schema document looks as follows:
        @code{.json}
            "type" : "string"
        @endcode
    """
    def __init__(self):
        """! @brief Constructor of Count_String_Visitor.

            It sets the string count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a string type keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "type" and str(node.getValue()) == "string"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of string type keyword in the Schema
        """
        return self.cnt
