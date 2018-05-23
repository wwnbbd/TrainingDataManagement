from trainingDataManager import *
import argparse
from utils import *
import configparser

parser = argparse.ArgumentParser(description="add filter condition")
parser.add_argument("--mode", default="filter", type=str, help="select function. The following three types are avaliable: filter,delete,add")
parser.add_argument("--id", default="None", type=str, help="target class id")
parser.add_argument("--prob", default="1.0", type=str, help="confidence threshold")
parser.add_argument("--subclass", default="0", type=str, help="extract subclasses")
parser.add_argument("--chinese", default="None", type=str, help="chinese name for new node")
parser.add_argument("--father", default="None", type=str, help="father of new node")
parser.add_argument("--size", default="ALL", type=str, help="the number of return images, default:return all the filtered images")
parser.add_argument("--file", default="None",type=str,help="get input from file")
parser.add_argument("--order",default="original",choices=["original","shuffle","descending"], help="original:the output order is the same as the storage order. shuffle:random order. descending:the descending order of probability.")
parser.add_argument("--priority",default="human", choices=["human","machine"],help="human:human annotation first, if there is not enough human annotation files,using machine annotations. machine:machine annotation first, use human annotation files when there is not enough machine annotation files.")
parser.add_argument("--re",default="None",type=str,help="Using regex to select candidates")

args = parser.parse_args()


#store input arguments
config = {
	"mode":args.mode,
	"id":args.id,
	"prob":args.prob,
	"subclass":args.subclass,
	"chinese":args.chinese,
	"father":args.father,
	"size":args.size,
	"file":args.file,
	"order":args.order,
	"priority":args.priority,
	"re":args.re
}

if args.file != "None":
	mconfig = configparser.ConfigParser()
	mconfig.read(args.file)
	config["mode"] = mconfig.sections()[0]
	for key in mconfig[config["mode"]]:
		config[key] = mconfig[config["mode"]][key]



