from Visitor import Visitor

class Check_Ref_Visitor(Visitor):
    """! @brief This visitor checks whether there are references in the JSON Schema.
        The result value is True if and only if there is at least one $ref in the JSON Schema.
    """

    def __init__(self):
        """! @brief Constructor of Check_Ref_Visitor.

            It sets the boolean result value to False.
        """
        self.contains_ref = False

    def visit(self, node):
        """! @brief Basic visit method implementation.

            This function visits a node and changes the result value to True if the node is a representation
            of a $ref keyword in the schema.

            @param  node    Node to visit. This has to be a inherited type from SchemaNode.
        """
        if node.getName() == "$ref":
            self.contains_ref = True

    def getCount(self): 
        """! @brief Basic getter for the result value implementation

            @return Integer conversion of the boolean result value.
                    Result value is True if and only if the Schema contains at least one $ref keyword.
        """
        return int(self.contains_ref) 

    def contains_ref(self):
        """! @brief Additional getter for the boolean result value

            @return True if the Schema contains at least one $ref keyword.
                    False otherwise.
        """
        return self.concontains_ref

