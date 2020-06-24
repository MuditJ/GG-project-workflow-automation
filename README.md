# GG-project-workflow-automation

DETAILS:

Automating the data cleaning and pre-processing tasks using the Luigi module

This module contains two Luigi scripts which serve to automate the data processing pipeline of the GoldenGate - Intelligent Insights project which so far has been done through running multiple individual scripts. 

This would make it simpler to take new instances of the CDR and cluster configuration data, and process and prepare the dataset for further analysis.




STEPS TO RUN :

Create a virtual environment:
python3 -m venv env

Activate the virtual environment:
source env/bin/activate

Install required dependencies using the requirements.txt from within the Python virtual environment. 

pip install -r requirements.txt 


IMPORTANT: Update the location of the CDR dataset and the corresponding cluster config dataset in the constants.py file - this is used in the Luigi scripts to be run

After updating the paths for the CDR dataset and the corresponding cluster configuration data, run the shell script :
./startup.sh




Folders created after running the shell script:

Running the Luigi scripts (from the shell script) will process the input data and create a few directories to hold the result. These are:

extracted-config-data/ : This directory holds data extracted from the cluster config data provided. The data for each cluster was present in a single data dump - extracted-config-data/cluster-wise-data/ holds data from each of these clusters, separated by the type of data i.e. there are now separate csvs which hold enduserdata, device data etc which was all previously present in a single data dump

data-visualisation/ : This directory holds images of basic data visualisation performed on the CDR dataset. This represents only small sample of the kinds of visualisations that can be performed on the 100+ fields present

processed-data/ : This directory holds two csvs:

processed_cdr.csv : This is a cleaned up version of the original CDR dataset, with redundant fields(which have the same value for each row or a unique one for each row) are removed, and new derived fields are added

final_joined_data.csv: This CSV combines device data obtained from the cluster configuration data and performs an INNER JOIN with the CDR data on the device name fields, to add new fields such as origDeviceLocation, origDeviceCSS, destDeviceLocation etc. 

THIS PARTICULAR CSV WAS USED TO TRAIN THE CLASSIFIER MODEL(TO PREDICT CALL FAILURES) WHICH GAVE US AN ACCURACY ABOVE 90%
