'''Pipeline to:

1. Clean up the cdr data by removing redundant fields

2. Get basic correlation, call failure visualization etc

3. Get basic call details summary for the entire dataset
'''


#This task simply cleans up the dataset, removing
#redundant fields etc before the SummarizeTask
#generates summaries and visualzations

import luigi
import os,csv
import pandas as pd 
import numpy as np 

from constants import *

class CleanUpDatasetTask(luigi.Task):

	def requires(self):
		return None

	def output(self):
		return [
		luigi.LocalTarget('processed_data/processed_cdr.csv'),
		luigi.LocalTarget('processed_data/summary')
		]

	def run(self):
		print('Hello')
		df = pd.read_csv(CDR_PATH, low_memory = False)
		single_val_columns = [col for col in df.columns if df[col].nunique() == 1]
		identifier_columns = [col for col in df.columns if df[col].nunique() == len(df)]
		
		#Drop all columns which only have a single value:
		df.drop(columns = single_val_columns, inplace = True)
		#Also drop identifier columns:
		df.drop(columns = identifier_columns, inplace = True)
		
		os.makedirs(self.output()[1].path)
		
		#Write to csv
		df.to_csv('processed_data/processed_cdr.csv',index = False)


class GetVisualisationsTask(luigi.Task):

	def requires(self):
		return CleanUpDatasetTask

	def output(self):
		pass

	def run(self):
		pass



if __name__ == "__main__":
	luigi.run()