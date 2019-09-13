import json
import jsonschema


class schema_checker(object):
    """! @brief This class implements a validity check for JSON Schema documents
        
        This class gets a schema as dictionary parsed by json module and checks whether it is
        a valid JSON Schema document by using the jsonschema validator module.
    """

    def __init__(self):
        """! @brief Constructor for schema_checker

            Initialize the internal variables self.schema, self.draft and self.validator
        """
        self.schema = None
        self.draft = ""
        self.meta = None
        self.validator = None

    def set_new_schema(self, schema):
        """! @brief This function introduces a new schema to check its validity.
            This function takes a schema dictionary and determines the draft version by checking
            the Schemas $schema property

            @param schema       a dictionary representation of the JSON Schema document parsed by json module
        """
        self.schema = schema
        try:
            schema_string = schema["$schema"]
            idx = schema_string.find("draft-0")
            if(idx == -1):
                if(schema_string == "http://json-schema.org/schema"):
                    self.draft = "draft-07" #latest draft
            else:                    
                self.draft = schema_string[idx:(idx+8)]
        except:
            # if $schema tag is missing, the draft verstion can't be determined and the schema is 
            # treaten as invalid
            print("$schema-Tag missing!")
            self.draft = None

    def check_schema(self, schema=None):
        """! @brief This function determines the validity of the given JSON Schema document.
            The jsonschema module is a validator that can check the given schema against the draft specification
            which is also a JSON Schema document.

            @param  schema  a dictionary representation of a Schema produced by json module
                            If not given or set to None, the method returns False i.e. invalid
            @return         Validity of schemas as boolean value. True => Valid; False => Invalid
        """
        ret_val = True

        if not schema is None:
            self.set_new_schema(schema)
            # switch validator according to draft version
            if ('draft-07' == self.draft):
                self.validator = jsonschema.Draft7Validator
            elif ('draft-06' == self.draft):
                self.validator = jsonschema.Draft6Validator
            elif ('draft-05' == self.draft):
                #draft-05 uses old metas form draft-04
                self.validator = jsonschema.Draft4Validator
            elif ('draft-04' == self.draft):
                self.validator = jsonschema.Draft4Validator
            elif ('draft-03' == self.draft):
                self.validator = jsonschema.Draft3Validator
            elif self.draft is None:
                print("Non-valid JSON Schema document!")
                return False
        
            # check validity. if invalid an exception is raised by jsonschema validators
            try:
                self.validator.check_schema(self.schema)
            except:
                print("Non-valid JSON Schema document!")
                ret_val = False
        else:
            ret_val = False

        return ret_val

   