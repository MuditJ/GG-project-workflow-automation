import os,sys
import luigi
import time

#Simple pipeline to write Hello World into a file and replace World with a name


#Make sure to run the luigid daemon which schedules the jobs,
#and provides a  web interface to view the dependencies

#Run the daemon using the command:

#luigid --background --port=8082 


#This is the primary task ie the task with no dependencies
class HelloWorldTask(luigi.Task):
	
	def requires(self):
		return None

	def output(self):
		return luigi.LocalTarget('helloworld.txt')

	def run(self):
		time.sleep(20)
		with self.output().open('w') as file:
			file.write('Hello World!')
		time.sleep(20)


#Reads input provided via output method of HelloWorldTask
class HelloNameTask(luigi.Task):
	name = luigi.Parameter()

	def requires(self):
		return [HelloWorldTask()]

	def output(self):
		return luigi.LocalTarget(self.input()[0].path.rstrip('world.txt') + self.name + '.txt')

	def run(self):
		time.sleep(20)
		with self.input()[0].open() as infile, self.output().open('w') as outfile:
			text = infile.read()
			text = text.replace('World',self.name)
			outfile.write(text)
		time.sleep(20)


class SampleTask(luigi.Task):

	def requires(self):
		return HelloNameTask(name = 'Mudit')

	def output(self):
		return luigi.LocalTarget('data.txt')

	def run(self):
		with open(self.output().path,'w') as file:
			file.write('This task ran')




if __name__ == "__main__":
	luigi.run()

