# PyTest: Unit Tests for JSON-Schema-Analysis

This directory and its subdirectories contain everything needed for running the defined unit tests for ___JSON_Schema_Analysis___.
It uses *pytest* framework in version 4.3.0.

## Preliminaries

Before running the test you'll have to install *pytest* from PyPI by running the following instruction either in bash on Linux or in PowerShell on Windows.

```PowerShell
> pip install pytest
```

## Running the tests

To run the test, navigate to your local version of the PyTest directory on your prefered CLI. Run the following command.

```PowerShell
> pytest
```

Pytest will automatically detect all files starting with test_ and include them in testing. In this case the only appropriate file is 
test_schemagraph.py. 
This file is implemented to accept test changes dynamically without touching the file itself. It fetches the inputs in terms of *files to test*
and the expected outputs for every test from the Excel sheet TestDefinitions.xlsx located in this directory.
To add a test case, you have to add a file to this sheet by adding a line containing the filename, the schema's expected depth, the schema's expected
resolved depth, the schema's expected has_recursions property, the schema's string count, the schema's maximum fan-in and the schema's reachability property.
Additionaly the test file has to be located in the subdirectory TestSchemas. 

## Test coverage

The defined tests are designed to test most of the analysis results. They check the schemas depth, the resolved depth, the resolved graph (by comparing it to a specified graph in DOT format)
, the detection of recursions, the string count, the maximum fan-in and the reachability detection.
The existing test files are designed to cover most of the possible JSON Schema structures allowed by the standard. Although this surely is impossible,
we hope that we could provide a stable analysis by checking against these test cases.
