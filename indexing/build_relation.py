lines = []
with open("./unique2.txt") as f:
	lines = f.readlines()

name_id = dict()
with open('./name_id.txt') as f:
	pairs = f.readlines()
	for pair in pairs:
		pair_parts = pair.strip('\n').split(":")
		name_id[pair_parts[-2]] = pair_parts[-1]
relation = []
for line in lines:
	print(line)
	parts = line.split()
	print(parts)
	if len(parts) >1:
		relation.append(parts[-1]+":"+name_id[parts[-2]])
print(relation)

with open("./relation.txt",'a') as f:
	for item in relation:
		f.write(item+"\n")
