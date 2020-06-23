'''Pipeline to:

1. Clean up the cdr data by removing redundant fields

2. Get basic correlation, call failure visualization etc

3. Get basic call details summary for the entire dataset
'''


#This task simply cleans up the dataset, removing
#redundant fields etc before the SummarizeTask
#generates summaries and visualzations

import luigi
import os,csv,json
import datetime,calendar
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt


CDR_PATH = os.path.join(os.getcwd(),'P_CDR_REC.csv')

class CleanUpDatasetTask(luigi.Task):

	def requires(self):
		return None

	def output(self):
		return [
		luigi.LocalTarget('processed_data/')
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

		#Create new columns:
		df['PSTNCaller'] = df.apply(lambda x: x['callingPartyNumberPartition'] is np.nan,axis = 1)
		
		df['CallForwarded'] = df.apply(lambda x:x['originalCalledPartyNumber'] != x['finalCalledPartyNumber'],axis = 1)

		df['CallStatus'] = df.apply(lambda x: 'Fail' if (x['duration'] == 0 and x['dateTimeConnect'] == 0) else 'Success', axis = 1)

		os.makedirs(self.output()[0].path)
		
		#Write to csv
		df.to_csv('processed_data/processed_cdr.csv',index = False)


class JoinCdrAndClusterConfigDataTask(luigi.Task):
	'''This task joins the CDR data with the cluster config data - specifically the device data present
		in the cluster config data. This process is done via performing INNER JOIN operation on the 
		device fields present in the CDR data with the device fields present in the cluster config device data '''

	def requires(self):
		#Since ExtractEndUserDataTask generates the json files holdng the device data, we need to run that task
		#before this one
		return CleanUpDatasetTask()

	def output(self):
		return [
		self.input()]


	def run(self):
			config_data_path = os.path.join('extracted-config-data/all-clusters-device-data/','all_devices_data.json')
			with open(config_data_path,'r') as data:
				json_device_data = json.load(data)

			#Loading the JSON data into a dataframe:
			config_data_df = pd.DataFrame(json_device_data, columns = list(json_device_data[0].keys()))

			#From the cluster config data, keep only devices which have one occurence(ie one configuration)

			#Grouping records by Device Name field
			config_device_groups = config_data_df.groupby('Device Name')

			#Filtering and keeping only those groups which have a count of 1 i.e. devices with a single occurence
			single_entry_devices = config_device_groups.filter(lambda x: len(x) == 1)['Device Name']

			#Load CDR data:

			cdr_data = pd.read_csv(os.path.join(self.input()[0].path,'processed_cdr.csv'), low_memory = False)
			#Filter the CDR data by origDeviceName and destDeviceName - such that all records have devices which
			#are present in the config data

			cdr_filtered_df = cdr_data.loc[(cdr_data['origDeviceName'].isin(single_entry_devices)) & (cdr_data['destDeviceName'].isin(single_entry_devices))].copy()

			#Perform join operation on Device Name field - this needs to be performed in two steps.
			#1. Perform inner join between origDeviceName of cdr dataset and Device Name of config dataset
			#2. Perform inner join between destDeviceName of cdr dataset and Device Name of config dataset

			joined_df_1 = pd.merge(cdr_filtered_df, config_data_df,left_on = 'origDeviceName', right_on = 'Device Name')

			#Rename the fields obtained from config dataframe
			joined_df_1.rename(columns = {'Device Pool': 'origDevicePool', 'CSS': 'origDeviceCSS','Location': 'origDeviceLocation'}, inplace = True)

			#Perform second join - between destDeviceName from cdr dataframe and Device Name field from cluster config dataframe:
			final_joined_df = pd.merge(joined_df_1,config_data_df, left_on = 'destDeviceName',right_on = 'Device Name')

			#Rename columns:
			final_joined_df.rename(columns = {'Device Pool': 'destDevicePool', 'CSS': 'destDeviceCSS','Location': 'destDeviceLocation'}, inplace = True)


			#Save the final processed dataset which is the INNER join of CDR data and Cluster config data(on the device name fields) in a new csv:
			final_joined_df.to_csv('processed_data/final_joined_data.csv',index = False)



class GetVisualisationsTask(luigi.Task):

	def requires(self):
		return JoinCdrAndClusterConfigDataTask()

	def output(self):
		return luigi.LocalTarget('data-visualisation/')

	def get_time_based_visualization(self, df):

		#Visualisation of call traffic by the hour:
		time_data = df[df['dateTimeConnect'] != 0].copy()
		
		#Creating a Call-Connect-Time field which displays dateTimeConnect values in UTC instead of Unix epoch timestamp:
		time_data['Call-Connect-Time'] = time_data['dateTimeConnect'].apply(lambda x: datetime.datetime.fromtimestamp(x).hour)

		call_traffic_hour = time_data['Call-Connect-Time'].value_counts()

		bar_plot = call_traffic_hour.plot.bar(title = 'Call traffic distribution by the hour')
		bar_plot.set_xlabel('Hour')
		bar_plot.set_ylabel('Number of calls')
		fig = bar_plot.get_figure()
		fig.savefig(os.path.join(self.output().path,'call_traffic_by_hour.png'))

		#Viewing distribution of calls by call duration:

		time_stamps = [0,60,300,600,3000]
		call_duration_values = {} #Key: call duration range, value: number of records with duration in that range

		for ind in range(0,len(time_stamps) - 1):
		    #Get count of all records with a duration between the two specified time stamps
		    res = time_data[time_data['duration'].between(time_stamps[ind],time_stamps[ind+1])]['duration'].count()
		    call_duration_values[f'{time_stamps[ind]} - {time_stamps[ind + 1]}'] = res

		call_duration_values['> 3000'] = time_data[time_data['duration'] > 3000]['duration'].count()

		
		plot_data = pd.Series(call_duration_values)
		plot = plot_data.plot.bar(title = 'Distribution of calls by call duration')
		plot.set_xlabel('Call duration range (in seconds)')
		plot.set_ylabel('Number of calls')
		fig = plot.get_figure()
		fig.savefig(os.path.join(self.output().path,'call_duration-distribution.png'))


	def get_call_failure_visualization(self, df):

		#Get the cause codes data:
		with open('CDR-codes/cause_codes.json','r') as json_file:
			cause_codes_dict = json.load(json_file)

		failed_calls_data = df[df['CallStatus'] == 'Fail']

		#Analyzing failed calls by the cluster ID associated with the call
		data_to_plot = failed_calls_data['globalCallId_ClusterID'].value_counts()
		plot = data_to_plot.plot.bar(title = 'Failed calls by cluster ID')		
		plot.set_xlabel('Cluster ID')
		plot.set_ylabel('Number of failed calls')
		fig = plot.get_figure()
		fig.savefig(os.path.join(self.output().path,'failed_calls_by_cluster.png'))


		#Analyzing failed calls by the call origin time (ie the dateTimeOrigination field):
		failed_calls_hour_dist = failed_calls_data['dateTimeOrigination'].apply(lambda x: datetime.datetime.fromtimestamp(x).hour).value_counts()
		failed_calls_hour_plot = failed_calls_hour_dist.plot.bar(title = 'Failed calls by call origin hour')
		failed_calls_hour_plot.set_xlabel('dateTimeOrigination Hour')
		failed_calls_hour_plot.set_ylabel('Number of failed calls')
		fig = failed_calls_hour_plot.get_figure()
		fig.savefig(os.path.join(self.output().path,'failed_calls_by_hour.png'))

		#Analyzing the most common origin device location and destination device location for failed calls:

		failed_calls_orig_location = failed_calls_data['origDeviceLocation'].value_counts()[:5]
		plot = failed_calls_orig_location.plot.bar(title = 'Failed calls by origin device location')
		plot.set_xlabel('Origin Device Location')
		plot.set_ylabel('Number of failed calls')
		fig = plot.get_figure()
		fig.savefig(os.path.join(self.output().path,'failed_calls_by_origin_location.png'))

		failed_calls_dest_location = failed_calls_data['destDeviceLocation'].value_counts()[:5]
		plot = failed_calls_dest_location.plot.bar(title = 'Failed calls by destination device location')
		plot.set_xlabel('Destination Device Location')
		plot.set_ylabel('Number of failed calls')
		fig = plot.get_figure()
		fig.savefig(os.path.join(self.output().path,'failed_calls_by_destination_location.png'))
		



	def run(self):
		
		os.makedirs(self.output().path)

		df = pd.read_csv(os.path.join(self.input()[0][0].path,'final_joined_data.csv'), low_memory = False)

		#Get time based visualization:
		self.get_time_based_visualization(df)

		self.get_call_failure_visualization(df)