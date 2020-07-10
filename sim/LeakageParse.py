import numpy as np
import matplotlib.pyplot as plt
from sys import argv
import time

arrSize = int(argv[1])

def Norm(x):
	Xmin = np.min(x)
	Xmax = np.max(x)
	print("Maximum: %3f" % Xmax)
	print("Minimum: %3f" % Xmin)
	X_norm = (x - Xmin) / (Xmax-Xmin)
	return X_norm

with open('weight.log', 'r') as fw:
	for line in fw.readlines():
		weightList = line.strip().split()

weightArr = np.array(weightList).reshape(int(argv[1]), int(argv[1]))


curArrAbs=[]
curArr=[]
with open('./current.log', 'r') as f:
	for line in f.readlines():
		tmp = line.strip().split(':')
		tmp2 = tmp[1].split(' ')
		curArrAbs.append(abs(float(tmp2[1])))
		curArr.append(float(tmp2[1]))

curArrAbs = np.array(curArrAbs).reshape((arrSize, arrSize))
curArr = np.array(curArr).reshape((arrSize, arrSize))
#curArrAbs = Norm(curArrAbs)
print(curArrAbs)

plt.imshow(np.transpose(curArrAbs), cmap='coolwarm')
plt.colorbar(shrink=.92)	
plt.xticks([])
plt.yticks([])
for i in range(arrSize):
	for j in range(arrSize):
		text = plt.text(i, j, "%.2f\n%s" % (curArr[i, j] * 1e6, weightArr[i,j]), ha="center", va="center", color="w")

now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())
plt.savefig('./result/Leakage_%s.png' % now)
plt.show()
