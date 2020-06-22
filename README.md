# GG-project-workflow-automation
Automating the data cleaning and pre-processing tasks using the Luigi module

This module contains multiple Luigi scripts which serve to automate the data processing pipeline of the GoldenGate - Intelligent Insights project which so far has been done through running multiple individual scripts. This would make it simpler to take new instances of the CDR and cluster configuration data, and process and prepare the dataset for further analysis. 


Steps:

Install required dependencies using the requirements.txt from within a Python virtual environment. 

After creating and loading a virtual environment, do:

pip install requirements.txt

Run the luigi daemon:
luigid --background --port=8082 

The individual Luigi scripts to be run are:

cdr-data-pipeline.py \n
extract-config-data-pipeline.py

Update the location of the CDR dataset and the cluster config dataset in the constants.py file

The latter Luigi script can be run as(after running the Luigi daemon):

python extract-config-data-pipeline.py ExtractEndUserDataTask

