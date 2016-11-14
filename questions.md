1. `FMAPI`中,由客户端(PC)的浏览器每隔2秒发送一次内容为`/FM?data`的请求,来获取FM解调后的数据

2. FM的解调程序,原始输入数据是每秒960K 个符号(每个符号有IQ两路,共占4个字节),产生的数据是24K个符号(24*4KB).
   但是在FPGA的verilog代码中好像没有下采样的模块,接收到的数据下采样到960K是在AD9361中完成的吗`??????`
3. static文件夹下是网页、图片等静态文件，在`web.py`程序中，只看到了对`static/index.html`文件的调用，没看到对其他网页的调用，请问其他网页的调用是怎么实现的`????`

4. `udp`  模块使用32M的DRAM存储
   `FMAPI`模块使用32M的DRAM存储
   `rxbuf`模块使用256K的OCM
   `data` 模块使用32M的DRAM存储

5. `_g=config.config()`无参数调用,使用缺省的值,这样`_g`中的`AXI2S_IBASE/AXI2S_ISIZE/AXI2S_OBASE/AXI2S_OSIZE`的值是大小32M存储器的,而不是256K 大小的OCM的,那如果想映射OCM作为存储区的话,就不能使用`_g`吗`????`

6. `udp`模块中,底层调用`aximem.c`执行udp的数据收发任务.在`aximem.c`中的`axi_inp_task()`函数中,调用`loadtime()`函数来加载time值,`time=bcnt*size+acnt`,此处的size为作为参数传入的结构体的其中一个变量,应为0xea6000(约为14.6M).但在FPGA的实现中,AXI2S_ISIZE只取了din[23:6],即只取设置值0xea6000的高18位,这才有address=AXI2S_IBCNT*AXI2S_ISIZE+AXI2S_IACNT.而在C程序中,bcnt乘的是未右移的0xea6000 `??????`

7. udp模块中,底层调用的`aximem.c`程序`axi_inp_task()`和`axi_out_task()`中,对`data out of date `的判断是什么原理`???`

8. 在rxbuf模块中,使用的是256K的OCM作为存储器,但是在判断数据是否early 和 too late 时,所使用的`self.base[AXI2S_ISIZE]`是由`axi2s_c.axi2s_c(_g.todict())`设定的,即`self.base[AXI2S_ISIZE]` 应为_g中的缺省值0xea6000,而这应该是使用32M的DRAM存储时使用的,是在哪个地方对 base[AXI2S_ISIZE]的值做了更改吗`????`

	def IinBuf(self,f,s):
	    dis = (self.cnt['AXI2S_IBCNT']-f)*self.base['AXI2S_ISIZE']+(self.cnt['AXI2S_IACNT']-s)	
	    if dis<0:
		return 1  #early
	    if dis>self.base['AXI2S_ISIZE']-self.base['AXI2S_ISIZE']/64:
		return -1 #too late
	    return 0
