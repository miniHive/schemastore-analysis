import urllib3 as url
import json
import io, os

def load_schema(url_str, logfile):
    """! @brief This function loads a schema from given web address and returns a JSON schema dictionary representation 
        
        The function is capable of returning sub-object of the schema by requesting e.g. http://example.com/#def1
        
        @note   For the UnitTest of schema_graph.py, this function can additionaly load two files from local storage
                when one of the following urls is requested: http://loopback/address or http://loopback/ext

        @param  url_str  url to download file from
        @param  logfile file pointer to logfile

        @return Dictionary representation of requested Schema, part of Schema or None if failed
    """
    partly_referenced = False
    valid_json = True 
    schema_url = url_str
    # change working directory to satisfy relative pathes
    old_path = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    # if special urls for unit tests are requested, load files from local storage
    if schema_url == "http://loopback/address":
        fp = open("./PyTest/TestSchemas/addr_rec.json")
        schema_raw = fp.read()
        fp.close()
    elif schema_url == "http://loopback/ext":
        fp = open("./PyTest/TestSchemas/ext_ref.json")
        schema_raw = fp.read()
        fp.close()
    else:
        if "#" in schema_url:
            #A definition or part of the whole file is referenced
            partly_referenced = True
            # extract url part
            definition_part = schema_url[(schema_url.find("#")+1):]
            schema_url = schema_url[:(schema_url.find("#"))]
        # download whole file
        url.disable_warnings(url.exceptions.InsecureRequestWarning)    
        http = url.PoolManager()
        schema_raw = http.request('GET', schema_url).data
    if schema_raw is None:
        logfile.write("Could not load from " + schema_url + "\n")
    else:
        try:
            schema_json = json.loads(schema_raw)
            if partly_referenced:
                # part of file referenced, set return value to sub-dictionary
                # get name of sub-dictionaries
                definition_list = definition_part.split(sep="/")

                # step-by-step deeper into dictionaries until right and last one in definition parts is reached
                for part in definition_list:
                    if part == '':
                        continue
                    else:
                        schema_json = schema_json[part]

        except:
            logfile.write("Fucked up JSON at " + schema_url + "\n")
            valid_json = False

    # restore working directory
    os.chdir(old_path)
        
    if valid_json:            
        return schema_json
    else:
        return None
