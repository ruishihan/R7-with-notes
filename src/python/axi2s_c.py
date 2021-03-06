import dev_mem
import reg_define as reg
from const import *
import time
import sys

## create a memfile and set the AXI2S_EN AXI2S_I(O)SIZE(BASE) and so on. 
class axi2s_c:
	def __init__(self,d=None):
		self.dev = dev_mem.dev_mem(FPGA_BASE,FPGA_SIZE)
		self.api = {
			  'ver':self.apiversion
			, 'rreg':self.apiread
			, 'wreg':self.apiwrite
		}
		self.status(d)
		self.cnt = {}

	def apiversion(self,argv):
		ver = self.version()
		return {'ret':'ok','data':ver}

	def apiread(self,argv):
		if 'reg' in argv:
			if argv.reg in reg.addr:
				return {'ret':'ok','data':hex(self.dev.ioread(reg.addr[argv.reg]))}
			else:
				return {'ret':'err','res':'reg not exit'}
		else:
			return {'ret':'err','res':'reg not given'}

	def apiwrite(self,argv):
		if 'reg' in argv and 'value' in argv:
##what's the type of argv??dict?? what's the meaning of this sentence??
			v = int(argv.value,16)
			if argv.reg in reg.addr:
				self.dev.iowrite(reg.addr[argv.reg],v)
				return {'ret':'ok'}
			else:
				return {'ret':'err','res':'reg not exit'}
		else:
			return {'ret':'err','res':'reg or value not given'}

	def version(self):
##version reture the version string contain VER_MAJOR +VER_MINOR0/1/2/3/4
		vreg = reg.addr['VER_MAJOR']
		major = self.dev.ioread(vreg)
		minor = []
		vreg = reg.addr['VER_MINOR0']
		for i in range(5):
			minor.append(self.dev.ioread(vreg))
			vreg += 4
		i = 4
		minstr = ""
		while i>=0:
			minstr +='%08x'%(minor[i])
			i -= 1
		ver = 'VER: %08x-%s'%(major,minstr)
		return ver
		
	def check(self):
		time.sleep(1)
		self.read('AXI2S_IACNT')
		self.read('AXI2S_IBCNT')
		self.read('AXI2S_OACNT')
		self.read('AXI2S_OBCNT')
		self.read('AXI_RRESP')
		self.read('AXI_WRESP')
		self.read('AXI_STATUS')
		self.read('AXI_RADDR')
		self.read('AXI_WADDR')
		print self.version()

	def init(self):
####init所做的工作是对一些使能寄存器进行设置，将四个需要提供值的寄存器根据给定的值进行设置。
		self.read('AXI2S_STATE')
		self.write('AXI2S_EN',0)
		for r in self.base:
			self.write(r,self.base[r])
		self.write('AXI2S_EN',4)
		self.write('AXI2S_EN',0)
		self.write('AXI2S_EN',IEN|OEN)
		self.read('AXI2S_STATE')
		
	def initDRAM(self):
		self.read('AXI2S_STATE')
		self.write('AXI2S_IBASE',0x1e000000)
		self.write('AXI2S_ISIZE',0x100000)
		self.write('AXI2S_OBASE',0x1f000000)
		self.write('AXI2S_OSIZE',0x100000)
		self.write('AXI2S_EN',IEN|OEN)
		self.read('AXI2S_STATE')

	def status(self,d):
####status根据传入的字典d 中的值来更新自身的base。

		self.base = {'AXI2S_IBASE':0x1ffc0000, 'AXI2S_ISIZE':0x10000, 'AXI2S_OBASE':0xfffd0000, 'AXI2S_OSIZE':0x10000}
		if d!=None:
			for r in self.base:
				if r in d:
					self.base[r] = d[r] 
		
	
	def getCNT(self):
####从下一层读取AXI2S_IACNT	AXI2S_IBCNT	AXI2S_OACNT	AXI2S_OBCNT

		regcnt  = ['AXI2S_IACNT', 'AXI2S_IBCNT', 'AXI2S_OACNT', 'AXI2S_OBCNT']
		for r in regcnt:
			self.cnt[r] =  self.dev.ioread(reg.addr[r])

	def IinBuf(self,f,s):
		dis = (self.cnt['AXI2S_IBCNT']-f)*self.base['AXI2S_ISIZE']+(self.cnt['AXI2S_IACNT']-s)	
		if dis<0:
			return 1  #early
		if dis>self.base['AXI2S_ISIZE']-self.base['AXI2S_ISIZE']/64:
			return -1 #too late
		return 0

	def OinBuf(self,f,s):
		dis = (self.cnt['AXI2S_OBCNT']-f)*self.base['AXI2S_OSIZE']+(self.cnt['AXI2S_OACNT']-s)	
		if dis>0: 
			return -1 #late
		if dis<-self.base['AXI2S_OSIZE']+self.base['AXI2S_OSIZE']/64:
			return 1  #too early
		return 0
		
	def read(self,regname):
		r = self.dev.ioread(reg.addr[regname])
		print 'R:',regname, hex(r)
		return r
	
	def write(self,regname,data):
		self.dev.iowrite(reg.addr[regname],data)
		print 'W:',regname, hex(data)
	def deinit(self):
		self.dev.deinit()
		
def main():
	uut = axi2s_c()
	uut.write('AXI2S_EN',0)
##what if argv[1] is empty???? execute 'else'???
	if sys.argv[1]=='DRAM':
		uut.initDRAM()
	else:
		uut.init()
	uut.check()

if __name__ == '__main__':
	main()
