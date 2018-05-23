from trainingDataManager import *
import argparse
from utils import *
import configparser

parser = argparse.ArgumentParser(description="parse arguments")
parser.add_argument("--mode",default="filter", choices=["filter","add","delete"], help="the functions for this script")
######################################################
parser.add_argument("--id", default="None", type=str, help="the class id")
parser.add_argument("--id-prob", default="1.0", type=str, help="the probability for ids")
parser.add_argument("--id-subclass", default="0",type=str,help="wheather to select the children")
parser.add_argument("--id-size", default="ALL", type=str,help="how many candidates to select")
parser.add_argument("--id-subclass-mode", default="0", type=str, help="if 0 the all subclasses will be viewed as a single class, if 1, all subclasses will be viewed separately")
#######################################################
parser.add_argument("--chinese", default="None", type=str, help="the chinese names for classes")
parser.add_argument("--chinese-prob", default="1.0", type=str, help="the probability for chinese names")
parser.add_argument("--chinese-subclass",default="0", type=str, help="wheather to select the children for chinese name")
parser.add_argument("--chinese-size", default="ALL", type=str,help="how many candidates to select")
parser.add_argument("--chinese-subclass-mode",default="0",type=str, help="if 0, merge to one class, if 1, viewed as different classes")
########################################################
parser.add_argument("--re", default="None", type=str, help="using regex to give ids")
parser.add_argument("--re-prob", default="1.0", type=str, help="the probability for regex")
parser.add_argument("--re-subclass",default="0", type=str, help="wheather to select the children")
parser.add_argument("--re-size",default="ALL",type=str, help="how many candidates to select")
parser.add_argument("--re-subclass-mode",default="0",type=str, help="if 0 , merge to one class, if 1, viewed as different classes")
########################################################
parser.add_argument("--subtract-id", default="None",type=str, help="the class which has this id will be excluded")
parser.add_argument("--subtract-id-subclass", default="0", type=str, help="subtract subclass or not")
parser.add_argument("--subtract-chinese", default="None",type=str,help="the class which has this id will be excluded")
parser.add_argument("--subtract-chinese-subclass", default="0", type=str, help="substract subclass or not")
parser.add_argument("--subtract-re", default="None",type=str,help="the class which matches regex will be excluded")
parser.add_argument("--subtract-re-subclass", default="0", type=str, help="subtract subclass or not")
#######################################################
parser.add_argument("--priority", default="human", choices=["human","machine"], help="use human or machine data first")
parser.add_argument("--order", default="original", choices=["original","shuffle","descending"],help="the order of returned candidates")
parser.add_argument("--file",default="None",type=str, help="config file path")
parser.add_argument("--father", default="None", type=str, help="the father id for new node")

args = parser.parse_args()


#store input arguments
config = {
	"mode":args.mode,
	"id":args.id,
	"id-prob":args.id_prob,
	"id-subclass":args.id_subclass,
	"id-subclass-mode":args.id_subclass_mode,
	"id-size":args.id_size,
	"chinese":args.chinese,
	"chinese-prob":args.chinese_prob,
	"chinese-subclass":args.chinese_subclass,
	"chinese-subclass-mode":args.chinese_subclass_mode,
	"chinese-size":args.chinese_size,
	"re":args.re,
	"re-prob":args.re_prob,
	"re-subclass":args.re_subclass,
	"re-subclass-mode":args.re_subclass_mode,
	"re-size":args.re_size,
	"subtract-id":args.subtract_id,
	"subtract-id-subclass":args.subtract_id_subclass,
	"subtract-chinese":args.subtract_chinese,
	"subtract-chinese-subclass":args.subtract_chinese_subclass,
	"subtract-re":args.subtract_re,
	"subtract-re-subclass":args.subtract_re_subclass,
	"priority":args.priority,
	"order":args.order,
	"file":args.file,
	"father":args.father
}


