import numpy as np
import pandas as pd
from config import basic_path
from utils import *
import os
import time
from time import gmtime, strftime
import shutil
from datetime import datetime

class manager():
	def __init__(self):
		self.dataframes_human = []
		self.dataframes_machine = []
		self.ids = []
		self.probs = []
		self.subclass_flags = []

	def load(self):
		print("Start Loading Human Annotation Files...\n")
		indexing_files = os.listdir(basic_path["indexing_file_path"])
		human_start = time.time()
		for item in indexing_files:
			item_path = os.path.join(basic_path["indexing_file_path"],item)
			#annotation_frame = pd.read_csv(item_path,sep="\t",header=None,names=["file_path","class_id","prob"],dtype={"class_id":np.int32,"prob":np.float32})
			annotation_frame = parse_single_annotation_file(item_path)
			self.dataframes_human.append(annotation_frame)
		human_end = time.time()
		print("Loading Human Annotation Files Done!  Using {} seconds\n".format(human_end-human_start))

		print("Start Loading Machine Annotation Files...\n")
		indexing_files = os.listdir(basic_path["indexing_file_machine_path"])
		machine_start = time.time()
		for item in indexing_files:
			item_path = os.path.join(basic_path["indexing_file_machine_path"], item)
			#annotation_frame = pd.read_csv(item_path, sep="\t",header=None,names=["file_path","class_id","prob"],dtype={"class_id":np.int32,"prob":np.float32})
			annotation_frame = parse_single_annotation_file(item_path)
			self.dataframes_machine.append(annotation_frame)
		machine_end = time.time()
		print("Loading Machine Annotation Files Done! Using {} seconds\n".format(machine_end-machine_start))

	def load_with_keywords(self, keywords):
		pass
	
	def load_with_date(self,begin,end):
		pass	


	def add_filter_condition(self, ids, probs, subclass_flags):
		#names should be ids
		if type(ids) != list or type(probs) != list or type(subclass_flags) != list:
			raise Exception("All the input types should be list!")
		if len(ids) != len(probs) or len(probs) != len(subclass_flags):
			raise Exception("The three input parameters should have equal length!")
		for i in range(len(ids)):
			if not is_number(ids[i]):
				raise Exception("Id should be number!")
			if probs[i]<0 or probs[i]>1:
				raise Exception("probability should between 0--1")
				
		self.ids += ids
		self.probs += probs
		self.subclass_flags += subclass_flags

	def delete_condition(self, ids):
		if type(ids) != list:
			raise Exception("The input type should be list!")	
		for i in range(len(ids)):
			if not is_number(ids[i]):
				raise Exception("id should be number!")
		pos = []
		for i in range(len(ids)):
			for j in range(len(self.ids)):
				if ids[i] == self.ids[j]:
					pos.append(j)
		pos = list(set(pos))
		removed_ids = []
		removed_prob = []
		removed_subclass = []
		for i in range(len(self.ids)):
			if i not in pos:
				removed_ids.append(self.ids[i])
				removed_prob.append(self.probs[i])
				removed_subclass.append(self.subclass_flags[i])
		self.ids = removed_ids
		self.probs = removed_prob
		self.subclass_flags = removed_subclass
		#for item in pos:
		#	del self.ids[item]
		#	del self.probs[item]
		#	del self.subclass_flags[item]

	def delete_all_condition(self):
		self.ids = []
		self.probs = []
		self.subclass_flags = []

	def get_filtered_candidates(self):
		results_human = []
		all_subclass_ids = get_all_subclasses(self.ids)
		for i in range(len(self.ids)):
			tmp = []			
			for dataframe in self.dataframes_human:
				filtered = dataframe[(dataframe['class_id'] == int(self.ids[i])) & (dataframe['prob']>=self.probs[i])].copy()
				if len(filtered.index):
					tmp.append(filtered)
				if self.subclass_flags[i]:
					for sub in all_subclass_ids[i]:
						filtered = dataframe[(dataframe['class_id'] == int(sub)) & (dataframe['prob']>=self.probs[i])].copy()
						if len(filtered.index):
							tmp.append(filtered)
			results_human.append(tmp)

		results_machine = []
		all_subclass_ids = get_all_subclasses(self.ids)
		for i in range(len(self.ids)):
			tmp = []
			for dataframe in self.dataframes_machine:
				filtered = dataframe[(dataframe['class_id'] == int(self.ids[i])) & (dataframe['prob']>=self.probs[i])].copy()
				if len(filtered.index):
					tmp.append(filtered)
				if self.subclass_flags[i]:
					for sub in all_subclass_ids[i]:
						filtered = dataframe[(dataframe["class_id"] == int(sub)) & (dataframe["prob"]>=self.probs[i])].copy()
						if len(filtered.index):
							tmp.append(filtered)
			results_machine.append(tmp)
		return {"human":results_human,"machine":results_machine}

	def add_filter_condition_using_re(self, exp, prob=1.0):
		results = get_ids_using_re(exp)
		self.add_filter_condition(results,[prob]*len(results),[False]*len(results))


#######################################admin function###############################
def add_node(chinese_name, node_id, father_id):
	if not isinstance(chinese_name, str):
		raise Exception("chinese name should be string")
	if not isinstance(node_id, str):
		raise Exception("node id should be string")
	if not isinstance(father_id, str):
		raise Exception("father id should be string")
	_,_,n_i,i_n,f_c,c_f = get_basic_index_dict()
	if chinese_name in n_i:
		raise Exception("Chinese name already exits!")
	if node_id in i_n:
		raise Exception("Node ID already exits!")
	if (father_id not in f_c) and (father_id not in c_f):
		raise Exception("Father ID not exits!")

	#doing backup
	dest_dir = basic_path["indexing_backup_path"]+str(datetime.now())+"-add"+"/"
	os.mkdir(dest_dir)
	copytree(basic_path["indexing_dir_path"], dest_dir)

	with open(basic_path["relation_index_path"],'a') as relation:
		relation.write(father_id + ":" +node_id + "\n")

	with open(basic_path["chinese_id_index_path"],'a') as f:
		f.write(chinese_name + ":" + node_id + "\n")

def delete_node(node_id):
	'''
	this function only change relation file, the name_id file will remain the same
	and all the indexing files will remain the same
	'''
	if not isinstance(node_id, str):
		raise Exception("node id should be string")
	
	#doing backup
	time_now = str(datetime.now())
	dest_dir = basic_path["indexing_backup_path"] +time_now+"-delete_node"+"/"
	os.mkdir(dest_dir)
	copytree(basic_path["indexing_dir_path"], dest_dir)

	_,_,n_i,i_n,f_c,c_f = get_basic_index_dict()
	if (node_id not in c_f) and (node_id not in f_c):
		raise Exception("Node not exits in the tree!")
	
	if node_id not in c_f:
		raise Exception("Can not delete root!")
	father = c_f[node_id]
	f_c[father].remove(node_id)#remove from father 
	if node_id in f_c:#have children
		children = f_c[node_id]
		f_c[father] += children
		f_c = {i:f_c[i] for i in f_c if i!= node_id}#remove node
	with open(basic_path["relation_index_path"],"w") as f:
		for k,v in f_c.items():
			for child in v:
				f.write(k+":"+child+"\n")


