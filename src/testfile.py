a=[]
for b in range(510):
    a.append(str(b))
    
    
print(a)

aa = []
while True:
    numItems=100
    if len(a)>=numItems:
        aa.append(a[0:numItems])
        a = a[numItems:]
        continue
    aa.append(a)
    break

for aaa in aa:
    print(aaa)