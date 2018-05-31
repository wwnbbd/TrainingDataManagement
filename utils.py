from config import basic_path
import queue
import re
import shutil
import os
import numpy as np
import pandas as pd
import multiprocessing as mp
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def is_chinese(text):
	return all('\u4e00' <= char <= '\u9fff' for char in text)

def get_basic_index_dict():
	e_c = dict() #stands for english name to chinese name
	c_e = dict() #stands for chinese name to english name
	with open(basic_path["english_chinese_index_path"], encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			parts = line.strip("\n").split("\t")
			if len(parts) > 1:
				e_c[parts[0]] = parts[1]
				c_e[parts[1]] = parts[0]
	
	n_i = dict() #chinese name to id
	i_n = dict() #id to chinese name
	with open(basic_path["chinese_id_index_path"], encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			parts = line.strip("\n").split(":")
			if len(parts) > 1:
				n_i[parts[0]] = parts[1]
				i_n[parts[1]] = parts[0]
	
	f_c = dict() #relation dict for father to child
	c_f = dict() # relation dict for child to father
	with open(basic_path["relation_index_path"], encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			parts = line.strip("\n").split(":")
			if len(parts) > 1:
				if parts[0] in f_c:
					children  = f_c[parts[0]]
					children.append(parts[1])
					f_c[parts[0]] = children
				else:
					f_c[parts[0]] = [parts[1]]

				c_f[parts[1]] = parts[0]

	return e_c, c_e, n_i, i_n, f_c, c_f

def convert_to_id(name):
	e_c,_,n_i,i_n,_,_ = get_basic_index_dict()
	if is_number(name):
		if name in i_n:
			return name	
	if is_chinese(name):
		if name in n_i:
			return n_i[name]
	raise Exception("invalid name: Not Found in the dictionary.")

def get_all_subclasses(names):
	if type(names) != list:
		raise Exception("The input type should be list which contains names ids.")
	for i in range(len(names)):
		if not is_number(names[i]):
			raise Exception("The "+str(i)+"th name should be digit number.")
	_,_,_,_,f_c,c_f = get_basic_index_dict()
	
	all_children_id = []
	for name in names:
		children_id = []
		q = queue.Queue()
	
		def queue_put(q,items):
			for item in items:
				q.put(item)

		if name in f_c:
			children_id += f_c[name]
			queue_put(q,f_c[name])
		while(q.qsize()):
			subname = q.get()
			if subname in f_c:
				children_id += f_c[subname]
				queue_put(q,f_c[subname])
		all_children_id.append(children_id)
	return all_children_id

def get_leaves(names):
	if type(names) != list:
		raise Exception("The input type should be list which contains names ids.")
	for i in range(len(names)):
		if not is_number(names[i]):
			raise Exception("The "+str(i)+"th name should be digit number.")
	_,_,_,_,f_c,c_f = get_basic_index_dict()
	all_children_id = get_all_subclasses(names)
	
	leaves = []
	for children in all_children_id:
		tmp = []
		for item in children:
			if item not in f_c:
				tmp.append(item)
		leaves.append(tmp)

	return leaves

def get_ids_using_re(exp):#this function is used to match chinese only
	pattern = re.compile(exp)
	_,_,n_i,i_n,_,_ = get_basic_index_dict()
	keys = list(n_i.keys())
	match_result = list(map(pattern.match, keys))
	results = []
	for i in range(len(match_result)):
		if match_result[i] is not None:
			results.append(n_i[keys[i]])
	return results

def copytree(src, dst, symlinks=False, ignore=None):
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
 			shutil.copy2(s, d)

def parse_argument_section(ids, prob, subclass, size, subclass_mode, origin):
	assert type(ids) == list
	if type(prob) != str:
		raise Exception("prob should be string")
	if type(subclass) != str:
		raise Exception("subclass should be string")
	if type(size) != str:
		raise Exception("size should be string")
	if type(subclass_mode) != str:
		raise Exception("subclass mode should be string")
	if type(origin) != list:
		raise Exception("origin should be list")
	if len(ids) != len(origin):
		raise Exception("the length of origin and ids should be the same.")

	candidates_prob = prob.strip().split(",")
	if len(candidates_prob) == 1:
		candidates_prob = candidates_prob * len(ids)
	if len(candidates_prob) != len(ids):
		raise Exception("the number of probability should match the number of id ")
	candidates_prob = list(map(float,candidates_prob))

	candidates_subclass = subclass.strip().split(",")
	if len(candidates_subclass) == 1:
		candidates_subclass = candidates_subclass * len(ids)
	if len(candidates_subclass) != len(ids):
		raise Exception("the number of subclass flags should match the number of id")
	for i in range(len(candidates_subclass)):
		if candidates_subclass[i] == "1":
			candidates_subclass[i] = True
		else:
			candidates_subclass[i] = False

	candidates_size = size.strip().split(",")
	if len(candidates_size) == 1:
		candidates_size = candidates_size * len(ids)
	if len(candidates_size) != len(ids):
		raise Exception("the number of size should match the number of id ")
	
	candidates_subclass_mode = subclass_mode.strip().split(",")
	if len(candidates_subclass_mode) == 1:
		candidates_subclass_mode = candidates_subclass_mode * len(ids)
	if len(candidates_subclass_mode) != len(ids):
		raise Exception("the number of mode size should match the number of id ")
	
	candidates_origin = origin
	
	leaves_id = []
	delete_pos = []
	tmp_prob = []
	tmp_size = []
	tmp_origin = []
	for i in range(len(ids)):
		if (candidates_subclass[i] == True) and (candidates_subclass_mode[i] == "1"):
			if len(get_leaves([ids[i]])[0]) != 0:#如果本来就是叶子节点，就不删除
				delete_pos.append(i)
			leaves_id.append(ids[i])
			tmp_prob.append(candidates_prob[i])
			tmp_size.append(candidates_size[i])
			tmp_origin.append(candidates_origin[i])
	leaves = get_leaves(leaves_id)#list, item list
	for i in range(len(leaves)):
		ids = ids + leaves[i]
		candidates_prob = candidates_prob + [tmp_prob[i]]*len(leaves[i])
		candidates_subclass = candidates_subclass + [False]*len(leaves[i])
		candidates_size = candidates_size + [tmp_size[i]]*len(leaves[i])
		candidates_origin = candidates_origin + [tmp_origin[i]]*len(leaves[i])

	removed_ids = []
	removed_prob = []
	removed_subclass = []
	removed_size = []
	removed_origin = []
	for i in range(len(ids)):
		if i not in delete_pos:
			removed_ids.append(ids[i])
			removed_prob.append(candidates_prob[i])
			removed_subclass.append(candidates_subclass[i])
			removed_size.append(candidates_size[i])
			removed_origin.append(candidates_origin[i])
	ids = removed_ids
	candidates_prob = removed_prob
	candidates_subclass = removed_subclass
	candidates_size = removed_size
	candidates_origin = removed_origin
	'''
	for pos in delete_pos:
		del ids[pos]
		del candidates_prob[pos]
		del candidates_subclass[pos]
		del candidates_size[pos]
	'''

	return ids,candidates_prob,candidates_subclass,candidates_size, candidates_origin

def parse_subtract(ids, ids_subclass):
	if type(ids) != list:
		raise Exception("ids should be a list")
	if type(ids_subclass) != str:
		raise Exception("ids_subclass should be a string")
	subclass_flags = ids_subclass.strip().split(",")
	if len(subclass_flags) == 1:
		subclass_flags = [subclass_flags[0]] * len(ids)
	if len(subclass_flags) != len(ids):
		raise Exception("the number of subclass flags should match the number of ids")
	ids_with_flag = []
	for i in range(len(ids)):
		if subclass_flags[i] == "1":
			ids_with_flag.append(ids[i])
	results = get_all_subclasses(ids_with_flag)
	final = []
	for result in results:
		final = final + result
	return final + ids

def parse_single_annotation_file(file_path):
	record = []
	with open(file_path) as f:
		lines = f.readlines()
		for line in lines:
			if line != "":
				parts = line.split(' ')
				probs = parts[-1].split(',')
				for prob in probs:
					pair = prob.split(':')
					record.append({"file_name":parts[0],"folder":parts[1], 'class_id':np.int32(pair[0]),'prob':np.float32(pair[1])})

		frame = pd.DataFrame(record)
		return frame
'''
def parse_annotation_file(file_paths):	
	num_samples = len(file_paths)
	num_cpu = mp.cpu_count()
	epoch = int(num_samples/num_cpu)
	final_result = []
	for i in range(epoch):
		print(i)
		results = []
		pool = mp.Pool()
		for j in range(num_cpu):
			result = pool.apply_async(_parse_single_annotation_file,args=(file_paths[i*num_cpu+j],))
			results.append(result)
		pool.close()
		pool.join()

		for result in results:
			final_result.append(result.get())
	
	result = []
	pool = mp.Pool()
	for i in range(epoch*num_cpu, num_samples):
		result = pool.apply_async(_parse_single_annotation_file,args=(file_paths[i],))
		results.append(result)
	pool.close()
	pool.join()

	for result in results:
		final_result.append(result.get())
	return final_result
'''
