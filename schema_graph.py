import sys
sys.path.append("./NodeTypes")
import networkx as nx
import matplotlib.pyplot as plt
from ObjectNode import ObjectNode
from ArrayNode import ArrayNode
from KeyValueNode import KeyValueNode
from graphviz import render
from Check_Ref_Visitor import Check_Ref_Visitor
import load_schema_from_web as web
from copy import deepcopy
from copy import copy


class schema_graph(nx.DiGraph):
    """! @brief This class implements a graph representing an JSON Schema document structure.
        
        The schema graph is a directed graph inherited from NetworkX's DiGraph. All Elements in a 
        JSON Schema are represented as one of three different nodes which inherit from SchemaNode.
        See the node classes' documentation for details.
        After setting up a schema graph, one can obtain different analysis tasks with internal methods
        and by using an implemented visitor pattern.
        Keyword counts are implemented by using different visitors.
        Other analysis tasks like the depth of a schema are implemented as internal methods of schema graphs.
        A schema graph is also capable of representing itself in DOT-Format and PDF-Format.
    """
    ## maximum number of resolving definitions rounds (see getSolvedGraph())
    max_count = 10

    def __init__(self, filename=""):
        """! @brief Constructor for a schema_graph.

            This function sets up different lists and properties that are used in internal anlysis methods.
            For details on the properties, please refered to the documentation of the method that uses them.

            @param filename     Path to JSON Schema document to be loaded into a schema_graph
        """
        super().__init__()
        ## JSON Schema document to be loaded into schema_graph
        self.filename = filename
        ## Store original JSON Schema dictionary to count references later on
        self.schema_dict = dict()
        ## $id tag of JSON Schema document
        self.id_tag = ""
        ## List of names of all unprocessed references in the schema_graph.
        ## Example: #/definitions/foo
        self.ref_name_list = []
        ## List of all unprocessed nodes representing references in the
        ## schema_graph.
        self.ref_node_list = []
        ## List of all allready processed names of references in the
        ## schema_graph
        self.res_node_list = []
        ## List of all allready processed nodes representing references in the
        ## schema_graph
        self.res_name_list = []
        ## Set of names of definitions sections to remove
        self.def_secs_name_set = set()
        ## Flag indicating whether the JSON Schema document represented by this
        ## graph is recursive
        self.has_recursions = False
        ## Schema_graph representation of this document with resolved
        ## references
        self.solved_graph = None
        ## Schema_graph representation of this document with extended (i.e.
        ## multiplied) resolved references
        self.ext_solved_graph = None
        ## Flag indicating whether an invalid reference was detected during
        self.invalid_reference_detected = False        
        ## Set to determine subgraphs (see getSuccessorSubgraph)
        self.sub_node_set = set()
        ## Node counter used to determine unique ID for every node
        self.node_count = 0

    def load_schema(self, schema_dict):
        """! @brief This function loads a dictionary representation of a schema into a schema_graph

            This includes converting the elements to the specific nodes.

            @param schema_dict      a dictionary representation of a JSON Schema document loaded by json module
        """

        self.schema_dict = schema_dict
        try:
            self.id_tag = schema_dict["$id"]
        except:
            self.id_tag = "no_tag"
            self.logmessage("No ID-Tag!")

        sg = self.load_subgraph(schema_dict, None)
        super().add_nodes_from(sg)
        super().add_edges_from(sg.edges)
    

    def load_subgraph(self, schema_pattern, name):
        """! @brief This function loads a subgraph from a so called schema_pattern.

            The function takes different types of elements as schema_patterns and produces the 
            corresponding nodes according to the type of schema_pattern. For example, an JSON
            Schema object is represented as a dictionary in schema_pattern and will be added 
            to the schema_graph as ObjecNode.
            This function operates recursively until all leafes of the tree are reached.

            @param  schema_pattern      JSON Schema Element of various typed
            @param  name                name of the resulting node of the schema_pattern

            @return The generated subgraph (nx.DiGraph), that results out of schema_pattern
        """

        # if no name is given, root node is asumed
        if name is None:
            name = "root"

        subgraph = nx.DiGraph()
        
        if isinstance(schema_pattern, dict):
            #Schema Objects
            oNode = ObjectNode(name)
            subgraph.add_node(oNode, name=name)

            for key in schema_pattern:
                # step into subnodes recursively
                h_graph = self.load_subgraph(schema_pattern[key], key)
                if h_graph is not None:
                    subgraph.add_nodes_from(h_graph)
                    subgraph.add_edges_from(h_graph.edges)
                    h_top_node = list(h_graph.nodes)[0]
                    subgraph.add_edge(oNode, h_top_node)
                else:
                    self.logmessage("Failed to load subgraph for Object " + name)

        elif isinstance(schema_pattern, list):
            #Schema Arrays
            arrNode = ArrayNode(name)
            subgraph.add_node(arrNode, name=name)
            
            for it in schema_pattern:
                #step into array nodes recursively
                h_graph = self.load_subgraph(it, str(it))
                if h_graph is not None:
                    subgraph.add_nodes_from(h_graph)
                    subgraph.add_edges_from(h_graph.edges)
                    h_top_node = list(h_graph.nodes)[0]
                    subgraph.add_edge(arrNode, h_top_node)
                else:
                    self.logmessage("Failed to load subgraph for list " + name)

        elif isinstance(schema_pattern, str) or isinstance(schema_pattern, int) or isinstance(schema_pattern, float):
            #Schema "properties"
            
            if (name == "$ref"):
                #$ref are shared ressources and shall be represented as such
                ref_name = name + schema_pattern
                if ref_name in self.ref_name_list:
                    #insert an edge from the previous node to the existing $ref
                    #node
                    index = self.ref_name_list.index(ref_name)
                    kvNode = self.ref_node_list[index] #adding an existing node to the graph is ignored by networkx
                else:
                    #insert new $ref node
                    self.ref_name_list.append(ref_name)
                    kvNode = KeyValueNode(name, schema_pattern)
                    self.ref_node_list.append(kvNode)
            else:
                kvNode = KeyValueNode(name, schema_pattern)

            subgraph.add_node(kvNode, name=name)

        elif schema_pattern is None:
            #null type is parsed to None by json library
            subgraph.add_node(KeyValueNode(name, "null"))
        else:
            #non-valid Schema document
            subgraph = None 

        return subgraph
    
    def show(self):
        """! @brief Shows a dirty version of the graph structure in a interactive window 
            @deprecated Use visualize(path)
        """
        nx.draw_shell(self, with_labels=False, font_weight='bold')

        plt.show()

    def visualize(self, path):
        """! @brief Creates a pdf and a DOT-format file with a proper visualisatzion of the graph.
        
            @param path     path to the dot-format file and the pdf
        """
        vis_graph = self.getVisGraph()
        
        nx.drawing.nx_pydot.write_dot(vis_graph, path + ".gv")
        render('dot', 'pdf', path + ".gv")

    def getVisGraph(self):
        """! @brief This function returns a DiGraph representation of the schema_graph for visualisation.
            This is necessary because Node can't be graphically represented as they get represented as Python 
            Objects with adresses. Therefor a DiGraph containing only the names of the nodes is generated 
            with this method.

            @return A nx.DiGraph with names of original nodes as nodes
        """
        vis_graph = nx.DiGraph()
        node_list = list(self.nodes)
        edge_list = list(self.edges)
        name_list = []
        
        # DiGraph nodes work with unique elements, names of nodes cant be the
        # same
        # if a node name already appeared, an integer is added to the name
        itrtr = 0
        for node in node_list:
            if (node is None):
                name = "None"
            elif node.getName() == "graph": #problem with gv file parsing
                name = "graf"
            else:
                name = node.getName()
            if name in name_list:
                name = name + str(itrtr)
            itrtr = itrtr + 1 

            name_list.append(name)

        vis_graph.add_nodes_from(name_list)

        for edge in edge_list:
            start_node = edge[0]
            end_node = edge[1]

            start_index = node_list.index(start_node)
            stop_index = node_list.index(end_node)

            vis_graph.add_edge(name_list[start_index], name_list[stop_index])

        return vis_graph

    def getFilename(self):
        """! @brief Getter for the filename 
            @return self.filename
        """
        return self.filename

    def depth(self, graph):
        """! @brief Determine the depth of graph by checking all path lengths to all leaf nodes.
            This function is using the simple paths method of NetworkX module. It gets all pathes
            to all leaf nodes of the graph and stores their length in a list. The maximum of this list
            is returned as depth.
            @param  graph   schema_graph to determine depth of
            @return The depth of the given graph
        """ 
        kvNodeList = list()
        path_length_list = list()
        root_node = list(graph.nodes)[0]
  
        for node in graph.nodes:
            # get all leaf nodes which have to be kvNodes and vice versa
            if isinstance(node, KeyValueNode):
                for path in nx.all_simple_paths(graph, root_node, node):
                    path_length_list.append(len(path))
             
        return max(path_length_list)

    def depth_schema(self):
        """! @brief Return the depth of the JSON Schema document.
        
            This is equivalent to the depth of the schema_graph itself.

            @return Depth of the JSON Schema document represented by this schema_graph.
        """
        return self.depth(self)

    def depth_resolvedReferenceGraph(self):
        """! @brief Determine the depth of the resolved reference graph of the Schema document.
            This means to solve the $refs and inserting the linked (sub) graph.
            If recursion are in the graph, the length of the bigest cycle is returned.
            
            @return Depth or max cycle length of the resolved reference graph
        """
        self.solved_graph = self.getResolvedReferenceGraph()

        if self.check_recursion(self.solved_graph):
            return self.max_cycle_length(self.solved_graph)
        else:
            return self.depth(self.solved_graph)

    def shortest_cycle(self):
        """! @brief Return the shortest cycle in the resolved graph or 0 if schema is not recursive

            @return Shortest Cycle in a recursive graph or 0 for non-recursive graphs
        """

        self.solved_graph = self.getResolvedReferenceGraph()

        if self.check_recursion(self.solved_graph):
            return self.min_cycle_length(self.solved_graph)
        else:
            return 0
    
    def updateRefNameList(self):
        """! @brief A function to update schema_graph's reference name and node lists.

            This function clears the internal ref_name_list, ref_node_list, res_name_list and
            res_node_list. They contain reference names and nodes and already resolved names and nodes.
            The ref_name_list and ref_node_list are filled with all references in the graph.
        """
        self.ref_name_list = list()
        self.ref_node_list = list()
        self.res_name_list = list()
        self.res_node_list = list()
        for node in self.nodes:
            name = node.getName()
            if (name == "$ref"):
                #$ref are shared ressources and shall be represented as such
                ref_name = name + node.getValue()
                if ref_name not in self.ref_name_list:
                    self.ref_name_list.append(ref_name)
                    self.ref_node_list.append(node)

    def getResolvedReferenceGraph(self):
        """! @brief This function creates the resolved reference graph. 
            
            The resolved reference graph is created by the method getSolvedGraph(..).

            @return The resolved reference graph.
        """
        if self.solved_graph is None:
            self.solved_graph = self.getSolvedGraph(0)
            
        return self.solved_graph

    def getSolvedGraph(self, count=0):      
        """! @brief This function creates the resolved reference graph. 
            
            The resolved reference graph is a version of the original schema_graph, where all reference
            nodes are replaced by the sub-graph they referenced. Internal definitions are loaded from
            definitions sections and copied to the reference. This can happen only once as $ref-nodes
            are unique and treaten as "shared resource". External references are loaded from the web.
            If a sub-graph contains references either, the algorithm searches for equal references in 
            the original schema_graph. These can be already resolved and therefor in res_name_list and
            res_node_list or they are to be resolved later and stored in ref_name_list and ref_node_list.
            If there are such references, the algorithm treats them as same unique references.
            This is used to detect recursive structures in the schema documents.

            @param  count   Integer value to determine how often this method was called from itself.
                            Multiple rounds can be necessary to resolve all references of subgraphs.
                            For the initial call of this function, always use count = 0.


            @return The resolved reference graph.
        """
        
        if self.solved_graph is not None:
            return self.solved_graph

        new_ref_round = False #determine whether this procedure has to be re-run
        count = count + 1 #count iterations of this method to newly created graphs
        
        if count == 1:
            self.updateRefNameList()

        if(len(self.ref_name_list) != 0):
            # Depth of JSON only differs from Schema's Depth if Schema contains
            # $refs
            solved_graph = deepcopy(self) # 'real' copy, no connection between objects
            it_ref_node_list = copy(solved_graph.ref_node_list)
            for it_node in  it_ref_node_list:
                node = it_node #adding in lists --> capability to change iterating node
                if isinstance(node, KeyValueNode):
                    #only KeyValue - Nodes can be $ref Nodes
                    if node.getName() == "$ref":
                        if node.getValue()[0] == "#":
                            ref_name = node.getValue()
                            defsec_name = self.store_defsecname(node.getValue()) #add section to list of known definition sections
                            #local reference
                            internal_valid_ref_flag = True
                            #find referenced node in solved_graph
                            def_node = solved_graph.getNodeByPath(ref_name)

                            if not def_node is None:
                                predecs = solved_graph.predecessors(node)    
                            
                                for pred in predecs:
                                    solved_graph.add_edge(pred, def_node)

                                solved_graph.remove_node(node)

                                node = def_node # neccessary for adding it to res_node_list

                                internal_valid_ref_flag = False 
                            else:
                                internal_valid_ref_flag = True
                            
                            self.invalid_reference_detected = self.invalid_reference_detected | internal_valid_ref_flag
                        elif node.getValue()[:4] == "http":
                            if node.getValue() == self.id_tag:
                                #recursive to self
                                predecs = solved_graph.predecessors(node)
                                solved_graph.remove_node(node)
                                for pred in predecs:
                                    solved_graph.add_edge(pred, list(solved_graph.nodes)[0])
                                node = list(solved_graph.nodes)[0] #neccessary for adding it to res_node_list
                            
                            else:#external reference, recursions possible
                                schema_dict = web.load_schema(node.getValue(), open("../../schema_graph.log", 'a+'))
                                if not schema_dict is None:
                                    subgraph = schema_graph(self.getFilename())
                                    subgraph.load_schema(schema_dict)    
                                    
                                    subgraph = subgraph.resolveInternalReferences(node.getValue())
                                    if subgraph.invalid_reference_detected == True:
                                        self.invalid_reference_detected = True
                                        self.logmessage("Invalid internal reference in externaly referenced file!")

                                    # include references as same node
                                    for ref_name in subgraph.ref_name_list:
                                        if ref_name in solved_graph.ref_name_list:
                                            if ref_name == ("$ref" + node.getValue()):
                                                # recursive reference to this
                                                # subgraph --> replace $ref
                                                # with root
                                                idx_rec_ref = subgraph.ref_name_list.index(ref_name)
                                                predecs_rec_ref = subgraph.predecessors(subgraph.ref_node_list[idx_rec_ref])
                                                subgraph.remove_node(subgraph.ref_node_list[idx_rec_ref])
                                                sub_top_node = list(subgraph.nodes)[0]
                                                for pred_rec_ref in predecs_rec_ref:
                                                    subgraph.add_edge(pred_rec_ref, sub_top_node)
                                            else:
                                                # reference to another party
                                                # already in graph
                                                idx_top = solved_graph.ref_name_list.index(ref_name)
                                                idx_sub = subgraph.ref_name_list.index(ref_name)
                                                sub_node = subgraph.ref_node_list[idx_sub]
                                                top_node = solved_graph.ref_node_list[idx_top]
                                                # refs are leaves in subgraph,
                                                # so no sucessors available
                                                predecs_sub = subgraph.predecessors(sub_node)
                                                subgraph.remove_node(sub_node)
                                                subgraph.add_node(top_node)
                                                for pred_node in predecs_sub:
                                                    subgraph.add_edge(pred_node, top_node)

                                        elif ref_name in solved_graph.res_name_list:
                                            # reference was already solved -->
                                            # connect to its subgraph's root
                                            idx_top = solved_graph.res_name_list.index(ref_name)
                                            idx_sub = subgraph.ref_name_list.index(ref_name)
                                            sub_node = subgraph.ref_node_list[idx_sub]
                                            top_node = solved_graph.res_node_list[idx_top]
                                            # refs are leaves in subgraph, so
                                            # no sucessors available
                                            predecs_sub = subgraph.predecessors(sub_node)
                                            subgraph.remove_node(sub_node)                                        
                                            subgraph.add_node(top_node)
                                            for pred_node in predecs_sub:
                                                subgraph.add_edge(pred_node, top_node)
                                        
                                        else: #ref_name never occured
                                            new_ref_round = True
                                            ##currently unknown reference -->
                                            ##recurse into subgraph to resolve
                                            ##it
                                            ref_node = subgraph.ref_node_list[subgraph.ref_name_list.index(ref_name)]
                                            solved_graph.ref_name_list.append(ref_name)
                                            solved_graph.ref_node_list.append(ref_node)
                                        
                                        #end for ref_name in
                                        #subgraph.ref_name_list
                                    idx_rep = solved_graph.ref_name_list.index("$ref" + it_node.getValue())
                                    rep_node = solved_graph.ref_node_list[idx_rep]
                                    predecs = solved_graph.predecessors(rep_node)
                                    solved_graph.remove_node(rep_node)
                                    solved_graph.add_nodes_from(subgraph)
                                    solved_graph.add_edges_from(subgraph.edges)
                                    sub_top_node = list(subgraph.nodes)[0]
                                    for pred_node in predecs:
                                        solved_graph.add_edge(pred_node, sub_top_node)
                                    node = sub_top_node #neccesary for adding it to res_node_list
                                else:
                                    self.invalid_reference_detected = True
                                    self.logmessage("Invalid external reference")
                        else:
                            #undefined reference detected
                            self.invalid_reference_detected = True
                            self.logmessage("Undefined internal reference")
                    #end if isinstance(node, KeyValueNode)
                #reference was solved --> remove from reference list and add it
                #to resolved references list
                ref_idx = solved_graph.ref_name_list.index(it_node.getName() + it_node.getValue())
                solved_graph.ref_name_list.remove(it_node.getName() + it_node.getValue()) #original iterated node
                solved_graph.ref_node_list.remove(solved_graph.ref_node_list[ref_idx])
                solved_graph.res_name_list.append(it_node.getName() + it_node.getValue()) #sub_top_node reference
                solved_graph.res_node_list.append(node)
                #end for it_node in solved_graph.ref_node_list
            if new_ref_round and (count <= schema_graph.max_count):
                self.solved_graph = solved_graph.getSolvedGraph(count)
                return self.solved_graph
            else: #no new references added
                self.solved_graph = solved_graph
                return solved_graph
        else: #no refs in graph
            self.solved_graph = self
            return self

    def resolveInternalReferences(self, webaddress):
        """! @brief This private function is resolves internal references only

            This is used to resolve internal references of externaly included files. 
        """
        self.updateRefNameList()
        webaddress = webaddress.split('#')[0]
        solved_graph = self #if no internal references, return original

        if(len(self.ref_name_list) != 0):
            # Depth of JSON only differs from Schema's Depth if Schema contains
            # $refs
            solved_graph = deepcopy(self) # 'real' copy, no connection between objects
            it_ref_node_list = copy(solved_graph.ref_node_list)
            for it_node in  it_ref_node_list:
                node = it_node #adding in lists --> capability to change iterating node
                if isinstance(node, KeyValueNode):
                    #only KeyValue - Nodes can be $ref Nodes
                    if node.getName() == "$ref":
                        if node.getValue()[0] == "#":
                            ref_name = node.getValue()
                            defsec_name = self.store_defsecname(node.getValue()) #add section to list of known definition sections
                            #local reference
                            internal_valid_ref_flag = True
                            #find referenced node in solved_graph
                            def_node = solved_graph.getNodeByPath(ref_name)

                            if def_node is None:
                                #not found, maybe in complete document
                                schema_dict = web.load_schema(webaddress + ref_name, open("../../schema_graph.log", 'a+'))

                                if not schema_dict is None:
                                    #convert to external address
                                    old_name = it_node.getName() + it_node.getValue()
                                    node.setValue(webaddress + ref_name)
                                    ref_idx = solved_graph.ref_name_list.index(old_name)
                                    solved_graph.ref_name_list.remove(old_name) #original iterated node
                                    solved_graph.ref_name_list.insert(ref_idx, node.getName() + node.getValue())
                                    continue

                            if not def_node is None:
                                predecs = solved_graph.predecessors(node)    
                            
                                for pred in predecs:
                                    solved_graph.add_edge(pred, def_node)

                                solved_graph.remove_node(node)

                                 #reference was solved --> remove from
                                 #reference list and add it to resolved
                                 #references list
                                ref_idx = solved_graph.ref_name_list.index(it_node.getName() + it_node.getValue())
                                solved_graph.ref_name_list.remove(it_node.getName() + it_node.getValue()) #original iterated node
                                solved_graph.ref_node_list.remove(solved_graph.ref_node_list[ref_idx])
                                solved_graph.res_name_list.append(it_node.getName() + it_node.getValue()) #sub_top_node reference
                                solved_graph.res_node_list.append(def_node)

                                internal_valid_ref_flag = False 
                            else:
                                internal_valid_ref_flag = True
                            solved_graph.invalid_reference_detected = solved_graph.invalid_reference_detected | internal_valid_ref_flag
                    else:
                        # external reference, nothing to do
                        pass
        return solved_graph

    def visit_tree(self, visitor):
        """! @brief Traverse the tree using visitor pattern.
            
            @param  visitor A vistitor to visit the schema graph. It has to be a instance inherited of Visitor.py
        """
        for node in self.nodes:
            node.accept(visitor)

    def visit_ext_graph(self, visitor):
        """! @brief Traverse extanded reference graph using visitor pattern.
            
            @param  visitor A vistitor to visit the schema graph. It has to be a instance inherited of Visitor.py
        """
        if self.ext_solved_graph is None:
            self.ext_solved_graph = self.getExtendedRefGraph()

        for node in self.ext_solved_graph.nodes:
            node.accept(visitor)

    def visit_res_graph(self, visitor):
        """! @brief Traverse resolved reference graph using the visitor pattern.

            @param visitor A visitor to visit the schema graph. It has to be a instance inherited of Visitor.py
        """

        if self.solved_graph is None:
            self.solved_graph = self.getResolvedReferenceGraph()

        for node in self.solved_graph:
            node.accept(visitor)
        

    def getFanInList(self):
        """! @brief This function returns a list of all element's fan-in values 
        
            @return List of Fan-in values of all elements in the original schema graph
        """
        fan_in_list = []
        for node in  self.nodes:
            fan_in_list.append(len(list(self.predecessors(node))))

        return fan_in_list


    def getMaxFanIn(self):
        """! @brief Get the maximum fan in of any node in the graph.
       
            @return Maximum fan-in value of any node in the graph.
        """        
        return max(self.getFanInList())

    def getFanOutList(self):
        """! @brief This function returns a list of all element's fan-out values excluding root 
        
            @return List of Fan-out values of all elements in the original schema graph excluding root node.
        """
        fan_out_list = []
        for node in self.nodes:
            if (node.getName() != "root"): 
                fan_out_list.append(len(list(self.successors(node))))

        return fan_out_list

    def getMaxFanOut(self):
        """! @brief Get the maximum fan out of any node in the graph excluding root.
       
            @return Maximum fan-out value of any node in the graph excluding root
        """
        return max(self.getFanOutList())

    def check_recursion(self, *args):
        """! @brief Checks whether the schema document contains recursions.

            This function loads the resolved reference graph by using the method getResolvedReferenceGraph()
            and converts it to a clean nx.DiGraph() to use the class's internal cycle detection method.
            By providing an schema_graph in args[0] the user can check args[0] for recursions.

            @param  *args    Optional list of arguments. If provided args[0] has to be a schema graph

            @return Boolean value to determine whether the schema document contains recursions.
        """

        #without converting it to a clean DiGraph, the
        #generator returned by simple_cycles doesn't work

        if(len(args) == 0):
            g = nx.DiGraph(self.getResolvedReferenceGraph().edges)
        else:
            g = nx.DiGraph(args[0].edges)
        
        if len(list(nx.simple_cycles(g))) != 0:
            self.has_recursions = True
        else:
            self.has_recursions = False

        return self.has_recursions

    def max_cycle_length(self, recursive_graph):
        """! @brief Returns the length of the longest cycle in a given recursive graph.
            @param  recursive_graph A schema_graph that contains recursions
            @return The lenght of the longest cycle in the recursive graph.
        """
        g = nx.DiGraph(recursive_graph.edges)
        len_list = list()
        
        for cycle in nx.simple_cycles(g):
            len_list.append(len(list(cycle)))

        return max(len_list)

    def min_cycle_length(self, recursive_graph):
        """! @brief Returns the length of the shortest cycle in a given recursive graph.
            @param  recursive_graph A schema_graph that contains recursions
            @return The lenght of the shortest cycle in the recursive graph.
        """
        g = nx.DiGraph(recursive_graph.edges)
        len_list = list()
        
        for cycle in nx.simple_cycles(g):
            len_list.append(len(list(cycle)))

        return min(len_list)

    def getNumberCycles(self):
        """! @brief Return the number of cycles in the resolved reference graph of self. 
            The function creates the resolved reference graph and returns the number of cycles
            in the resolved reference graph.

            @return Number of cycles in the resolved reference graph of self.
        """
        g = nx.DiGraph(self.getResolvedReferenceGraph().edges)

        return len(list(nx.simple_cycles(g)))

    def getNumberPathes(self):
        """! @brief Return the number of simple pathes included in the resolved reference graph. 

            This is equivalent to the number of leafes in the tree. Thats why this function counts
            the number of KeyValueNodes in the graph. KeyValueNodes are leafes and vice versa.

            @return The number of pathes in the resolved refernce graph of self            
        """
        count = 0
        solved_graph = self.getResolvedReferenceGraph()
        for node in solved_graph.nodes:
            if isinstance(node, KeyValueNode):
                count += 1

        return count

    def getWidth(self):
        """! @brief Return the width of the schema_graph which is equivalent to the number of 
            leafes of the graph 
            
            @return The width of the schema graph defined as number of leafes.
            
         """
        count = 0

        for node in self.nodes:
            if isinstance(node, KeyValueNode):
                count += 1

        return count
    

    def check_reachability(self):
        """! @brief This function checks if the graph is fully reachable. 
        
            Reachability is defined as usage of defintions. Reachability is given if all defined defintions
            in the schema are referenced at least once. Reachability is not given if at least one defined
            defintions is not at least referenced once.
            This function uses the internal set self.def_secs_name_set which contains the names of all defintions
            sections. It has to be set before using this method. It is created in getResolvedReferenceGraph().

            @return Reachability of the graph as defined above.
        """

        self.solved_graph = self.getResolvedReferenceGraph()
        reachability = True
        
        if not self.invalid_reference_detected:
            for def_name in self.def_secs_name_set:
                def_sec_node = self.getNodeByName(def_name)
                if not def_sec_node is None:
                    defs_in_section = self.successors(def_sec_node)
                    for def_node in defs_in_section:
                        if not (("$ref#/" + def_name + "/" + def_node.getName()) in self.solved_graph.res_name_list):
                            reachability = False
                            return reachability
                        else:
                            if None == self.solved_graph.getNodeByName(def_node.getName()): #refs in definition sections get resolved entries even if not used elsewhere
                                reachability = False
                                return reachability 
                else:
                    reachability = False
                    break
        else:
            reachability = False

        return reachability

    def getNoReferences(self):
        """! @brief This function counts all references in the JSON Schema document.

            The method iterates over the raw dictionary of the Schema document to find all references.
            This has to be done, because the schema_graph itself interprets equal references as one node.
            That would not lead to the intended result.

            @return An integer value representing the number of references in the JSON schema document
        """
        return self.search_references(self.schema_dict)

    def search_references(self, schema_pattern, parentName="none"):
        """! @brief This private function is used to find all references in the JSON Schema document in a 
                    recursive manner.

            This method shall only be used by self.getNoReferences(self). Beginning with the original schema dictionary
            the method goes recursively into the schema and finds all occurences of references.

            @param  schema_pattern  Part of the schema_dictionary to step into
            @param  parentName      Name of the parent "node" to identify $ref

            @return Number of references in the currrent observed part of the schema_dictionary
        """

        ## return value
        ref_count = 0

        if isinstance(schema_pattern, dict):
            for key in schema_pattern:
                ref_count += self.search_references(schema_pattern[key], str(key))

        elif isinstance(schema_pattern, list):
            for item in schema_pattern:
                ref_count += self.search_references(item, str(item))
            
        elif (isinstance(schema_pattern, str) and (parentName == "$ref")):
            ref_count += 1
        else:
            # schema_pattern is either int, float, or None (null in JSON
            # Schema) and therefore no reference
            # do nothing
            pass

        return ref_count

                     
    def getInvalidReferenceFlag(self):
        """! @brief Getter for invalid reference detection flag.
       
            @return Invalid reference detection flag - Set if invalid references were detected
        """
        return self.invalid_reference_detected

    def store_defsecname(self, ref_name):
        """! @brief This function stores the name of the definition section in self.def_secs_name_set.
            It returns the stored name.
        
            @return The stored definition section name
        """
        str_part_list = ref_name.split('/')
        if len(str_part_list) > 1:
            #ref_name come in the form of "#/defname/refname", so second entry
            #in list is the defname
            self.def_secs_name_set.add(str_part_list[1]) #sets store entries unique
        
            return str_part_list[1]
        else:
            # root referenced by "#"
            # do not store this as defintions section
            return "#"

    def getNodeByName(self, name):
        """! @brief This function searches the given name in all nodes and returns the first node with the given name.
            
            @param  name    Node's name to search for.

            @return First node found with the given name.
        """
        for node in self.nodes:
            if node.getName() == name:
                return node
        return None # in case name was not found, return None


    def getNodeByPath(self, path):
        """! @brief This function returns the node located at the end of path

            @param  path    Path to node as string, e.g. #/defintions/foo, when Node "foo" is searched

            @return  Searched node in self or None if not found
        """

        path_parts = path.split('/')
        node = None
        valid_path = True

        for part in path_parts:
            if part == '#':
                node = list(self.nodes)[0]
            else:
                valid_path = False #set true if successor found
                if not node is None:
                    for suc in self.successors(node):
                        if suc.getName() == part:
                            node = suc
                            valid_path = True
                            break # successor found, stop searching
                else:
                    # empty reference, return None
                    # this is treaten as invalid reference later on
                    break
            if valid_path == False:
                node = None
                break
        return node

    def logmessage(self, message):
        """! @brief This function writes a message to the logfile.

            The function write the filename and the given message to the logfile "../../schema_graph.log".
            
            @param  message Message to write to the logfile        

        """
        logfile = open("../../schema_graph.log", 'a+')
        logfile.write(self.filename + ": " + message + "\n")
        logfile.close()

    def getExtendedRefGraph(self):
        """! @brief This function is used to create a graph with extended references.
            
            This is done by multiplying the every reference to generate multiple reference node with one predecessor only.
            Then, a resolved graph is generated for this extended graph. The result is stored in self.ext_solved_graph.

            @return The extended resolved reference graph
        """

        if self.ext_solved_graph is None:
            ext_graph = deepcopy(self.getResolvedReferenceGraph())

            ext_graph.setNodeIDs


            ext_orig_nodes = list(ext_graph.nodes)
            for node in ext_orig_nodes:
                predecs = list(ext_graph.predecessors(node))
                if ((len(predecs)) > 1):
                    subgraph = ext_graph.getSuccessorSubgraph(node)
                    # cycles in subgraphs can lead to _unconnected_ cliques in
                    # the extendend graph
                    # prevention is applied by removing _cyclic predecessors_
                    # from the predecs list
                    predec_copy = predecs
                    for pred_node in predec_copy:
                        if pred_node in subgraph.nodes:
                            predecs.remove(pred_node)                        

                    for pred in predecs[1:]: #let the first edge lead to the originial subgraph
                        subgraph_copy = deepcopy(subgraph)
                        # search sub_root in subgraph
                        sub_root = None
                        for sub_node in subgraph_copy.nodes:
                            if sub_node.getID() is node.getID():
                                sub_root = sub_node
                                break # root found # no checking for None necessary because node with right ID
                                      # surely exists
                    
                        # copy the new subgraph into the extended graph, remove
                        # the edge to shared reference and add new edge
                        # to the subgraph
                        ext_graph.add_edges_from(subgraph_copy.edges)
                        ext_graph.remove_edge(pred, node)
                        ext_graph.add_edge(pred, sub_root)
            self.ext_solved_graph = ext_graph

        return self.ext_solved_graph

    def getSuccessorSubgraph(self, ref_node):
        """! @brief This function returns a subgraph with ref_node as root.
            All successors and successors of successors (and so on) of ref_node are 
            determined using the recursive function successor_list and the resulting
            subgraph is returned.

            @param ref_node     Root node of subgraph

            @return The resulting subgraph
        """

        self.sub_node_set = set()

        self.successor_list(ref_node)
            
        return self.subgraph(self.sub_node_set)

    def successor_list(self, ref_node):    
        """! @brief This private function fills the successor list self.sub_node_set in a recursive manner.
            It is called by getSuccessorSubgraph(..). This function ensures that self.sub_node_set is empty in advance.

            @param ref_node Node to find and add successors

            @return None
        """

        if not ref_node in self.sub_node_set:
            self.sub_node_set.add(ref_node)

        for successor in self.successors(ref_node):
            if not successor in self.sub_node_set:
                self.sub_node_set.add(successor)
                self.successor_list(successor)

    def setNodeIDs(self):
        """! @brief This functions sets unique IDs for each node in the graph

            This is necessary to find the correct sub roots while expanding the graph and generating subgraphs.

            @param void
            @return Nothing
        """
        i = 0
        for node in self.nodes:
            node.setID(i)
            i += 1

    def getBlowUpFactor(self):
       """! @brief This function calculates a blow-up factor as proxy-metrics for how compact the schema is designed.
           
           When authors of schemas make use of references, they can create very tight schemas. The blow-up factor is a proxy-metrics
           for the "tightness" of a schema. It is calculated as the number of nodes after expanding the graph (see getExtendedRefGraph() )
           divided by the number of nodes in the original schema graph. 

           @return A Blow-Up Factor as proxy-metrics for the "tightness" of a schema
       """

       if not self.check_recursion():
           if self.ext_solved_graph is None:
               self.ext_solved_graph = self.getExtendedRefGraph()
       
           if self.solved_graph is None:
               self.solved_graph = self.getResGraph()

           ret_val = (len(list(self.ext_solved_graph.nodes)) / len(list(self.solved_graph.nodes)))

       else:
           ret_val = 0

       return ret_val