#TODO Deal with config file#######################################################
if args.file != "None":
	mconfig = configparser.ConfigParser()
	mconfig.read(args.file, encoding="utf-8")
	for mode in ["filter", "add","delete"]:
		if mode in mconfig.sections():
			config["mode"] = mconfig.sections()[0]
			break
	for key in mconfig[config["mode"]]:
		config[key] = mconfig[config["mode"]][key]
###################################################################################


if config["mode"] == "filter":
	candidates_ids = []
	candidates_prob = []
	candidates_subclass = []
	candidates_size = []
	
	#parse input arguments
	if config["id"] == "None" and config["chinese"] == "None" and config["file"] == "None" and config["re"] =="None":
		raise Exception("Must use class id, chinese name, file or regex to filter!")
	#if ids are given, using ids
	if config["id"] != "None":
		id_ids = config["id"].strip().split(",")
		id_ids, id_prob, id_subclass, id_size = parse_argument_section(id_ids, config["id-prob"], config["id-subclass"], config["id-size"], config["id-subclass-mode"])
		#merge
		candidates_ids = candidates_ids + id_ids
		candidates_prob = candidates_prob + id_prob
		candidates_subclass = candidates_subclass + id_subclass
		candidates_size = candidates_size + id_size
	
	if config["chinese"] != "None":
		candidates_chinese = config["chinese"].strip().split(",")
		chinese_ids = list(map(convert_to_id,candidates_chinese))
		chinese_ids, chinese_prob, chinese_subclass, chinese_size = parse_argument_section(chinese_ids, config["chinese-prob"], config["chinese-subclass"], config["chinese-size"], config["chinese-subclass-mode"])
		#merge
		candidates_ids = candidates_ids + chinese_ids
		candidates_prob = candidates_prob + chinese_prob
		candidates_subclass = candidates_subclass + chinese_subclass
		candidates_size = candidates_size + chinese_size


	if config["re"] != "None":#using regex to specify ids
		re_ids = get_ids_using_re(config["re"])
		re_ids, re_prob, re_subclass, re_size = parse_argument_section(re_ids, config["re-prob"], config["re-subclass"], config["re-size"],config["chinese-subclass-mode"])
		#merge
		candidates_ids = candidates_ids + re_ids
		candidates_prob = candidates_prob + re_prob
		candidates_subclass = candidates_subclass + re_subclass
		candidates_size = candidates_size + re_size

	#subtract
	subtract_list = []
	if config["subtract-id"] != "None":
		subtract_id_list = config["subtract-id"].strip().split(",")	
		subtract_list += parse_subtract(subtract_id_list, config["subtract-id-subclass"])
	if config["subtract-chinese"] != "None":
		subtract_chinese_list = list(map(convert_to_id, config["subtract-chinese"].strip().split(",")))
		subtract_list += parse_subtract(subtract_chinese_list, config["subtract-chinese-subclass"])
	if config["subtract-re"] != "None":
		subtract_re_list = get_ids_using_re(config["subtract-re"])
		subtract_list += parse_subtract(subtract_re_list, config["subtract-re-subclass"])
	
	#subtract filter
	pos = []
	for i in range(len(subtract_list)):
		for j in range(len(candidates_ids)):
			if subtract_list[i] == candidates_ids[j]:
				pos.append(j)
	removed_ids = []
	removed_prob = []
	removed_subclass = []
	removed_size = []
	for i in range(len(candidates_ids)):
		if i not in pos:
			removed_ids.append(candidates_ids[i])
			removed_prob.append(candidates_prob[i])
			removed_subclass.append(candidates_subclass[i])
			removed_size.append(candidates_size[i])
	candidates_ids = removed_ids
	candidates_prob = removed_prob
	candidates_subclass = removed_subclass
	candidates_size = removed_size

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
	for i in range(len(candidates_size)):
		if candidates_size[i] != "ALL":
			final[i] = final[i][:min(int(candidates_size[i]),len(final[i]))]	

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

	

