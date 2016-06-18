import numpy as np
from ctypes import *
import time

import GSM
from sptools import findFreq
from GSMSync import GSMSync

import matplotlib.pyplot as plt

class GSMTimingSync(GSMSync):
	def __init__(self,f,url='http://192.168.1.110:8080/'):
		GSMSync.__init__(self,f,url)
		self.sb = GSM.SB()
		self.osr = self.fc/GSM.symbolrate


	def once( self ):
		blk = self.fl/16

		rfd,start = self.getRfData(self.fl-blk,blk*3)
		nprfd = self.short2Complex(rfd)
		f = np.abs(self.sb.channelEst(nprfd,self.osr))
		for i in range(4):
		 	start = self.fl*10*i
		 	rfd,start = self.getRfData(start+self.fl-blk,blk*3)
		 	nprfd = self.short2Complex(rfd)
		 	f += np.abs(self.sb.channelEst(nprfd,self.osr))
		inx = int(f.argmax()-blk-42*self.osr)
		return inx

	def sync(self):
		self.waitClockStable()
		
		ff = self.once()
		fs = self.getFrameStart()
		self.setFrameStart(fs+ff/2)

		return ff

def main():
	fs = GSMTimingSync(1.92e6)
	f0 = fs.sync()
	f1 = 0.
	while abs(f1-f0)>5:
		f1 = f0
		f0 = fs.sync()
		print "Timing sync:",f0
		time.sleep(1)
	return fs

if __name__ == '__main__':
	fs = main()

