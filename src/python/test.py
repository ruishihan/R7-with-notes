class test:

	def __init__(self):
		self.a=1
		self.b=2
		self.c=3
		self.d=4
		for k in ['a','b','c','d']:
			print k
			print self.__dict__[k]
		print dir(self)
if __name__=="__main__":
	test()
