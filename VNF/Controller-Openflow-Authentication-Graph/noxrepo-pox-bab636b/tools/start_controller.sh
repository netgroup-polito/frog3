#! /bin/sh
# /etc/init.d/start_my_controller

case "$1" in
	start)
		echo "starting my_controller"
		#echo "starting controller" >> /home/frog/log.txt
		cd /home/frog/MyOpenFlowController/noxrepo-pox-bab636b/
		sudo ./pox.py IP_forger &>log.txt
		echo $! >conf.txt
		;;
	stop)
		echo "stopping my_controller"
		cd /home/frog/MyOpenFlowController/noxrepo-pox-bab636b/
		pid= $(head -1 conf.txt)
		echo $pid
		sudo kill $pid
		;;
	*)
		echo "Usage: /etc/init.d/start_my_controller {start|stop}"
		exit 1
		;;
esac

exit 0 
