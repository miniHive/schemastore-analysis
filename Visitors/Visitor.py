import abc

class Visitor(abc.ABC):
    """! @brief This is an abstract parent class to implement the visitor pattern
    
        Different visitors are used in this project to analyse a JSON Schema Document.
        Basically, a visitor counts special elements or nodes in the Schema. All visitors
        have to implement the methods visit(self, node) and getCount(self).
    """
    @abc.abstractmethod
    def visit(self, node):
        """! @brief This is the basic visit method. Every visitor has to implement it.
        """
        pass

    @abc.abstractmethod
    def getCount(self):
        """! @brief This is the basic getter for the results of the visit. Every visitor has
                    to implement it.
        """
        pass

