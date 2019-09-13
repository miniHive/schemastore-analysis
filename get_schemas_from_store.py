#!/usr/bin/python3

## This file downloads and renames and stores the available JSON Schemas from schemastore.org

import urllib3 as url
import json
import os
import shutil
import csv

# specifiy path where a folder with all JSONs will be created
path_schema = "./"

path = path_schema + "JSON"

if not os.path.exists(path):
    os.makedirs(path)
    print("Created Directory JSON!")
else:
    shutil.rmtree(path)
    os.makedirs(path)
    
path = path + "/"

url.disable_warnings(url.exceptions.InsecureRequestWarning)    
http = url.PoolManager()

schema_catalog_req = http.request('GET', 'http://schemastore.org/api/json/catalog.json')
schema_catalog_raw = schema_catalog_req.data

# converts a json file into python data structures, e.g. Object --> dict
schema_catalog_json = json.loads(schema_catalog_raw)

itrtr = 0
print("Fetching Schemas...", end="")
log = open(path_schema + "logfile.log", 'w+')
url_file = open(path_schema + "non_descripted_urls.log", 'w+')
bad_names_file = open(path_schema + "bad_names.log", 'w+')
csv_file = open(path_schema + "filename_spec.csv",'w+', newline='')
csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=["name", "filename"])
csv_writer.writeheader()

no_schemas_available = len(schema_catalog_json["schemas"])

duplicate_list = []
duplicate_iterators = []

for schema in schema_catalog_json["schemas"]:
    valid_json = True 
    schema_url = schema["url"]
    schema_raw = http.request('GET', schema_url).data
    if schema_raw is None:
        log.write("Could not load from " + schema_url + "\n")
        print("NONE")
    else:
        try:
            schema_json = json.loads(schema_raw)
        except:
            log.write("Fucked up JSON at " + schema_url + "\n")
            valid_json = False
     
    try:
        filename = schema_json["title"].replace(" ", "_") + ".json"
    except KeyError:
        try:
            filename = schema_json["description"].replace(" ", "_") + ".json"
        except KeyError:
            filename = schema_url[12:23].replace(" ", "_") + ".json"
            url_file.write(schema_url + "\n")

    filename = filename.replace("/", "_")
    filename = filename.replace(",", "_")
    filename = filename.replace(":", "")
        
    if valid_json:            
        if os.path.isfile(path+filename):
            if filename in duplicate_list:
                idx = duplicate_list.index(filename)
                duplicate_iterators[idx] = duplicate_iterators[idx] + 1
            else:
                duplicate_list.append(filename)
                duplicate_iterators.append(1)
                idx = duplicate_list.index(filename)
                
            filename = filename[:-5] + "_" + str(duplicate_iterators[idx]) + ".json"
        try:
            f = open(path + filename, 'w+')
            f.write(json.dumps(schema_json, indent=4))
            f.close()
            itrtr = itrtr + 1
        except OSError:
            old_filename = filename
            filename = "Schema_" + str(itrtr) + ".json"
            try:
                f = open(path + filename, 'w+')
                f.write(json.dumps(schema_json, indent=4))
                f.close()
                bad_names_file.write(old_filename + ": " + schema_url + "\n")
                itrtr = itrtr + 1
            except OSError:
                log.write("File " + old_filename + " could not be created\n")
            log.write("File " + old_filename + " renamed to " + filename + "\n")
        csv_writer.writerow({'name' : schema["name"], 'filename' : filename})
    else:
        csv_writer.writerow({'name' : schema["name"], 'filename' : "None"})
            
    print(".", end="")
    
    #endif valid_json
log.close()
url_file.close()
bad_names_file.close()
csv_file.close()
print("")
print(str(itrtr) + " of " + str(no_schemas_available) + " available schemas fetched!")
