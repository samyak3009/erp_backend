input_str = input()
first_list  = list(map(int,input_str.split(' ')))
second_list = []
output=  []
for f in first_list:
  second_list.append(bin(f)[:1:-1])
for s in second_list:
  output.append(int(s,2))
for o in output:
  print(str(o)+',')