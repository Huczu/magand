
# Magand

Magand simple Molpro output parser to csv files

### Requirements:

Python 3.0+

### Usage:

Configure your options in config.json file and/or use optional parameters in run arguments
Run: **python magand.py <optionalParams>**
*Optional parameters:*
-i [--ifile=] input file from Molpro. **Default value:** read from config.json
-o [--ofolder=] output folder with parsed results. **Default value:** read from config.json
-c [--configtype=] config type used from config.json. **Default value:** default

### Features:

Magand parser can extract results to csv file of:
* Spin-Orbit Matrix
* Spin-Orbit Matrixblock
* Composition of spin-orbit eigenvectors
* Expectation values DMX
* Expectation values DMY
* Expectation values DMZ

Can group results to one file of matrix results or to separate rvec files
Can use multiple configurations in one file

### TODO:

* Results of Eigenvectors
* Extract result of one element

### License:

GNU GENERAL PUBLIC LICENSE
Feel free to use and modify
