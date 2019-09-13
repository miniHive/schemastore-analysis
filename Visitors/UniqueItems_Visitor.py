from Visitor import Visitor
from KeyValueNode import KeyValueNode

class UniqueItems_Visitor(Visitor):
    """! @brief Visitor to count uniqueItems key word in a Schema.
        
        This visitor counts the appearances of the uniqueItems keyword of JSON Schema.
    """
    def __init__(self):
        """! @brief Constructor of the UniqueItems_Visitor.
            It sets the unique items count result value to zero.
        """
        self.cnt = 0

    def visit(self, node):
        """! @brief Basic visit method implementation of UniqueItems_Visitor.
            
            This function visits a node and increments the counter if the node represents
            a uniqueItems keyword in the JSON Schema.

            @param  node    Node to visit. This node has be a inherited type of SchemaNode
        """
        if (node.getName() == "uniqueItems"):
            self.cnt = self.cnt + 1

    def getCount(self):
        """! @brief Basic getter for the result value implementation
            
            @return The amount of uniqueItems appearances in the Schema
        """
        return self.cnt
