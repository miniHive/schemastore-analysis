import threading as th
import multiprocessing as mp
import json
import io
import os
import validity_constants as validity
from itertools import count
import schema_graph
from schema_checker import schema_checker
from load_schema_from_web import load_schema

from Count_String_Visitor import Count_String_Visitor
from AdditionalProperties_Visitor import AdditionalProperties_Visitor
from AllOf_Visitor import AllOf_Visitor
from AnyOf_Visitor import AnyOf_Visitor
from Arrays_Visitor import Arrays_Visitor
from CountReferences_Visitor import CountReferences_Visitor
from Enum_Visitor import Enum_Visitor
from MultipleOf_Visitor import MultipleOf_Visitor
from Not_Visitor import Not_Visitor
from Number_Visitor import Number_Visitor
from Pattern_Visitor import Pattern_Visitor
from Required_Visitor import Required_Visitor
from UniqueItems_Visitor import UniqueItems_Visitor
from ValueRestriction_Visitor import ValueRestriction_Visitor
from Boolean_Visitor import Boolean_Visitor
from NullType_Visitor import NullType_Visitor
from Object_Visitor import Object_Visitor


class Analytic_Process(mp.Process):
    """! @brief A definition of a process to analyze a JSON Schema files

        An Analytic_Process gets a list of files to analyze, a dictionary for the 
        outputs, a list for all processed filenames and three locks for all shared
        data. In this way the analysis is parallelized over files.
        Additionally, with this approach, a blocking (e.g. a big) file does only 
        block one thread while the other threads can execute and analyse other 
        files in parallel.
    """
    _ids = count()
    def __init__(self, verbose_flag = True, filelist = [], cat_list_dict = dict(), namedict = dict(), \
                filename_cat_dict = dict(), print_lock = th.Lock(), file_lock = th.Lock(), res_lock = th.Lock()):
        """! @brief   The constructor of of an Analytic_Process

            To create an Analytic_Process, the main process has to set up a list of all files to be analyzed,
            a dictionary with categories as keys and lists of attribute dictionaries as values for the results,
            a list to store all valid and processed filenames, and a dicitionary to match filenames with categories.
            Additiononally the main process has to prepare thread locks for printing to console, for fetching
            new files from the list of files to analyse and one to store the results. All lists and dictionaries
            are shared resources and therefor protected with locks.

            @param  verbose_flag:        specifies whether the output shall be shwon on the console
            @param  filelist            a list of all files (i.e. their pathes) that shall be analysed
            @param  cat_list_dict       a dictionary with categories as keys and lists of result attribute_dicts as values 
            @param  namedict            a dictionary of all valid and processed filenames sorted by category
                                        as keys and lists of filenames as values
            @param  filename_cat_dict   a dictionary to match files against their category 
            @param  print_lock          lock for console outputs
            @param  file_lock           lock for files to analyse list
            @param  res_lock            lock for result dictionary cat_list_dict

            @return void
        """
        super().__init__()
        ## Process ID 
        self.id = next(self._ids)
        ## Path to logfile
        self.schema_graph_log_path = "../../schema_graph.log"
        ## Path to currently processed file
        self.filepath = ""
        ## List with filenames to process
        self.filelist = filelist
        ## Flag to indicate whether resulsts shall be printed on console
        self.verbose = verbose_flag
        ## threding.lock to print results in verbose mode safely
        self.print_lock = print_lock
        ## threading.lock() to fetch files to process safely
        self.file_lock = file_lock
        ## threading.lock() to store resulsts safely
        self.res_lock = res_lock
        ## Dictionary to store resulst attribute dictionaries in lists sorted by category
        self.cat_list_dict = cat_list_dict
        ## Dictionary to store names of valid and processed files
        self.name_dict = namedict
        ## Dicitonary to macht filenames against categories
        self.filename_cat_dict = filename_cat_dict
        ## Flag indicating if processed schema was valid
        self.validity_flag = validity.SCHEMA_VALID
        ## Result values stored in dictionary
        self.attribute_dict = dict()
        ## Dictionary of all used visitors on the resolved graph
        self.visitor_dict = dict()
        self.visitor_dict["add_prop_visitor"] = AdditionalProperties_Visitor()
        self.visitor_dict["all_of_visitor"] = AllOf_Visitor()
        self.visitor_dict["any_of_visitor"] = AnyOf_Visitor()
        self.visitor_dict["array_visitor"] = Arrays_Visitor()
        # self.visitor_dict["ref_visitor"] = CountReferences_Visitor() # not applicable on resolved graph --> visit original document graph
        self.visitor_dict["str_visitor"] = Count_String_Visitor()
        self.visitor_dict["enum_visitor"] = Enum_Visitor()
        self.visitor_dict["mult_of_visitor"] = MultipleOf_Visitor()
        self.visitor_dict["not_visitor"] = Not_Visitor()
        self.visitor_dict["number_visitor"] = Number_Visitor()
        self.visitor_dict["pattern_visitor"] = Pattern_Visitor()
        self.visitor_dict["required_visitor"] = Required_Visitor()
        self.visitor_dict["unique_items_visitor"] = UniqueItems_Visitor()
        self.visitor_dict["value_restriction_visitor"] = ValueRestriction_Visitor()
        self.visitor_dict["boolean_visitor"] = Boolean_Visitor()
        self.visitor_dict["nulltype_visitor"] = NullType_Visitor()
        self.visitor_dict["object_visitor"] = Object_Visitor()


    def setFilepath(self, filepath):
        """! @brief Setter for self.filepath 
             @param filepath    Path to the file that shall later be analysed
             @return void
        """
        self.filepath = filepath

    def resetVisitors(self):
        """! @brief Reset all used visitors
            This is necessary because otherwise counts are counted up over files.
        """
        self.visitor_dict["add_prop_visitor"] = AdditionalProperties_Visitor()
        self.visitor_dict["all_of_visitor"] = AllOf_Visitor()
        self.visitor_dict["any_of_visitor"] = AnyOf_Visitor()
        self.visitor_dict["array_visitor"] = Arrays_Visitor()
        self.visitor_dict["str_visitor"] = Count_String_Visitor()
        self.visitor_dict["enum_visitor"] = Enum_Visitor()
        self.visitor_dict["mult_of_visitor"] = MultipleOf_Visitor()
        self.visitor_dict["not_visitor"] = Not_Visitor()
        self.visitor_dict["number_visitor"] = Number_Visitor()
        self.visitor_dict["pattern_visitor"] = Pattern_Visitor()
        self.visitor_dict["required_visitor"] = Required_Visitor()
        self.visitor_dict["unique_items_visitor"] = UniqueItems_Visitor()
        self.visitor_dict["value_restriction_visitor"] = ValueRestriction_Visitor()
        self.visitor_dict["boolean_visitor"] = Boolean_Visitor()
        self.visitor_dict["nulltype_visitor"] = NullType_Visitor()
        self.visitor_dict["object_visitor"] = Object_Visitor()

    def getFilepath(self):
        """! @brief Getter for self.filepath
            @return self.filepath   Path to currently analysed file
        """

        return self.filepath

    def getAttributeDict(self):
        """! @brief Getter for the dictionary that stores analysis results.
            @return self.attribute_dict     Analysis results as dictionary
        """

        return self.attribute_dict

    def getID(self):
        """!@brief Getter for Process' ID
            @return self.id     Process' instance ID
        """

        return self.id

    def run(self):
        """! @brief Process' main function to analyse one file after another as long as files are available.
            
            The thread's core functionality is to analyse multiple files, one after another. Therefor
            a thread gets the next file to process from the list given in constructor. A thread deletes the
            file it is going to process from the list. Race conditions arepossible here. Thats 
            why the block is secured with a lock.

            As long as there are files available to process, threads continue to take files from the list and
            analyse them. The result is stored in the result dictionary in a protected manner.

            @return void

        """

        # Fetching files as long as there are unprocessed files available
        files_available = True

        while files_available:
            self.file_lock.acquire(True)
            if len(self.filelist) == 0:
                files_available = False
                self.file_lock.release()
                break;
            else:
                self.filepath = self.filelist[0]
                self.filelist.pop(0)

            self.file_lock.release()

            # open file and parse content as JSON
            try:
                with open(self.filepath) as fp:
                    schema_dict = json.loads(fp.read())
            except:
                print("incorrect file")
                return

            # analyse the schema....
            if(self.verbose):
                # ... verbose
                self.validity_flag = self.analyse_schema_verbose(schema_dict)
            else:
                # ... silent
                self.validity_flag = self.analyse_schema(schema_dict)

            # store the result in global result dictionary if the schema is valid
            # otherwise produce an entry in the log file
            f_name = os.path.basename(self.filepath)
            cat = self.filename_cat_dict[f_name]
            if self.validity_flag == validity.SCHEMA_REFERENCE_EXCEPTION:
                self.print_lock.acquire(True)
                with open(self.schema_graph_log_path, 'a+') as fp:
                        fp.write(f_name + " contains invalid references!\n")
                self.print_lock.release()
            elif self.validity_flag == validity.SCHEMA_VALIDATOR_EXCEPTION:
                self.print_lock.acquire(True)
                with open(self.schema_graph_log_path, 'a+') as fp:
                        fp.write(f_name + " is invalid according to validator!\n")
                self.print_lock.release()
            elif self.attribute_dict is None:
                self.print_lock.acquire(True)
                with open(self.schema_graph_log_path, 'a+') as fp:
                    fp.write(f_name + "'s validity check went terribly wrong!\n")
                self.print_lock.release()
            else:
                # protected write to result dictionary
                self.res_lock.acquire(True)
                self.name_dict[cat].append(f_name)
                self.cat_list_dict[cat].append(self.attribute_dict)
                self.res_lock.release()


    def analyse_schema(self, schema):
        """! @brief Analyze all features of the given schema.
            
            This function performs all analysis steps and stores the results of every step in
            the internal result dictionary self.attribute_dictionary.

            @param  schema      dictionary representation of the schema produced by json parser module

            @return Indicator "enum" for valid schemas
        """
        # reset attribute dict in case of failure in previous file
        self.attribute_dict = dict() 
        self.resetVisitors()
        ret_val = validity.SCHEMA_VALID
        validator   = schema_checker()

        # check whether schema is valid according to validator module jsonschema
        self.is_valid = validator.check_schema(schema)

        # start analysis only if schema is valid
        if self.is_valid:
            # create schema_graph and load schema
            sg = schema_graph.schema_graph(os.path.basename(self.filepath))

            sg.load_schema(schema)

            # all counts are implemented using the visitor pattern
            # make all visitors visit the resolved reference graph and store the results
            for (name,visitor) in self.visitor_dict.items():
                sg.visit_res_graph(visitor)
                key = name[:-7] + "count" #replace _visitor with _count
                self.attribute_dict[key] = visitor.getCount()

            # perform all other analysis steps and store results
            self.attribute_dict["filename"] = os.path.basename(self.filepath)
            self.attribute_dict["ref_count"] = sg.getNoReferences()
            self.attribute_dict["depth_schema"] = sg.depth_schema()
            self.attribute_dict["depth_resolvedTree"] = sg.depth_resolvedReferenceGraph()
            self.attribute_dict["fan_in"] = sg.getMaxFanIn()
            self.attribute_dict["fan_out"] = sg.getMaxFanOut()
            self.attribute_dict["has_recursion"] = sg.check_recursion()
            self.attribute_dict["min_cycle_len"] = sg.shortest_cycle()
            self.attribute_dict["width"] = sg.getWidth()
            self.attribute_dict["reachability"] = sg.check_reachability()
            self.attribute_dict["fan_in_list"] = sg.getFanInList()
            self.attribute_dict["fan_out_list"] = sg.getFanOutList()
            self.attribute_dict["blow_up"] = sg.getBlowUpFactor()


            if sg.getInvalidReferenceFlag() == True:
                #Schema contains invalid references, what means that it is not valid
                #in terms of semantics --> not taken into account
                ret_val = validity.SCHEMA_REFERENCE_EXCEPTION
                self.attribute_dict = None
        else:
            ret_val = validity.SCHEMA_VALIDATOR_EXCEPTION

        return ret_val

    def analyse_schema_verbose(self, schema):
        """! @brief Analyse the given schema and print all results to the console.

            This function uses analyse_schema() to analyse the given schema.
            
            @param  schema      dictionary representation of schema produced by json module parser
            
            @return Indicator "enum" if schema is valid
            
        """
        
        ret_val = self.analyse_schema(schema)        

        #synchronized console output of the analysis results
        if sg is not None:
            self.print_lock.acquire(True)
            self.print_results()
            self.print_lock.release()

        return ret_val
        
    def print_results(self):
        """! @brief This function creates a console output of the analysis results.
       
        """

        print("File at " + self.filepath + ":")
        print("Is Schema valid:", end=" ")
        print(str(self.is_valid))        

        print("Depth of Schema:", end=" ")
        print(str(self.attribute_dict["depth_schema"]))

        print("Depth of resulting JSON:", end=" ")
        print(str(self.attribute_dict["depth_resolvedTree"]))

        print("Maximum Fan-in:", end=" ")
        print(str(self.attribute_dict["fan_in"]))

        print("Maximum Fan-out:", end=" ")
        print(str(self.attribute_dict["fan_out"]))

        print("Schema has recursions:", end=" ")
        print(str(self.attribute_dict["has_recursion"]))

        print("Reachability given:", end=" ")
        print(str(self.attribute_dict["reachability"]))

        print("Number of simple Pathes or simple cycles respectively:", end=" ")
        print(str(self.attribute_dict["no_path_or_cycle"]))

        print("Width of JSON Schema:", end=" ")
        print(str(self.attribute_dict["width"]))

        # output all counts created by visitors
        for (name, visitor) in self.visitor_dict.items():
            value_name = name[:-7] + "count"
            print(value_name, end=": ")
            print(str(self.attribute_dict[value_name]))

    def getValidityFlag(self):
        """! @brief Return the validity flag of the current processed schema.

            @return Indictator "enum" if schema is valid
        """
        return self.validity_flag
