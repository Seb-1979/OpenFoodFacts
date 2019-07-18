# OpenFoodFacts
The goal of this program is to use the OpenFoodFacts API to substitute a user-selected food for a healthier one.

## Installation :

To use this application, you will need to install the plug-ins defined in the requirements.txt file with the following command in your virtual environment:
> pip install -r requirements.txt

I also use the normally installed webbrowser module as well as tkinter which is part of the packages installed by default with python 3 but it may not be the case as under Ubuntu where it will install the package `python3-tk` .
__________________________

## Role of each module :

1. **dbmysql :**
Its module allows to widen with the mysql / connector module.

2. **wrap_api_opf :**
Its module allows you to recover products from the OpenFoodFacts database using the API written in Python. The API is defined in the openfoodfacts package.

3. **tables_opf :**
Contains the definition of the Mysql tables that will be used to record data from the Open Food Facts database.

4. **ui :**
This is the user interface of the application.

5. **main :**
This is the module to call to run the application.

6. **Secondary modules**
  - **timer :**
  Contains a `Timer` class that creates an object to measure elapsed time, and a `tms_to_str` function that takes an integer value in milliseconds and converts it to a value in hours, minutes, and seconds. This value is returned as a string.
  - **listselect :**
  Contains a `ListSelect_ class to create a listbox with Tkinter. It manages the scrollbar and adds a text field to select an item via its number.
