counter = 10000
id_dict = dict()
with open("./unique2.txt") as f:
	lines = f.readlines()
	for line in lines:
		#for char in ['/','_','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0',' ','\n']:
			#line = line.replace(char,'')
			#line = line.strip()
		#id_dict.append(line)
		parts = line.split()
		if len(parts) == 0:
			continue
		if len(parts) != 3:
			print('warning!!!!!!!!!!!!!!!!!!!!!!!!')
		id_dict[parts[-2]] = parts[-1]
with open("./name_id.txt",'a') as f:
	counter = 10000
	for k,v in id_dict.items():
		print(k+":"+v)
		newline = k+":"+str(counter)+"\n"
		f.write(newline)
		counter += 1


