# R7OCM工程使用说明
-------------------------------------------------------------
## 本工程目前主要已实现以下功能：
	 一、GSM信号解析(含频谱图、IQ路数据图)
	 二、FM调频收音机
	 三、扫频功能(覆盖GSM和WIFI频段)
	 四、GSM信令解析功能(还未完成测试)
	     
        其中GSM信号解析功能测试过程中目前存在一个网页画出的图形时会出现散点无法正常显示图形的情形：
		   目前分析可能是以下原因:
  		 * 浏览器的配置问题；
  		 * 板子本身的配置问题(测试过程中发现有的板子会出现这一问题)

-------------------------------------------------------------
## 测试环境与工具：
	> Vivado(2014.4之后的版本)软件
	> git工具(Linux版或Windows版均可)
	> gtkterm(Linux下) 、Xshell5(Windows下) 或 其它串口工具
	> Linux环境：纯Linux系统(如Ubuntu系统)、安装Linux系统的虚拟机或虚拟的Linux环境(如Cygwin软件，仅限于前三个功能)

-------------------------------------------------------------
## 硬件环境：
	> Q7板子及电源
	> SD卡、网线、USB数据线、合适的天线
	> 具有Linux环境的PC机

-------------------------------------------------------------

## 本文分四部分介绍R7OCM工程的使用方法：
	1. 对SD卡进行分区并制作成系统盘
	2. PC端的工作
	3. 启动ARM，并向ARM上传文件
	4. 在PC端接收并查看数据 及 通过curl对ARM各参数进行配置

### 本说明默认具备以下环境：
	1. 文件夹root.full.function (以后将会上传到指定的网址)包含以下文件：
 	  - BOOT.bin 、core-image-my-sdk-r7-zynq7-20150620151425.rootfs.cpio.gz
 	  - devicetree.dtb、uEnv.txt、uImage、uramdisk.image.gz
	2. Ubuntu 14.04 LTS 系统，并且装有git、ssh、curl、Vivado_2014.4、gtkterm

-------------------------------------------------------------

## SD卡分区及系统盘制作
> 进入管理员模式(或直接在命令前加sudo)：

        sudo su
> 通过fdisk -l命令找出SD可对应的设备文件(或用df -h 命令查看SD卡对应的设备文件)：

        fdsik -l
> 对SD对应的设备文件进行操作，这里假设设备文件是 /dev/sdb

- 假设SD卡未进行分区，则先对SD卡进行分区(分区前须先将SD卡umount，详见fdisk命令的使用方法)

        fdisk /dev/sdb
- 然后根据fdisk的命令提示进行操作，用n选项新建分区，第一个分区分配8G空间，剩余空间分给第二个分区(分配空间可自由分配，但不应小于***)
- 用t选项改变分区格式，分区一设置为W95 FAT32格式（Hex code 为 c），分区二保持linux格式不变
- 设置好两个分区的格式后，用w选项将分区表写入SD卡，并退出fdisk命令
- 格式化两个分区，分别用下面的命令将两个分区格式化成ext4和fat32格式：
	> sudo mkfs.vfat /dev/sdb1
	
	> sudo mkfs.ext4 /dev/sdb2
	
*  注： 如果SD卡已有分区，但分区大小不符合要求，则可以通过 d 命令删除分区。注意分区时须把第一个分区设置成FAT32格式，否则可能会出现问题。
       
        

> 将SD卡挂载后进入分区二（linux分区），执行下述命令：

        zcat /.../root.full.function/core-image-my-sdk-r7-zynq7-20150620151425.rootfs.cpio.gz |sudo cpio -i

> 将root.full.function 文件夹中的 BOOT.bin  devicetree.dtb  uEnv.txt  uImage uramdisk.image.gz 五个文件拷贝到分区一(FAT32分区)中

> 在卸载SD卡之前，使用 `sync` 确保数据已全部写入SD卡；然后正确卸载SD卡

* 至此，系统盘制作完成。ARM将先读取分区一中的启动文件，并启动程序，在启动后挂载分区二，并改为运行分区二中的程序。



## PC端的工作

> 将github中的R7-OCM库复制到本地

        git clone https://github.com/RP7/R7-OCM.git

> 在R7-OCM目录下运行 `make install`,该命令将给upload.sh 和 curlinit.sh 文件赋予执行权限；把 post-commit 文件copy到.git/hooks目录下，并赋予执行权限。

> 在R7-OCM目录下运行 `.git/hooks/post-commit`，该命令将生成 src/rtl/gitversion.v，文件中记录了版本信息，该文件将在Vivado运行R7OCM.tcl脚本时被用到。

* 注：此处可以直接设置scripts文件夹下的执行权限，再直接运行./scripts/post-commit 命令实现

> 用 Vivado 生成FPGA的配置文件R7OCM_top.bit

>> 打开Vivado,在Tcl Console 窗口中输入命令，先切换到R7-OCM目录下，执行
>>>
            source ./scripts/R7OCM.tcl

>> 等待工程生成完毕后，运行`Generate bitstream`，生成R7OCM_top.bit文件。（选项Vivado左侧的`Flow Navigator`栏中）


## 启动ARM，并向ARM上传文件

> 首先将ARM的USB端口和网口分别同PC的USB端口和网口连接起来

> 通过gtkterm 打开两个终端，两个终端分别对应USB口的两条线路

      sudo -S gtkterm -p /dev/ttyUSB1 -s 115200 
      sudo -S gtkterm -p /dev/ttyUSB0 -s 115200
