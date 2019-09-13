import sys, pytest
sys.path.append("../")
sys.path.append("../NodeTypes")
sys.path.append("../Visitors/")
from schema_graph import schema_graph
import json
import pandas as pd
import networkx as nx
from Count_String_Visitor import Count_String_Visitor
from CountReferences_Visitor import CountReferences_Visitor

"""! @package This file runs the unit test for JSON_Schema_Analysis project
    It loads all test cases with files as input and the expected values per category
    from the Excel Sheet TestDefintions.xlsx
"""

#getting test data from ExcelSheet
xl = pd.ExcelFile("TestDefinitions.xlsx")
df = xl.parse('Tests')
xl.close()

ex_depth_list = list()
ex_resdepth_list = list()
ex_has_recursion_list = list()
ex_string_count_list = list()
ex_fan_in_list = list()
ex_reachability_list = list()
ex_ref_count_list = list()
ex_no_nodes_list = list()
ex_no_exp_nodes_list = list()
filename_list = list()
i = 0
for file in df["Filename"]:
    ex_depth_list.append((file, df["schema_depth"][i]))
    ex_resdepth_list.append((file, df["resolved_depth"][i]))
    ex_has_recursion_list.append((file, df["has_recursions"][i]))
    ex_string_count_list.append((file, df["string_count"][i]))
    ex_fan_in_list.append((file, df["fan_in"][i]))
    ex_reachability_list.append((file, df["reachability"][i]))
    ex_ref_count_list.append((file, df["ref_count"][i]))
    ex_no_nodes_list.append((file, df["no_nodes"][i]))
    ex_no_exp_nodes_list.append((file, df["no_exp_nodes"][i]))
    filename_list.append(file)
    i += 1

@pytest.mark.parametrize("test_input, expected", ex_depth_list)
    
def test_depth(test_input, expected):
    assert depth(test_input) == expected

@pytest.mark.parametrize("test_input, expected", ex_resdepth_list)

def test_resolvedDepth(test_input, expected):
    assert resDepth(test_input) == expected

@pytest.mark.parametrize("test_input, expected", ex_has_recursion_list)

def test_recursion(test_input, expected):
    assert recursion(test_input) == expected

@pytest.mark.parametrize("test_input, expected", ex_string_count_list)

def test_string_count(test_input, expected):
    assert string_count(test_input) == expected

@pytest.mark.parametrize("test_input, expected", ex_fan_in_list)

def test_fan_in(test_input, expected):
    assert fan_in(test_input) == expected

@pytest.mark.parametrize("test_input, expected", ex_reachability_list)

def test_reachability(test_input, expected):
    assert reachability(test_input) == expected

@pytest.mark.parametrize("test_input, expected", ex_ref_count_list)

def test_refCount(test_input, expected):
    assert refCount(test_input) == expected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           

def depth(filename):
    sg = getSg(filename)
        
    return sg.depth_schema()

def resDepth(filename):
    sg = getSg(filename)
    ret_val = sg.depth_resolvedReferenceGraph()
    return ret_val

def recursion(filename):
    sg = getSg(filename)

    return sg.check_recursion()

def string_count(filename):
    sg = getSg(filename)
    visitor = Count_String_Visitor()
    sg.visit_res_graph(visitor)

    return visitor.getCount()

def fan_in(filename):
    sg = getSg(filename)

    return sg.getMaxFanIn()

def reachability(filename):
    sg = getSg(filename)

    return sg.check_reachability()

def refCount(filename):
    sg = getSg(filename)

    return sg.getNoReferences()

def origNodes(filename):
    sg = getSg(filename)

    return len(list(sg.nodes))

def expNodes(filename):
    sg = getSg(filename)

    if sg.check_recursion():
        ret_val = 1
    else:
        expGraph = sg.getExtendedRefGraph()
        ret_val = len(list(expGraph.nodes))

    return ret_val

def getSg(filename):
    """! @brief Load Schema Graph from file 
        @param  filename    Name of the file located in ./TestSchemas directory

        @return schema_graph of the given file
    """
    with open("./TestSchemas/"+filename, 'r') as fp:
        sg = schema_graph(filename)
        sg.load_schema(json.loads(fp.read()))

    return sg
