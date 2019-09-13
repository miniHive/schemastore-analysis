from Visitor import Visitor
from KeyValueNode import KeyValueNode

class Pattern_Visitor(Visitor):
    """! @brief Visitor to count pattern keywords in Schema.
        The visitor counts all appearances of the "pattern" keyword and the "patternProperties"
        keyword. 
    """
    def __init__(self):
        """! @brief Constructor of Pattern_Visitor
            Sets the counter result value to zero
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and increments the counter if the node is a representation
            of a pattern keywords in the schema like defined in the class decsription.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        param_list = ["pattern", "patternProperties"]
        if (node.getName() in param_list):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation

            @return The amount of appearances of pattern keywords in the Schema as 
                    defined in the class decsription
        """
        return self.cnt
