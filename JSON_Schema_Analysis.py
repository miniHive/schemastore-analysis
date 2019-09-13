#! /usr/bin/python

"""! @package JSON_Schema_Analysis
    @brief This is the main file of the JSON Schema Analysis Project.
 By calling this file and specifying its command line arguments the analysis process is started
 Usage:
   JSON_Schema_Analysis.py [-v | --verbose] [(-a | --all) | ((-c | --count) <val>)
 
 Args:
   - -v | --verbose        output of analysis results to console
   - -a | --all            analyse all schemas located in directory ./JSON
   - -c | --count <val>    analyse only first <val> files in directory ./JSON
"""

import sys, getopt
sys.path.append("./Visitors")
sys.path.append("./NodeTypes")
import os
absFilePath = os.path.abspath(__file__)
os.chdir(os.path.dirname(absFilePath))
from Analytic_Process import Analytic_Process
import threading as th
import multiprocessing as mp
import csv, json
import pandas as pd
import validity_constants as validity
from array import *
from schema_graph import schema_graph


def main(argv):
    """! @brief This is the main entry function of JSON_Schema_Analysis.

        The main function parses the command line arguments and starts the analyses as specified by them.
        The JSON Schema documents are analysed in parallel with n threads, where n represents the number
        of virtual CPU cores found by os.cpu_count().
        This method sets up all lists and dictionaries needed by an Analytic_Thread to perform the analysis
        of the JSON Schema documents and to store the results.
        After all files were analysed completely, the results are output as different csv files and as a 
        Excel sheet.
        The resulting Excel sheet will look as follows:

        Filename | Category | add_prop_count | all_of_count | any_of_count | array_count | ref_count | str_count | enum_count | mult_of_count | not_count | number_count | pattern_count | required_count | unique_items_count | value_restriction_count | boolean_count | nulltype_count | object_count | depth_schema | depth_resolvedTree | fan_in | fan_out | has_recursion | no_path_or_cycle | width | reachability
        --- | --- |         --- |           --- |           --- |       --- |           --- |   --- |       --- |           --- |       --- |           --- |           --- |       --- |               --- |                   --- |               --- |       --- |                   --- |               --- |       --- |           --- |   --- |       --- |       --- |               --- |       ---    
        File1 |  example category | val | val |          val |          val |           val |       val |   val |           val |           val |       val |           val |       val |               val |                   val |               val |           val |               val |           val |           val |           val |       val |   val |           val |           val |       val 
    """
    verbose_output = False
    file_count = 0
    thread_timeout_secs = 720.0

    # parse command line arguments
    try:
        opts, args = getopt.getopt(argv, "hvac:",["verbose","all","count="])
    except getopt.GetoptError:
        print('JSON_Schema_Analysis.py [-v | --verbose] [(-a | --all) | ((-c | --count) <val>)')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('JSON_Schema_Analysis.py [-v | --verbose] [(-a | --all) | ((-c | --count) <val>)')
            sys.exit()
        elif opt in ('-v', '--verbose'):
            verbose_output = True
        elif opt in ('-a', '--all'):
            file_count = 0
        elif opt in ('-c', '--count'):
            file_count = int(arg)

    # set up the environment as specified in the loaded files
    ## directory with JSON Schema documents
    json_dir_path = "./JSON"   
    ## csv that stores nicknames of files and there actual filename
    file_spec_path = "./filename_spec.csv" 
    ## csv that stores nicknames of files and there category
    cat_spec_path = "./categorisation.csv" 
    ## path to logfile
    schema_graph_log_path = "./schema_graph.log" 
    ## multiprocessing manager
    manager = mp.Manager()
    ## matching nicknames to filenames
    filename_dict = manager.dict()
    ## matching nicknames to categories
    cat_dict = manager.dict()   
    ## matching filenames to categories
    filename_cat_dict = manager.dict() 
    ## result dictionary
    cat_list_dict = manager.dict() 
    ## dict of all valid and processed files
    filename_res_dict = manager.dict() 

    open(schema_graph_log_path, 'w+').close() #clean logfile

    with open(file_spec_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            filename_dict[row["name"]] = row["filename"]

    with open(cat_spec_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader: 
            cat_dict[row["name"]] = row["category"]

    for name, filename in filename_dict.items():
        filename_cat_dict[filename] = cat_dict[name]

    help_cat_set = set(cat for cat in cat_dict.values()) #unique categories

    for cat in help_cat_set:
        cat_list_dict[cat] = manager.list()
        filename_res_dict[cat] = manager.list()

    # create list of JSON Schema documents to be analysed
    unmanaged_pathes = list()
    pathes = manager.list()
    
    for file in os.listdir(json_dir_path):
        unmanaged_pathes.append(json_dir_path + "/" + file)

    if not file_count is 0:
        if len(unmanaged_pathes) > file_count:
            unmanaged_pathes = unmanaged_pathes[:file_count]

    for path in unmanaged_pathes:
        pathes.append(path)

    # determine how many threads to use
    thread_count = os.cpu_count()
    # create list to store threads
    thread_list = []
    # create all semaphores for different operations of Analytic_Threads
    print_lock = mp.Lock()
    list_lock = mp.Lock()
    res_lock = mp.Lock()
  
    print("Analysis of files started!")
    pathes_available = True

    #creating and starting of threads
    #threads now handle multiple files by them self
    if verbose_output:
        for i in range(0, thread_count):
            thread_list.append(Analytic_Process(True, pathes, cat_list_dict, filename_res_dict, filename_cat_dict,\
                                print_lock, list_lock, res_lock))
    else:
        for i in range(0, thread_count):
            thread_list.append(Analytic_Process(False, pathes, cat_list_dict, filename_res_dict, filename_cat_dict,\
                                print_lock, list_lock, res_lock))

    for i in range(0, thread_count):
        thread_list[i].start()

    #wait for thread without timeout
    for i in range(0, thread_count):
        thread_list[i].join() 

    unmanaged_cat_list_dict = dict()
    for key in cat_list_dict:
        unmanaged_cat_list_dict[key] = list()


    #create output by storing analysis results to csv and xlsx
    createKeywordCountTable(cat_list_dict)
    saveAllInformation(cat_list_dict, filename_res_dict)
    createFanInCSV(cat_list_dict)
    createFanOutCSV(cat_list_dict)

    print("Finished analysis!")
 

def createKeywordCountTable(cat_list_dict):
    """! @brief Output a CSV file with categories and each counted value.
    
        The ouput csv file specifies summed keyword count per category

        @param  cat_list_dict   dictionary with all analysis results
    """

    # this list specifies all relevant attributes for this csv file
    attribute_name_list = ["add_prop_count", "all_of_count", "any_of_count", \
        "array_count", "ref_count", "str_count", "enum_count", "mult_of_count", \
        "not_count", "number_count", "pattern_count", "required_count", "unique_items_count", \
        "value_restriction_count", "boolean_count", "nulltype_count", "object_count"]

    # sum up the keyword counts for all relevant attributes per category
    attr_count = 0
    cat_count = 0
    table = [[0 for x in range(len(cat_list_dict.keys()))] for y in range(len(attribute_name_list))]
    for attr in attribute_name_list:
        cat_count = 0
        for cat in cat_list_dict:
            cat_att_sum = 0
            for att_dict in cat_list_dict[cat]:
                cat_att_sum += att_dict[attr]
            table[attr_count][cat_count] = cat_att_sum
            cat_count += 1
        attr_count += 1
    
    # write the csv file to ../../KeywordCount.csv
    with open("./KeywordCount.csv", 'w+') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",")
        csvwriter.writerow(["Attribute"] + list(cat_list_dict.keys()))
        attr_count = 0
        for row in table:
            csvwriter.writerow([attribute_name_list[attr_count]] + row)
            attr_count += 1

def saveAllInformation(cat_list_dict, filenamedict):
    """! @brief This function saves all analysed information in a csv-File and a Excel sheet.
        This function creates a csv file where all analysis results of all Schema documents are stored.
        It also creates an equivalent Excel sheet with the same information

        @param  cat_list_dict       a dictionary with all analysis results
        @param  filenemlist         a list with the names of all valid and analysed JSON Schema documents
    """  
    
    keyword_list = list()
    #exclude fan_in and fan_out lists from this csv
    for key in cat_list_dict["data"][0].keys():
        if (key == "fan_in_list") or (key == "fan_out_list") or (key == "filename"):
            continue
        else:
            keyword_list.append(key)
    # create csv-file at ../../AnalysisResults.csv
    data = []
    filenames = []
    with open("./AnalysisResults.csv", 'w+') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        # Header with all attribute names. These are extracted from example category conf and the 
        # first element in the category's dictionary list
        
        csvwriter.writerow(["Category"] + keyword_list)
        for cat in cat_list_dict:
            #filenames.extend(filenamedict[cat])
            for attr_dict in cat_list_dict[cat]:
                csv_row = [cat]
                filenames.append(attr_dict["filename"])
                for attr in keyword_list:
                    csv_row.append(attr_dict[attr])
                data.append(csv_row)
                csvwriter.writerow(csv_row)

    # create equivalent Excel Sheet at ../../AnalysisResults.xlsx
    col_list =  keyword_list;
    col_list.insert(0, "Category")
    df = pd.DataFrame(data, filenames, col_list)
    df.to_excel("./AnalysisResults.xlsx")

    
def createFanInCSV(cat_list_dict):
    """! @brief This function creates a csv file with all fan-ins of all elements in all files.
        The output csv file is used to generate plots of all fan-ins contained in a file.

        @param cat_list_dict        a dictionary containing all analysis results
    """
    with open("./FanInList.csv", 'w+') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for cat in cat_list_dict:
            for attr_dict in cat_list_dict[cat]:
                csvwriter.writerow([cat] + attr_dict["fan_in_list"])

def createFanOutCSV(cat_list_dict):
    """! @brief This function creates a csv file with all fan-outs of all elements in all files.
        The output csv file is used to generate plots of all fan-outs contained in a file.

        @param cat_list_dict        a dictionary containing all analysis results
    """
    with open("./FanOutList.csv", 'w+') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for cat in cat_list_dict:
            for attr_dict in cat_list_dict[cat]:
                csvwriter.writerow([cat] + attr_dict["fan_out_list"])

# entry point
if __name__ == "__main__":
    main(sys.argv[1:])
