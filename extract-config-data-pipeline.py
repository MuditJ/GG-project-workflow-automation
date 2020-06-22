#Pipeline to do the following:
'''
1. Extract individual csv files from the cluster config dump. This is done
using the fact that some rows start with text such as 
'enduser.csv' meaning that the folloing rows represent end-user data until a new
row with some '.csv' comes along

2. Store these individual csv files in separate directories based on 
the cluster they belong to

3. Write separate tasks to extract information such as 
device data, enduser data, device feature data etc

4. Store this extracted data in one particular location
'''


import os,csv,json
import luigi

import constants
import pandas as pd
import numpy as np


class ExtractFromDataDumpTask(luigi.Task):

	#Passed as command-line argument. By default, parameters are treated as string
	target_path = luigi.Parameter(default = constants.CLUSTER_CONFIG_PATH)

	def requires(self):
		return None

	def output(self):
		return luigi.LocalTarget('extracted-config-data/cluster-wise-data/')

	def extract_files(self,csv_file):

		sub_directory_name = csv_file[:3] + '-Cluster-Data'
		#Make the directory for storing this particular CUCM config file's data
		new_path = os.path.join(self.output().path,sub_directory_name)
		os.makedirs(new_path)

		#CSV reader
		file_path = os.path.join(self.target_path,csv_file)
		with open(file_path,'r') as config_file:
			reader = csv.reader(config_file)
			flag = False #A value of True for flag means that current row is part of a csv
			for row in reader:
				if len(row) == 0:
					continue
				else:
					if '.csv' in row[0]: #Marks start of a new_csv 
						#print(row[0])
						if flag == True: #A file is currently active. Close and then open new
							out_file.close()
							print(f'Closing out file: {out_file}')

						else:
							flag = True
						#Start writing into a new file

						file_name = row[0].lstrip().split(' ')[0]
						print(f'Splitting on {row[0]}')
						out_file = open(os.path.join(new_path,file_name),'w')
						print(f'Current file: {file_name}')
						print(f'Out file: {out_file}')
						writer = csv.writer(out_file)
						row[0].lstrip(file_name)
						#print(row)
						writer.writerow(row)

					else:
						if flag == True: #Current row is part of a csv
							writer.writerow(row)
						else:
							pass

	def run(self):
		files = os.listdir(self.target_path)

		#Create the target directory(where the extracted data is to be stored)
		#os.makedirs ensures that any missing directories in the specified path is also created
		os.makedirs(self.output().path)
		for file in files:
			self.extract_files(file)

class ExtractPhoneDataTask(luigi.Task):

	def requires(self):
		return (ExtractFromDataDumpTask())

	def output(self):
		return [
		luigi.LocalTarget('extracted-config-data/all-clusters-phone-data'),
		self.input() #LocalTarget object pointing at the extracted-config-data directory
		]

	def run(self):
		
		#These are the fields to be extracted from the phone.csv files from the different clusters
		required_fields = ['Device Name','Device Pool','Location','Directory Number 1', 'Route Partition 1', 'Device Type', 'Phone Button Template','Softkey Template']

		#Collect data from the different csvs and store as a list of dictionaries
		phone_data = []

		for cluster_path in os.listdir(self.input().path):
			flag = False
			csv_file = os.path.join(self.input().path,cluster_path,'phone.csv')
			
			with open(csv_file,'r') as file:
				reader = csv.reader(file)
				if not flag:
					flag = True #This conditional only needs to be run once to define the following variables
					field_headers = next(reader) #Get the field headers from the csv file
					fields = {val:ind for ind,val in enumerate(field_headers)}
				for row in reader:
					phone_data.append({x:row[fields[x]] for x in required_fields})
		
		print(len(phone_data))

		
		#Create the output directory
		os.makedirs(self.output()[0].path)

		#Write this data into a JSON file

		with open(os.path.join(self.output()[0].path,'phone_data.json'),'w') as json_file:
			json.dump(phone_data,json_file)

class ExtractAllDeviceDataTask(luigi.Task):

	def requires(self):
		return ExtractPhoneDataTask()

	def output(self):
		return [
		luigi.LocalTarget('extracted-config-data/all-clusters-device-data'),
		self.input()[1] #LocalTarget object pointing at the extracted-config-data directory
		]

	def run(self):
		all_devices_data = []

		#Extract from phone.csv
		required_fields_phone_csv = ['Device Name','Device Pool', 'CSS', 'Location']
		required_fields_trunk_csv = ['DEVICE NAME', 'DEVICE POOL', 'CALLING SEARCH SPACE', 'LOCATION']

		for cluster_path in os.listdir(self.input()[1].path):
			
			#Gettting data from phone.csv files
			flag = False
			csv_file = os.path.join(self.input()[1].path,cluster_path,'phone.csv')
			with open(csv_file,'r') as file:
				reader = csv.reader(file)
				if not flag:
					flag = True #This conditional only needs to be run once -  to get the field headers
					field_headers = next(reader) #Get the field headers from the csv file
					field_indices = {val:ind for ind,val in enumerate(field_headers)}
					for row in reader: #For each row of data:
						data_dict = {header:row[field_indices[header]] for header in required_fields_phone_csv}
						all_devices_data.append(data_dict)

			
			#Getting data from trunk.csv files
			flag = False
			csv_file = os.path.join(self.input()[1].path,cluster_path,'trunk.csv')
			with open(csv_file,'r') as file:
				reader = csv.reader(file)
				if not flag:
					flag = True #This conditional only needs to be run once -  to get the field headers
					field_headers = next(reader) #Get the field headers from the csv file
					field_indices = {val:ind for ind,val in enumerate(field_headers)}
				for row in reader: #For each row of data:

					data_dict = {required_fields_phone_csv[ind]:row[field_indices[required_fields_trunk_csv[ind]]] for ind in range(0,len(required_fields_trunk_csv))}
					all_devices_data.append(data_dict)

		os.makedirs(self.output()[0].path)

		with open(os.path.join(self.output()[0].path,'all_devices_data.json'),'w') as json_file:
			json.dump(all_devices_data,json_file)


