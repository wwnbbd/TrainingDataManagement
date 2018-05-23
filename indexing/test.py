children = []
with open("./relation.txt") as f:
	relations = f.readlines()
	for relation in relations:
		parts = relation.strip("\n").split(":")
		if parts[-2] == "0":
			children.append(parts[-1])
names = []
name_id = dict()
with open("./name_id.txt") as f:
	ids = f.readlines()
	for i in ids:
		name_id[i.strip("\n").split(":")[-1]] = i.split(":")[-2]

for i in children:
	names.append(name_id[i])

print(names)
