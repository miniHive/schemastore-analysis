from Visitor import Visitor
from KeyValueNode import KeyValueNode

class ValueRestriction_Visitor(Visitor):
    """! @brief Visitor to count all value restrictions for numbers and integers or arrays in the schema.
        
        A value restriction can be upper and lower limits for integers and numbers or arrays in the schema.
        The key words searched for are:
            - minimum
            - maximum
            - minLength
            - maxLength
            - exclusiveMinimum
            - exclusiveMaximum
    """
    def __init__(self):
        """! @brief Constructor of the ValueRestriction_Visitor.

            Sets initial count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation.
            This function visits a node in the graph and increments the count if the node's name
            is a value restriction keyword as specified by the class description.

            @param  node    The node to visit. It has to be a inherited class of SchemaNode.
        """
        param_list = ["minimum", "maximum", "minLength", "maxLength", "exclusiveMinimum", "exclusiveMaximum"]
        if (node.getName() in param_list):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the visit result implementation
            
            @return The amount of value restriction keywords in the Schema.
        """
        return self.cnt