if config["mode"] == "filter":
	#parse input arguments
	if config["id"] == "None" and config["chinese"] == "None" and config["file"] == "None" and config["re"] =="None":
		raise Exception("Must use class id, chinese name, file or regex to filter!")
	#if ids are given, using ids
	if config["id"] != "None":
		candidates_ids = config["id"].strip().split(",")
		if len(config["prob"].strip().split(",")) == 1:
			candidates_prob = [float(config["prob"].strip().split(",")[0])] * len(candidates_ids)
		elif config["prob"] == "1.0":
			candidates_prob = [1.0] * len(candidates_ids) 
		else:
			candidates_prob = config["prob"].strip().split(",")
			candidates_prob = [float(i) for i in candidates_prob]
			assert len(candidates_prob) == len(candidates_ids)
		
		if config["subclass"] == "0":
			candidates_subclass = [False] * len(candidates_ids)
		elif config["subclass"] == "1":
			candidates_subclass = [True] * len(candidates_ids)
		else:
			tmp = config["subclass"].strip().split(",")
			candidates_subclass = [False] * len(tmp)
			for i in range(len(tmp)):
				if tmp[i] == "1":
					candidates_subclass[i] = True
			assert len(candidates_subclass) == len(candidates_ids)

	if config["id"] == "None" and config["chinese"] != "None":
		candidates_chinese = config["chinese"].strip().split(",")
		candidates_ids = list(map(convert_to_id,candidates_chinese))
		if len(config["prob"].strip().split(",")) == 1:
			candidates_prob = [float(config["prob"].strip().split(",")[0])] * len(candidates_ids)
		elif config["prob"] == "1.0":
			candidates_prob = [1.0] * len(candidates_ids)
		else:
			candidates_prob = config["prob"].strip().split(",")
			candidates_prob = [float(i) for i in candidates_prob]
			assert len(candidates_prob) == len(candidates_ids)
		
		if config["subclass"] == "0":
			candidates_subclass = [False] * len(candidates_ids)
		elif config["subclass"] == "1":
			candidates_subclass = [True] * len(candidates_ids)			
		else:
			tmp = config["subclass"].strip().split(",")
			candidates_subclass = [False] * len(tmp)
			for i in range(len(tmp)):
				if tmp[i] == "1":
					candidates_subclass[i] = True
			assert len(candidates_subclass) == len(candidates_ids)

	if config["id"] == "None" and config["chinese"] == "None" and config["re"] != "None":#using regex to specify ids
		candidates_ids = get_ids_using_re(config["re"])
		if len(config["prob"].strip().split(",")) == 1:
			candidates_prob = [float(config["prob"].strip().split(",")[0])] * len(candidates_ids)
		else:
			candidates_prob = config["prob"].strip().split(",")
			candidates_prob = [float(i) for i in candidates_prob]
			assert len(candidates_prob) == len(candidates_ids)
	
		if config["subclass"] == "0":
			candidates_subclass = [False] * len(candidates_ids)
		elif config["subclass"] == "1":
			candidates_subclass = [True] * len(candidates_ids)
		else:
			tmp = config["subclass"].strip().split(",")
			candidates_subclass = [False] * len(tmp)
			for i in range(len(tmp)):
				if tmp[i] == "1":
					candidates_subclass[i] = True
			assert len(candidates_subclass) == len(candidates_ids)


	#main process
	a = manager()
	a.load()
	a.add_filter_condition(candidates_ids,candidates_prob,candidates_subclass)
	result = a.get_filtered_candidates()#both human and machine
	
	#concat result for further filtering
	for i in range(len(candidates_ids)):
		if len(result["human"][i])!= 0: result["human"][i] = pd.concat(result['human'][i])
		if len(result["machine"][i])!=0: result["machine"][i] = pd.concat(result["machine"][i])
	#deal with order argument
	if config["order"] == "shuffle":
		for i in range(len(candidates_ids)):
			if len(result["human"][i]): result['human'][i]=result["human"][i].sample(frac=1)
			if len(result["machine"][i]): result['machine'][i]=result["machine"][i].sample(frac=1)
	
	if config["order"] == "descending":
		for i in range(len(candidates_ids)):
			if len(result["human"][i]): result['human'][i]=result['human'][i].sort_values(by='prob',ascending=False)
			if len(result['machine'][i]): result['machine'][i]=result['machine'][i].sort_values(by="prob",ascending=False)
	
	#deal with priority
	if config["priority"] == "human":
		final = []
		for i in range(len(candidates_ids)):
			combine = []
			if len(result["human"][i]): combine.append(result["human"][i])
			if len(result["machine"][i]): combine.append(result["machine"][i])
			if len(combine): 
				final.append(pd.concat(combine))
			else:
				final.append(combine)
	if config["priority"] == "machine":
		final = []
		for i in range(len(candidates_ids)):
			combine = []
			if len(result["machine"][i]): combine.append(result["machine"][i])
			if len(result["human"][i]): combine.append(result["human"][i])
			if len(combine): 
				final.append(pd.concat(combine))
			else:
				final.append(combine)

	#deal with size argument
	#print(final)
	if config["size"] != "ALL":
		candidates_size = config["size"].strip().split(",")
		if len(candidates_size) == 1:
			candidates_size = [int(candidates_size[0])] * len(candidates_ids)
		else:
			candidates_size = [int(i) for i in candidates_size]
			assert len(candidates_size) == len(candidates_ids)	
		for i in range(len(candidates_size)):
			final[i] = final[i][:min(candidates_size[i],len(final[i]))]	

	#print final result
	for i in range(len(final)):
		print("===========================")
		print(final[i])


#########################################################################################################
#operations for indexing
if config["mode"] == "add":
	add_node(config["chinese"], str(config["id"]), str(config["father"]))

if config["mode"] == "delete":
	_,_,n_i,i_n,f_c,c_f = get_basic_index_dict()
	father = c_f[str(config["id"])]
	print("before delete father's children:")
	print(f_c[c_f[str(config["id"])]])
	print("before delete, target node's children:")
	print(f_c[str(config["id"])])
	delete_node(str(config["id"]))
	_,_,n_i,i_n,f_c,c_f = get_basic_index_dict()
	#print(len(f_c))
	#print(len(c_f))
	print("after delete, father's childre:")
	print(f_c[father])

	

