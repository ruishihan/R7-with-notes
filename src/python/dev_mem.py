#! /usr/bin/python
# -*-coding:utf-8-*-
import mmap
from ctypes import *
#本函数只使用了python提供的库mmap，不直接涉及python调用c的操作，但是mmap可能是调用c来实现的，所以需要包含ctypes库。
#本函数完成内存映射，并且提供内存读写接口。

class dev_mem:
    DEVNAME = '/dev/mem'
    def __init__(self,BASE,LEN):
        self.len = LEN
        self.base = BASE
        self.fd = open(dev_mem.DEVNAME,'r+b',buffering=0)
        self.mmap = mmap.mmap(self.fd.fileno(),LEN, offset=BASE) 

    def ioread(self,addr):
        buf = self.memread(addr,1)
        return buf[0]

    def iowrite(self,addr,d):
        buf = (c_uint*1)()
        buf[0] = d
        self.memwrite(addr,buf)
    
    def memread(self,addr,len):
        buf = (c_uint*len)()
        self.mmap.seek(addr)
##seek()----set the file's current position.
        memmove(buf,self.mmap.read(4*len),4*len)
        return buf
    
    def bufread(self,addr,len):
        self.mmap.seek(addr)
        buf=self.mmap.read(len)
        return buf
    
    def SetOffset(self,offset):
        self.mmap.seek(offset)

    def memwrite(self,addr,buf):
        self.mmap.seek(addr)
        self.mmap.write(buf)

    def deinit(self):
        self.mmap.close()

def main():
    uut = dev_mem(0xfffc0000,0x10000)
    print uut.mmap[:5]
##uut.mmap[:5] ????
if __name__ == '__main__':
    main()