class ExtractEnduserDataTask(luigi.Task):
	def requires(self):
		return ExtractAllDeviceDataTask()

	def output(self):
		#Two json files will be created - one to store data for all
		#devices and one for phone only data
		return [
		luigi.LocalTarget('extracted-config-data/all-clusters-enduser-data'),
		self.input()[1]
		]

	def run(self):
		all_devices_data = []
		phone_data = []

		for cluster_path in os.listdir(self.input()[1].path):
		#for cluster_path in [x for x in os.listdir(self.input()[1].path) if '-Cluster-Data' in x]:
			flag = False
			csv_file = os.path.join(self.input()[1].path,cluster_path,'enduser.csv')
		
			with open(csv_file,'r') as file:
				reader = csv.reader(file)
				fields = next(reader)
				field_headers = {val:ind for ind,val in enumerate(fields)}
				device_name_field_indices = [field_headers[val] for val in fields if 'DEVICE NAME' in val]
				#Not all device name fields will hold an IP phone device - may
				#hold a Jabber phone device instead or be empty
				for row in reader:
					all_device_dict = {}
					phone_only_dict = {}

					#Add the user ID to both dictionaries
					all_device_dict['User'] = row[4]
					phone_only_dict['User'] = row[4]

					#Get a list of all devices - for all_devices_data, and a separate
					#list for just phone devices
					all_devices = [row[ind] for ind in device_name_field_indices]
					phone_devices = [dev for dev in all_devices if 'SEP' in dev]


					all_device_dict['Devices'] = all_devices
					phone_only_dict['Devices'] = phone_devices
					
					all_devices_data.append(all_device_dict)
					phone_data.append(phone_only_dict)

		os.makedirs(self.output()[0].path)

		with open(os.path.join(self.output()[0].path,'enduser_data_all_devices.json'),'w') as json_file:
			json.dump(all_devices_data,json_file)

		
		with open(os.path.join(self.output()[0].path,'enduser_data_phone_only.json'),'w') as json_file:
			json.dump(phone_data,json_file)



class ExtractFeaturesTemplateDataTask(luigi.Task):

	'''This task extracts the phone button template and softkey template data from
	the cluster config csv files. Each phone device has a particular phone button 
	template and softkey template associated and thus, the phone devices can be joined with the 
	phone button and softkey template data to get a list of subscribed features for the phone '''
	def requires(self):
		return ExtractEnduserDataTask()

	def output(self):
		return [
		luigi.LocalTarget('extracted-config-data/phone-button-softkey-data'),
		self.input()[1]
		]

	def get_phone_button_template_data(self):
		
		phone_button_template_data = []
		for cluster_path in os.listdir(self.input()[1].path):

			flag = False
			csv_file_one = os.path.join(self.input()[1].path,cluster_path,'phonebuttontemplate.csv')
			
			with open(csv_file_one,'r') as file:
				reader = csv.reader(file)
				if not flag:
					flag = True #This conditional only needs to be run once -  to get the field headers
					field_headers = next(reader) #Get the field headers from the csv file
					fields = {val:ind for ind,val in enumerate(field_headers)}

					#This represents the columns that we want to keep i.e. these represent the type of
					#PhoneButtonTemplate feature. 
					feature_fields = [header for header in field_headers if 'TYPE OF FEATURE' in header]
				for row in reader: #For each row of data:
					data_dict = {}
					type_of_feature_vals = [(feature,row[fields[feature]]) for feature in feature_fields]
					data_dict['Phone Button Template'] = row[0]
					data_dict.update({val[0]:val[1] for val in type_of_feature_vals})
					phone_button_template_data.append(data_dict)

		with open(os.path.join(self.output()[0].path,'phone_button_template_data.json'),'w') as json_file:
			json.dump(phone_button_template_data,json_file)

	def get_softkey_template_data(self):
	
		softkey_template_data = []

		for cluster_path in os.listdir(self.input()[1].path):

			flag = False
			csv_file_two = os.path.join(self.input()[1].path,cluster_path,'softkeytemplate.csv')

			with open(csv_file_two,'r') as file:
				reader = csv.reader(file)
				if not flag:
					flag = True #This conditional only needs to be run once -  to get the field headers
					field_headers = next(reader) #Get the field headers from the csv file

					#Get indices of all those fields which have SOFT KEY as name
					field_indices = [ind for ind,val in enumerate(field_headers) if 'SOFT KEY' in val]
					
				for row in reader: #For each row of data:
					data_dict = {}
					softkey_template_vals = [row[ind] for ind in field_indices]
					data_dict['Soft Key Template'] = row[0]
					data_dict.update({f'Soft Key {x + 1}': softkey_template_vals[x] for x in range(0,len(softkey_template_vals))})
					softkey_template_data.append(data_dict)


		with open(os.path.join(self.output()[0].path,'softkey_template_data.json'),'w') as json_file:
			json.dump(softkey_template_data,json_file)


	def run(self):

		#Store the to-be-read data as a list of dictionaries before writing into a JSON file

		os.makedirs(self.output()[0].path)
		
		self.get_phone_button_template_data()

		self.get_softkey_template_data()



if __name__ == "__main__":
	luigi.run()

