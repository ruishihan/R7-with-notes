#! /bin/bash
hostip=$1
echo "init ad9361"
curl -F adscripts=@'AD9361/FM.reg' http://${hostip}:8080/misc
echo ""
echo "set rx fir"
curl -F chead=@'AD9361/30K_75K.h' http://${hostip}:8080/fir
####这一句是什么意思？？？
echo ""
echo "set freq set agc"
curl http://${hostip}:8080/init?'rx&freq=97.4e6&gain=35'
echo ""
sleep 1
echo "start FM"
curl http://${hostip}:8080/FM?start
####从这一句的解析入手，查看其调用的函数。
echo ""
echo "finished"
