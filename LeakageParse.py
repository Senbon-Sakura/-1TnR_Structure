import numpy as np
import matplotlib.pyplot as plt
from sys import argv

arrSize = int(argv[1])

def Norm(x):
	Xmin = np.min(x)
	Xmax = np.max(x)
	X_norm = (x - Xmin) / (Xmax-Xmin)
	return X_norm

curArr=[]
with open('./current.log', 'r') as f:
	for line in f.readlines():
		tmp = line.strip().split(':')
		tmp2 = tmp[1].split(' ')
		curArr.append(abs(float(tmp2[1])))

curArr = np.array(curArr).reshape((arrSize, arrSize))
#curArr = Norm(curArr)
print(curArr)

plt.imshow(curArr, cmap='coolwarm')
plt.colorbar(shrink=.92)	
plt.xticks([])
plt.yticks([])
plt.savefig('figimage.png')
plt.show()
