#!/bin/sh

## Daemonizer for the CBAS.
## Expected to work under both Debian-based systems and RedHat.
## Version: 0.1
## Author: Umar Toseef
## Organization: EICT

# chkconfig: 2345 80 20
# description: startup script for CBAS

### BEGIN INIT INFO
# Provides: cbas
# Required-Start: $local_fs $remote_fs $network $syslog
# Required-Stop: $local_fs $remote_fs $network $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: startup script for CBAS
### END INIT INFO
#

# Name for the service, used in logging
CBAS_NAME=cbas

# Title for the service, used in service commands
CBAS_TITLE="CBAS"

# Name of the user to be used to execute the service
CBAS_USER=root

# In which directory is the shell script that this service will execute
CBAS_HOME=$( cd "$( dirname "$0" )" && pwd )

# Where to write the process identifier - this is used to track if the service is already running 
# Note: the script noted in the COMMAND must actually write this file 
PID_FILE=/var/run/$CBAS_NAME.pid

# File to handle instances of the program
LOCK_FILE=/var/lock/$CBAS_NAME

# Where to write the spreader log file
LOG_FOLDER=log
LOG_FILE=cbas.log

# How can the script be identified if it appears in a 'ps' command via grep?
# Examples to use are 'java', 'python' etc.
PROCESS_TYPE=/usr/bin/python

# Construct the command(s) to invoke the proper script(s)
EXEC="$PROCESS_TYPE $CBAS_HOME/src/main.py"
# Return variables
RET_SUCCESS=0
RET_FAILURE=1

export CBAS_HOME

if [ -e /etc/redhat-release ]; then
	. /etc/init.d/functions
fi

# Is the service already running? If so, capture the process id 
if [ -f $PID_FILE ]; then
	PID=`cat $PID_FILE`
else
	PID=""
fi

create_log() {
	# Create symlink to log within cbas if not previously there
	if [ ! -L /var/log/$CBAS_NAME ]; then
		ln -sf $LOG_FOLDER/ /var/log/$CBAS_NAME
	fi
}

do_start() {
	if [ "$PID" != "" ]; then
		# Check to see if the /proc dir for this process exists
		if [ -f "/proc/$PID" ]; then
			# Check to make sure this is likely the running service
			ps aux | grep $PID | grep $PROCESS_TYPE >> /dev/null
			# If process of the right type, then is daemon and exit 
			if [ "$?" = "0" ]; then
				return $RET_SUCCESS
			else
				# Otherwise remove the subsys lock file and start daemon 
				echo "$CBAS_TITLE is already running." 
				rm -f $LOCK_FILE
			fi
		else
			# The process running as pid $PID is not a process
			# of the right type; remove lock file
			rm -f $LOCK_FILE
		fi
	fi

#	create_log

	# RedHat-based distros do not help too much with pidfiles creation, so it
	# is done manually by retrieving and killing the last created process (tail).
	if [ -e /etc/redhat-release ]; then
#		daemon $EXEC --pidfile $PID_FILE --user $CBAS_USER start > \
#		/dev/null 2> /dev/null &
#		PID=`ps xaww | grep "$PROCESS_TYPE" | grep "$EXEC" | grep "pidfile $PID_FILE" | tail -1 | awk '{print $1}'`

		# Daemon opens N processes for Resource Orchestrator (shell, bash, python).
		# Using something more adequate, then retrieving its PID
		$EXEC > /dev/null 2> /dev/null &
		PID=`ps xaww | grep "$PROCESS_TYPE" | grep "$EXEC" | grep -v "grep" | tail -1 | awk '{print $1}'`
		echo $PID > $PID_FILE
	else
		#start-stop-daemon --start --chuid $CBAS_USER --user $CBAS_USER \
		#--name $CBAS_USER -b --make-pidfile --pidfile $PID_FILE --exec $EXEC
		start-stop-daemon --start -b --make-pidfile --pidfile $PID_FILE --exec $EXEC
	fi

	touch $LOCK_FILE
	return $RET_SUCCESS
}

do_stop() {
#	daemon $EXEC --pidfile $PID_FILE --user $CBAS_USER stop > /dev/null 2> /dev/null &

	# Always remove control files on stop
	rm -f $LOCK_FILE
	rm -f $PID_FILE
	if [ "$PID" != "" ]; then
        # Debian 7
        pkill -TERM -P $PID
        #PIDS=`ps xaww | grep "$PROCESS_TYPE" | grep "$EXEC" | grep -v "grep" | cut -d " " -f1`
        echo $PIDS
        # XXX: Several processes are being initialised! Take care of them.
        #for PE in "${PIDS##*:}"; do
        #    kill -QUIT $PE
        #done
		for i in {1..30}
		do
			if [ -n "`ps aux | grep $PROCESS_TYPE | grep $EXEC`" ]; then
				sleep 1 # Still running, wait a second
				echo -n . 
			else
				# Already stopped 
				return $RET_SUCCESS
			fi
		done
	else
		echo "$CBAS_TITLE is already NOT running."
		return $RET_SUCCESS
	fi
	# Should never reach this...?
	pkill -TERM -P $PID | return $RET_FAILURE # Instant death. If THAT fails, return error
	return $RET_SUCCESS
}

do_restart() {
	do_stop
	sleep 1
	do_start
}

do_check_status() {
	if [ "$PID" != "" ]; then
		STATUS="running (pid $PID)"
	else
		STATUS="NOT running"
	fi
	echo "$CBAS_TITLE is $STATUS."
}

case "$1" in
	start)
		action="Starting $CBAS_TITLE.";
		echo $action;
		do_start;
		exit $?
	;;
	stop)
		action="Stopping $CBAS_TITLE.";
		echo $action;
		do_stop;
		exit $?
	;;
	restart|force-reload)
		action="Restarting $CBAS_TITLE.";
		echo $action;
		do_restart;
		exit $?
	;;
	status)
		do_check_status;
		exit $?
	;;
	*)
		echo "Usage: service $CBAS_NAME {start|stop|restart|status}";
		exit $RET_SUCCESS
	;;
esac