> 在ttyUSB1端口中输入(显示为 `system:>` )

        从SD卡启动系统：BootFromSD / 从NAND FLASH启动系统：BootFromNAND
        注：此处须设置从SD卡启动

> 另一个端口会显示ARM正在启动linux系统，等待启动完成后，输入用户名 root(此系统未设置密码，直接使用用户名登录即可)，进入系统

* 如果系统启动失败，可能是因为SD未正确卸载导致的，可以先尝试重新输入`BootFromSD`，重启系统；如果还不行，将SD卡重新挂载在PC上，然后正确卸载即可。

> 对PC和ARM的IP进行配置，注意一定要让两者在一个网段
  >> 如现设PC和Q7板子的IP分别为： 192.168.1.12 192.168.1.11

> 在 ***PC*** 的命令窗口中，切换到R7-OCM目录下，运行

            sh ./scripts/upload.sh 192.168.1.11 1

* 注意命令后须设两个参数，第一个为Q7板子的IP地址，第二个为vivado工程下的`R7OCM.runs/impl_1`目录`impl_1`中的数字，一般情况下默认为数字 ` 1 `
* upload.sh 脚本中主要完成文件压缩（PC端）、文件上传、文件解压（ARM端），FPGA配置（R7OCM_top.bit），并且在ARM端运行axi2s_c.py 和 q7web.py两个python程序

## 在PC端接收并查看数据 及 通过curl对ARM各参数进行配置(详见工程目录中的RESTful.md文件)


### PC端接收并查看数据 (须将天线接在Rx1接口上)

-------------------------------------------------------------
> 功能一：GSM信号解析(含频谱图、IQ路数据图)
>> 进入PC端命令终端，切换到R7-OCM目录下，运行
>>>
	sh ./scripts/curlinit.sh 192.168.1.11

>> 打开浏览器，输入192.168.1.11:8080，即可打开web网页查看图形，在另一个浏览器窗口中输入以下命令可以设置频率和增益(其它功能中的设置方法一样):

  * 设置频率: 192.168.1.11:8080/rx?freq(查看频率)、192.168.1.11:8080/rx?freq=942.4e6(设置频率为942.4MHz)
  * 设置增益: 192.168.1.11:8080/rx?gain(查看增益)、192.168.1.11:8080/rx?gain=60(设置增益为60,最大为76)

-------------------------------------------------------------
> 功能二：FM调频收音机
>> 进入PC端命令终端，切换到R7-OCM目录下，运行
>>>
        sh ./scripts/fm.sh 192.168.1.11

>> 打开浏览器，输入192.168.1.11:8080，可以在web网页看到功能一中的图形，频率和增益的设置方法同上，在另一个浏览器窗口中输入:http://192.168.1.11:8080/static/fm.html便可以听到声音(PC需有音响或耳机)

--------------------------------------------------------------
> 功能三: 扫频功能(覆盖GSM和WIFI频段)
>> 进入PC端命令终端，切换到R7-OCM目录下，分别在两个终端窗口上运行以下命令：
>>>
        sh ./scripts/curlinit.sh 192.168.1.11
>>>
        sh ./scripts/scan.sh 192.168.1.11

>> 打开浏览器，输入http://192.168.1.11:8080/static/scan.html，便可以打开频谱页面，可以通过页面上的三个bar分三阶设置扫频范围，同时也可以通过页面上的按钮查看数据和保存频谱图。
   

----------------------------------------------------------------
> 功能四:GSM信令解析功能(还未完成测试) 
>> 本功能的测试配置方面比较复杂，暂时还没有实现测试，须在纯Linux环境下测试并需使用wireshark工具进行测试

>> 在github上下载完R7-OCM工程后运行以下命令，下载USRT源码
>>>
	git submodule update --init
   
>> 下载完后需进入src/host/cpp/USRT目录下打个补丁，命令为：
>>>
	patch < ../USRT.patch    

>> 进入R7-OCM工程目录，执行Makefile文件,具体命令如下：
>>> 
	1. make usrtlib
>>>  
	2. make hostlib
>>>  
	3. make host
>>>
	4. make /tmp/libcgsm.so

  
>> 然后再依次运行以下命令：
>>> 
	1. work/initQ7mem
>>> 
	2. work/Q7UDP  + IP(板子IP) + port(端口号默认为：10000)
>>>
	3. work/rxclock
  
  
>> 上面的运行成功后进入src/host/python目录下运行以下python程序：
>>>
	1. python GSMRoughSync.py (同步成功后再操作下一步骤)
>>>  
	2. python SyncTask.py
   
   
* 注：以上是大致的操作流程，可能还存在些问题，记得好像还需要设置一个系统的东西，
   我也忘了怎么弄了，有空请教教一下赵老师吧，我当时也并没有实现这一功能的测试。


### 通过curl对ARM进行配置
* 通过curl控制ARM的方法详见R7-OCM/RESTful.md

-----------------------------------------------------------------
## 大规模配置ad9361的寄存器（ad9361寄存器配置文件的生成和使用）
> ad9361配置文件的使用
>> 切换到ARM中的`/tmp/R7OCM/src/python/`目录下，运行 `python adscripts.py`，该python程序将会根据 `/tmp/R7OCM/AD9361/ad9361_config.reg`配置文件中的参数配置AD9361。

> ad9361配置文件的生成

## vivado
