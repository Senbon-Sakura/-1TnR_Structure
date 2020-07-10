# argv[1]=array_size, argv[2]=lineResistance; argv[3]=VarSwitch
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Unit import *
#from PySpice.Physics.SemiConductor import ShockleyDiode

import PySpice



PySpice.Spice.Simulation.CircuitSimulator.DEFAULT_SIMULATOR = 'ngspice-subprocess'
#libraries_path = "/home/victor/Downloads/hspiceLib"
#libraries_path = "/home/wzw/Download/ngspice/Spice64/PySpice/examples/libraries/transistor"
libraries_path = "/home/wzw/Download/ngspice/PySpice/examples/libraries/transistor"
spice_library = SpiceLibrary(libraries_path)


## circuit
circuit = Circuit(title='sparse_net')
circuit.include(spice_library['ptm65nm_nmos'])
circuit.include(spice_library['ptm65nm_pmos'])

# params
#sparseRate = 0.5
# 65nm nmos with Vg=1.2V, 2.5V will induce large Ig
VGATEON = 1.2@u_V
VGATEOFF = 0.0@u_V
VSEL = 1.2@u_V
VREAD = 0.2@u_V
arrSize=int(argv[1])
line_R = int(argv[2])@u_Ohm
level_R = [100@u_kOhm, 10@u_kOhm]
# generaged params
#weights1 = np.random.uniform(0, 1, (128, 128)) >= sparseRate
#weights1 = np.ones((arrSize, arrSize))
weights1 = (np.random.rand(8*8) > 0.5).reshape(8,8)

def rlevel(level):
    #return level_R[int(level)]
    return level_R[int(level)]*np.exp(-1*np.random.normal(0,0.5))



VWL = []
VBL = []
VSL = []
for i in range(arrSize):
	VWL.append('WL_w1_%03d' % (i))
for i in range(arrSize):
	VBL.append('BL_w1_%03d' % (i))
for i in range(arrSize):
	VSL.append('SL_w1_%03d' % (i))


circuit.VoltageSource(name='WL_SEL', plus='WL_SEL', minus=circuit.gnd, dc_value=VGATEON)
circuit.VoltageSource(name='BL_SEL', plus='BL_SEL', minus=circuit.gnd, dc_value=VREAD)



'''
# WL Voltage
for i in range(arrSize):
    circuit.VoltageSource(name=VWL[i], plus='WL_w1_%03d%03d' % (i, 0), minus=circuit.gnd, dc_value=VGATEOFF)

# BL Voltage
for i in range(arrSize):
    circuit.VoltageSource(name=VBL[i], plus='BL_w1_%03d%03d' % (0, i), minus=circuit.gnd, dc_value=0.0@u_V)

# SL Voltage
for i in range(arrSize):
    circuit.VoltageSource(name=VSL[i], plus='SL_w1_%03d%03d' % (i, 0), minus=circuit.gnd, dc_value=0.0@u_V)
'''



# WL Voltage
for i in range(arrSize):
	circuit.VoltageSource(name=VWL[i], plus='WL_w1_%03d' % i, minus=circuit.gnd, dc_value=0.0@u_V)
	circuit.Mosfet(name='TG_WL_%03d_n0' % (i), drain='WL_SEL', gate='WL_w1_%03d' % (i), source='WL_w1_%03d%03d' % (i, 0), bulk=circuit.gnd, model='ptm65nm_nmos', length=65@u_nm, width=160@u_nm)


# BL Voltage
for i in range(arrSize):
	circuit.VoltageSource(name=VBL[i], plus='BL_w1_%03d' % i, minus=circuit.gnd, dc_value=0.0@u_V)
	circuit.Mosfet(name='TG_BL_%03d_n0' % (i), drain='BL_SEL', gate='BL_w1_%03d' % (i), source='BL_w1_%03d%03d' % (0, i), bulk=circuit.gnd, model='ptm65nm_nmos', length=65@u_nm, width=160@u_nm)

