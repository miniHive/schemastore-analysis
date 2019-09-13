from Visitor import Visitor
from KeyValueNode import KeyValueNode

class Number_Visitor(Visitor):
    """! @brief Visitor to count the number or integer type keyword in the Schema

        This visitor counts all appearances of the keywords number or integer in the schema.
        A number or integer type keyword in a JSON Schema document looks as follows
        @code{.json}
            "type" : "number"
            "type" : "integer"
        @endcode
    """
    
    def __init__(self):
        """! @brief Constructor of Number_Visitor.

            It sets the number count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a number or integer type keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "type" and (str(node.getValue()) == "number") or (str(node.getValue()) == "integer")):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of integer or number type keyword in the Schema
        """
        return self.cnt
