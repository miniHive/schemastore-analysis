# JSON-Schema-Analysis

## Description
__JSON-Schema-Analysis__ is a project to analyse real-world JSON Schema documents towards their usage of components and features allowed by the [JSON Schema standard](https://json-schema.org/latest/json-schema-core.html).  
Therefore the JSON Schema files available at the [JSON Schema Store](schemastore.org) are downloaded and analysed using some Python scripts. 

## Running the Code 
### Preliminaries
To run this code on your device, you have to download or clone this repository. You must have a version of Python 3 installed.
The project is tested with Python version __Python 3.7.2__. You'll also need to install some packages available with __pip__. The used packages are:
* [Networkx](https://networkx.github.io/) - A package for operations on graphs
* [PyDot](https://pypi.org/project/pydot/) - A package to operate with DOT-Format used to visualize graphs
* [Graphviz](https://pypi.org/project/graphviz/) - A package to interact with the Graphviz Framework
* [MatPlotLib](https://matplotlib.org/) - A package to create plots with the results of the analysis 
* [Pandas](https://pandas.pydata.org/) - A package used to import and export MS Excel sheets 
* [Openpyxl](https://openpyxl.readthedocs.io/en/stable/) - A package used by Pandas to export data to MS Excel format
* [jsonschema](https://github.com/Julian/jsonschema.git) - A package which implements a JSON Schema Validator, that is used to validate
* [xlrd](https://pypi.org/project/xlrd/) - A packacke for data extraction from Excel documents
the Schemas themselves

The following table shows the versions of the packages, which were used to run the project.

Package | Version
------- | -------:
NetworkX | 2.2
PyDot | 1.4.1
Graphviz | 0.10.1
Matplotlib | 3.0.2
Pandas | 0.23.4
Openpyxl | 2.6.1
jsonschema |  3.0.0a4.dev74+g5f5b865

### Installing on Windows
To install the named packages run the following code in your Windows PowerShell.
```PowerShell
> pip install networkx
> pip install pydot
> pip install graphviz
> pip install matplotlib
> pip install pandas
> pip install openpyxl
> pip install urllib3
> pip install git+https://github.com/Julian/jsonschema.git
```

It is necessary to install the *jsonschema* package directly from GitHub to get the latest version. The version available at PyPI does **not** include support for Schema draft 6 and 7.

Additionally you will have to install the [GraphViz](http://www.graphviz.org/) software from [here](https://graphviz.gitlab.io/_pages/Download/Download_windows.html).  Select the most recent
stable release (2.38 on 05/21/2019). The easiest way is to downlowad the msi file. Openening that will start an installer.
__NOTE: *Don't forget to include the /bin directory of your GraphViz to your PATH environment variable on windows after installation. Depending on your installation the path to add to your PATH variable could look like this: C:\Program Files (x86)\Graphviz2.38\bin. 
For more information on how to change your PATH environment variable please have a look at [this post](https://java.com/en/download/help/path.xml) .*__. 


### Installing on Unix
To install the named packages run the following code in your Windows PowerShell.
```bash
$ pip install networkx
$ pip install pydot
$ pip install graphviz
$ pip install matplotlib
$ pip install pandas
$ pip install openpyxl
$ pip install urllib3
$ pip install git+https://github.com/Julian/jsonschema.git
```

It is necessary to install the *jsonschema* package directly from GitHub to get the latest version. The version available at PyPI does **not** include support for Schema draft 6 and 7.

Additionally you will have to install the [GraphViz](http://www.graphviz.org/) software from [here](http://www.graphviz.org/download/). 

### Running the code

After you appropriately installed the packages named above, you can rerun the analysis provided by this project.
The main file is JSON_Schema_Analysis.py. It takes some optional command line arguments. Providing `-a` makes the code analyse all files provided in the directory *JSON*. With the argument `-c <arg>` you can specify the amount of files to analyse. It is also possible to print all results on the CLI with the argument `-v`.

To analyse additional schemas, you have to put them in the directory JSON and add them in the two CSV files responsible for category matching. These are filename_spec.csv and categorisation.csv, both located in the main directory of this project. For each file, you have to specify a nickname, the real filename and a category. Insert a line with `nickname,filename` in filename_spec.csv and a line with `nickname,category` in categorisation.csv for every additional JSON Schema you want to analyse. 
Although ___JSON_Schema_Analysis___ specifies the four categories *app*, *data*, *conf* and *meta*, it is capable of handling other categories just by specifing them as `category`in categorisation.csv.

### Results
The results are stored as an Excel sheet named AnalysisResulst.xlsx in the projects main directory and as CSV file AnalysisResulsts.csv in the same directory. Plots have to be generated seperately with the provided scripts explained at the bottom of this document.
AnalysisResulsts.xlsx consists of several columns containing information about a specific JSON Schema document in each row.
The first column is giving the filename of the JSON Schema document located in the JSON directory. The following columns in the same row provide the information about this JSON Schema generated by the analysis.
The following table will give an explanation of the meaning of each column.

Column name | Meaning
:----------- | :--------
add_prop_count | Number of occurences of the *additionalProperties* keyword.
all_of_count | Number of occurences of the *allOf* keyword.
any_of_count | Number of occurences of the *anyOf* keyword.
array_count | Number of occurences of the *array* keyword.
str_count | Number of occurences of the *string* type keyword.
enum_count | Number of occurences of the *enum* keyword.
mult_of_count | Number of occurences of the *multipleOf* keyword.
not_count | Number of occurences of the *not* keyword.
number_count | Number of occurences of the *integer* plus *number* type keywords. 
pattern_count | Number of occurences of the *pattern* plus *patternProperty* keyword.
required_count | Number of occurences of the *required* keyword.
unique_items_count | Number of occurences of the *uniqueItems* keyword.
value_restriction_count | Sum of occurences of the *min*, *max*, *minLength*, *maxLength*, *exlusiveMinimum* and *exlusiveMaximum* keywords.
boolean_count | Number of occurences of the *boolean* type keyword.
nulltype_count | Number of occurences of the *null* type keyword.
object_count | Number of occurences of the *object* type keyword.
ref_count | Number of occurences of the *$ref* keyword.
depth_schema | Depth of the tree that emerges from loading the *raw* JSON Schema into an __schema_graph__ .
depth_resolvedTree | Depth of the tree after resolving the references. If *has_recursion* is true, this is the maximum cycle length in the recursive document.
fan_in | Maximum Fan-In over all nodes included in the schema_graph.
fan_out | Maximum Fan-Out over all nodes included in the schema_graph.
has_recursion | Boolean flag that indicates whether the JSON Schema document (i.e. the resolved graph) is recursive.
min_cycle_len | Minimum cycle length of a recursive document. If *has_recursion* is false, this column will be 0.
width | Number of leaf nodes in the schema_graph of the raw JSON Schema document.
reachability | Boolean flag that indicates whether the schema contains unreachable (unused) definitons.

### Project Structure
The main part of the project is located in *./JSON_Schema_Analysis/JSON_Schema_Analysis*. The Python script *JSON_Schema_Analysis.py* contains the main function.
When started, it creates several processes equal to the number of virtual CPU cores available on the current machine. These processes are described in the file *Analytic_Process.py*. 
The project uses the python multiprocessing library and an Analytic_Process inherits from the process class defined there.
Analytic_Processes fetch a file and perform all necessary analytic steps. The results are stored afterwards and a new file is fetched as long as unprocessed files are available. This is implemented to avoid problems with concurrency.
The Analytic_Processes build schema_graph from the JSON Schema documents. These graphs are represented by the class defined in *schema_graph.py*. Most computational stuff is performed there.
Three types of graph nodes are defined in the project: KeyValuenNodes, ArrayNodes and ObjectNodes that all inherit from SchemaNode defined in the files with the same name.
The file *load_schema_from_web.py* is used to download additional files in the resolving process every time an external reference is required. The schema_checker.py file performs the validity check with one validator.
All type counts and some other counts are performed using the visitor pattern. All used visitors are defined in the subdirectory *Visitors*. The *Meta_Schemas* directory contains the JSON Schema Meta Schemas for each draft.

All unit tests performed can be found in the directory *PyTest*. There is an additional ReadMe.md that describes the structure of the tests.

The top directory of the project contains the results in *AnalysisResulst.xlsx* and *AnalysisResulsts.csv*. The contained information is equal.
The file *categorisation.csv* contains the mapping of JSON Schema document's short names to their category. The file *filename_spec.csv* contains the mapping from document short names (see schemastore.org)
to the actual used filenames of the stored JSON Schema documents. Both files are used by the project to determine the category of each file.
The file filename_spec.csv is generated by *get_schemas_from_store.py*. This script downloads all JSON Schema documents from schemastore.org, generates the filenames and stores the schemas in the directory JSON.
The file *typeCompareBoxplot_CombinedCount.py* generates the plot *typeCompareBoxplot_CombinedCount.png* in the directory *Plots* by reading the required data from AnalysisResulsts.xlsx.
The three barcharts are generated by *hist.py*. The file countsSpecialCategoriesTotal.csv is generated by *table.py*. The file *writer.py* implements helper functions for *table.py*. Before *table.py* can be executed, *writer.py* has to be run at least once.

The directory _JsonSchemaAnalysis_ contains a reference implementation of the python project which was used to validate the calculated results.