# SL Voltage
for i in range(arrSize):
	#circuit.VoltageSource(name=VSL[i], plus='SL_w1_%03d' % i, minus=circuit.gnd, dc_value=0.0@u_V)
	circuit.Mosfet(name='TG_SL_%03d_n0' % (i), drain=circuit.gnd, gate='WL_w1_%03d' % (i), source='SL_w1_%03d%03d' % (i, 0), bulk=circuit.gnd, model='ptm65nm_nmos', length=65@u_nm, width=160@u_nm)



# w1 xbar
# pos w1 xbar
for i in range (arrSize):
	circuit.Resistor(name='SL_w1_%03d%03d' % (i, 0), plus='SL_w1_%03d%03dH' % (i, 0), minus='SL_w1_%03d%03dL' % (i, 0), resistance=line_R)
	circuit.Resistor(name='WL_w1_%03d%03d' % (i, 0), plus='WL_w1_%03d%03d' % (i, 0), minus='WL_w1_%03d%03dL' % (i, 0), resistance=line_R)
	circuit.Mosfet(name='Msel_w1_%03d%03d' % (i, 0), drain='SL_w1_%03d%03dL' % (i, 0), gate='WL_w1_%03d%03dL' % (i, 0), source='SL_w1_%03d%03d' % (i, 0), bulk=circuit.gnd, model='ptm65nm_nmos', length=65@u_nm, width=160@u_nm)
	for j in range (arrSize):
		# lines
		circuit.Resistor(name='BL_w1_%03d%03d' % (i, j), plus='BL_w1_%03d%03d' % (i, j), minus='BL_w1_%03d%03d' % (i+1, j), resistance=line_R)
		circuit.Resistor(name='RRAM_w1_%03d%03d' % (i, j), plus='BL_w1_%03d%03d' % (i+1, j), minus='SL_w1_%03d%03dH' % (i, 0), resistance=rlevel(weights1[i,j]))



resList = []
with open('./weight.log', 'w') as fw:
	#for i in range(int(argv[1])):
	#	for j in range(int(argv[1])):
	#		if weights1[i,j]:
	#			resList.append('10K')
	#		else:
	#			resList.append('100K')
	#fw.write(str(np.array(resList).reshape(8,8)))
	for i in range(int(argv[1])):
		for j in range(int(argv[1])):
			fw.write(str('%d\t' % weights1[i,j]))

#simulate
simulator = circuit.simulator(simulator='ngspice-subprocess')


#circuit['VWL_w1_000'].dc_value=VSEL
#circuit['VWL_w1_001'].dc_value=VSEL
#circuit['VWL_w1_002'].dc_value=VSEL
circuit['VWL_w1_003'].dc_value=VSEL
#circuit['VWL_w1_004'].dc_value=VSEL
circuit['VWL_w1_005'].dc_value=VSEL
#circuit['VWL_w1_006'].dc_value=VSEL
circuit['VWL_w1_007'].dc_value=VSEL

#circuit['VBL_w1_000'].dc_value=VSEL
#circuit['VBL_w1_001'].dc_value=VSEL
#circuit['VBL_w1_002'].dc_value=VSEL
circuit['VBL_w1_003'].dc_value=VSEL
#circuit['VBL_w1_004'].dc_value=VSEL
#circuit['VBL_w1_005'].dc_value=VSEL
#circuit['VBL_w1_006'].dc_value=VSEL
#circuit['VBL_w1_007'].dc_value=VSEL



# print sp file
sp_file = open('SparseNet.sp', 'w')
sp_file.write(str(circuit))
sp_file.close()
print("Netlist Saved in SparseNet.sp")

analysis = simulator.operating_point()

with open('./current.log', 'w') as fid:
	for i in range(arrSize):
		for j in range(arrSize):
			VH = analysis['BL_w1_%03d%03d' % (i+1, j)][0]
			VL = analysis['SL_w1_%03d%03dH' % (i, 0)][0]
			Iread = (VH - VL) / (circuit['RRRAM_w1_%03d%03d' % (i, j)].resistance)
			fid.write("cell(%03d, %03d)'s weight = %d" % (i, j, weights1[i,j]) + "\tread current is: " + str(Iread) + "\n")
			

print("****************************************************************************")
print("SIMULATION FINISHED!!!")
print("****************************************************************************")
