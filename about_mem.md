#存储地址分配
存储空间共分为四个部分：OCM、DRAM、FPGA寄存器、SPI寄存器。
在ARM中，存储空间都是通过设备文件`/dev/mem`访问，下面分别介绍：
##寄存器地址空间
FPGA寄存器和SPI寄存器的地址分配为：
		#define FPGA_BASE 0x40000000
		#define FPGA_SIZE 0x40000
		#define AD9361_SPI_BASE  0xE0007000
		#define AD9361_SPI_SIZE  0x1000

FPGA寄存器主要用于AD9361、FPGA接收/发送数据、缓存区的基地址/大小 等控制参数设置和FPGA当前读写位置的获取，其起始地址为0x40000000，大小为 0x40000；各FPGA寄存器的具体访问地址(相对于基地址的偏移地址)见`src/rtl/reg_define.v`

SPI寄存器主要用于SPI的控制参数设置、写SPI数据发送buffer、读SPI数据接收buffer，其起始地址为0xE0007000，大小为0x1000；各SPI寄存器的具体访问地址(相对于基地址的偏移地址)见`src/c/spi.h`。SPI寄存器是ARM内部的寄存器，不需要做后续处理。

通过改变FPGA寄存器`AXI_ISIZE/AXI_IBASE/AXI_OSIZE/AXI_OBASE`的值，可以实现OCM缓冲区和DRAM缓冲区的切换。

##DRAM缓冲区
通过设置FPGA寄存器的值如下，可以使用DRAM寄存器：
		#define AXI2S_IBASE 0x1e000000
		#define AXI2S_ISIZE 0xea6000
		#define AXI2S_OBASE 0x1f000000
		#define AXI2S_OSIZE 0xea6000
其中，AXI2S_ISIZE和AXI2S_OSIZE分别代表input缓冲区(FPGA写，ARM读)和output缓冲区(ARM写，FPGA读)的大小，可以根据需要更改，但是最大不应超过16MB，且应为64 Bytes 的整数倍。

##OCM缓冲区

通过设置FPGA寄存器的值如下，可以使用OCM缓冲区：
		#define AXI2S_IBASE 0x1ffc0000
		#define AXI2S_ISIZE 0x10000
		#define AXI2S_OBASE 0xfffd0000
		#define AXI2S_OSIZE 0x10000

#FPGA与ARM关于地址空间的约定
##缓冲区地址约定
如上所述，ARM端通过向FPGA寄存器`AXI2S_IBASE/AXI2S_ISIZE/AXI2S_OBASE/AXI2S_OSIZE`写入地址和大小，来控制FPGA对缓冲区的使用。

##FPGA当前读写位置
ARM端可以通过读取`AXI2S_IACNT/AXI2S_IBCNT`来获取FPGA当前的写位置，读取`AXI2S_OACNT/AXI2S_OBCNT`来获取FPGA当前的读位置。下面将介绍FPGA改写这四个寄存器的规则：
以`AXI2S_IACNT/AXI2S_IBCNT`为例。

###AXI2S_IACNT
AXI2S_IACNT是一个24位的寄存器，但是后6位全为0，因为DRAM一次搬移64 Bytes的数据，因此不必关注后6位的变化。
AXI2S_IACNT从0增长到 AXI2S_ISIZE设定的缓冲区的大小，然后归零，以此往复。

###AXI2S_IBCNT
每当 AXI2S_IACNT归零，AXI2S_IBCNT 的值增加1。
通过 AXI2S_IBCNT，可以在逻辑上构建一个一直增长的时间轴(逻辑地址可以一直增长)。
