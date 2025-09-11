#xt2640_data_logger.py
#Use: Run this script on a raspberry pi connected via USB-RS232 to Xitron xt2640 power analyzer
#extends the capabilities of the built in logging system

#imports
import serial
import time

#user variables
#PA_PORTS=['/dev/ttyUSB0','/dev/ttyUSB1']
PA_PORTS=['COM8']


#function for setting up serial comms
def serial_init(PORTS):
    serial_objects=[]
    for pa_port in PORTS:
        serial_object=serial.Serial(port=pa_port, baudrate=115200,timeout=3,dsrdtr=True)
        serial_objects.append(serial_object)
    return serial_objects

#function for getting pa data via serial comms
def log_pa_response(pa,measurement_number,query_string,log_file):
    #get measurement date
    pa.write("DATE?\n".encode("ascii"))
    date_string=pa.readline().decode().removesuffix('\r\n')

    #get measurement time
    pa.write("TIME?\n".encode("ascii"))
    time_string=pa.readline().decode().removesuffix('\r\n')

    #get measurement values
    pa.write(query_string.encode("ascii"))
    measurement_string=pa.readline().decode().removesuffix('\r\n')

    #build log string
    log_string=str(measurement_number)+','+date_string+','+time_string+','+measurement_string
    f=open(log_file,"a")
    f.write(log_string)
    f.close()

#get inputs from user
duration_int=int(input("Enter test duration in seconds: "))
delay_int=int(input("Enter delay period before test start in seconds: "))
log_file_name=input("Enter name of log file: ")

#build list of power analyzers as pyserial objects
power_analyzers=serial_init(PA_PORTS)

#get query string from file
f=open('query_string.txt','r')
query_string=f.readline()
f.close()
print(f'Found query string {query_string}')

#set up log file
f=open(log_file_name,'w')
f.write("SAMPLE NUM,DATE,TIME,")
f.write(query_string.removeprefix('READ?,'))
f.close()

#wait for delay time
for x in range(delay_int):
    print(str(delay_int-x)+" seconds till test start")
    time.sleep(1)

#main logging loop
for x in range(duration_int):

    #log time before getting data and writing file
    start_time=time.time()

    #write data to log
    for analyzer_num in range(len(power_analyzers)):
        log_pa_response(power_analyzers[analyzer_num],x+1,query_string,log_file_name)
        print(f'logged point {x+1} out of {duration_int} from analyzer at {PA_PORTS[analyzer_num]}')
    
    #write endline to log (so all PA data from the same time ends up in the same row)
    f=open(log_file_name,'a')
    f.write('\n')
    f.close()

    #wait till 1 second elapses before getting next measurement
    while(time.time()-start_time<1):
        pass