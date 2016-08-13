import AD9361_c
import axi2s_c
import aximem

class config:
	def __init__(self):
		self.AXI2S_IBASE = 0x1e000000
		self.AXI2S_ISIZE = 0xea6000
		self.AXI2S_OBASE = 0x1f000000
		self.AXI2S_OSIZE = 0xea6000
		self.rx    = {
				'freq':940.1e6
			, 'gain': [68,68]
			}
		self.aximem = aximem.aximem()
		self.udpSrv = None
		self.FM = None
		self.port = 10000
		self.scan = None
	
	def todict(self):
		r = {}
		for k in ['AXI2S_IBASE','AXI2S_ISIZE','AXI2S_OBASE','AXfI2S_OSIZE','rx','port']:
			r[k] = self.__dict__[k]
			##self.__dict__[] 是一个存放类属性的字典 
		return r
	
	def init(self):
		c = self.todict()
		##c is a dict that stores the property of class config.
		axi2s = axi2s_c.axi2s_c(c)
		##why there is 2 axi2s_c ????	the first axi2s_c is the name of file(module), the second is the name of class.
		## axi2s create a object that exploit a mem and create a dict that stores the values of parameters.
		ad = AD9361_c.AD9361_c()
		axi2s.init()
		##init() write the values of parameters to device.
		ad.webapi['rx']['set']['freq'](self.rx['freq'])
		ad.webapi['rx']['set']['gain'](self.rx['gain'][0],0)
		ad.webapi['rx']['set']['gain'](self.rx['gain'][0],1)
		self.aximem.init(c)
		self.aximem.reset("inp")
		ad.Check_FDD()
		return c
