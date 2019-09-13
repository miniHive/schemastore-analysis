from Visitor import Visitor
from KeyValueNode import KeyValueNode

class Object_Visitor(Visitor):
    """! @brief Visitor to count object types in Schema

        This visitor counts all appearances of the object type keyword in the schema.
        A object type in a Schema looks as follows:

        @code{.json} "type" : "object" @endcode
    """

    def __init__(self):
        """! @brief Constructor of Object_Visitor.

            It sets the object type count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a object type keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if (node.getName() == "type" and str(node.getValue()) == "object"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of object type keyword in the Schema
        """
        return self.cnt
