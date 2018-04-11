#!/usr/bin/python
import time
import datetime
import urllib2
import requests
import test_ping.py
import os
from requests.exceptions import ConnectionError
import serial
from influxdb import InfluxDBClient

while 1:    
    try:
            while 1:
                        
                        serial_port = "/dev/ttyAMA0" # or "/dev/ttyS0"
                        baud = 38400
                        host = '13.95.148.9'
                        port = 8086
                        DBNAME = 'monitor'
                        USER = 'root'
                        PASSWORD = 'root'
                        #import serial
                        ser = serial.Serial(serial_port, baud, timeout=1)
                        #from influxdb import InfluxDBClient
                        client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)  
                        
                        response = ser.readline()
                        Z = response.split(",")
                        X = ['RealP1','RealP2','RealP3','Irms1','Irms2','Irms3','Vrms']
                        Y = ['RealP1(kwh)','RealP2(kwh)','RealP3(kwh)']
                        if len(Z)>=2:
                            try:
                                now = datetime.datetime.today()
                                i=0
                                j=0
                                points1 = []
                                points2 = []                    
                                for z in Z:                    
                                    point1 = {
                                                "measurement":'two_sec',
                                                "time": 1000000000*int(now.strftime('%s')),
                                                "tags": {
                                                        "measure_type":X[i]
                                                },        
                                                "fields": {
                                                        "value":float(z)
                                                }
                                        }
                                    if j < 3:    
                                        point2 = {
                                                    "measurement":'two_sec_kwh',
                                                    "time": 1000000000*int(now.strftime('%s')),
                                                    "tags": {
                                                            "measure_type":Y[j]
                                                    },        
                                                    "fields": {
                                                            "value_kWh":(float(z)/600)
                                                    }
                                            }
                                    points1.append(point1)
                                    points2.append(point2)   
                                    i=i+1
                                    j=j+1
                                #print(points1)
                                #print(points2)
                                client.write_points(points1)
                                client.write_points(points2)
                                print("wifi's up --> send data to ouss now: %s" %datetime.datetime.today())

                            except KeyboardInterrupt:
                                ser.close() 
    

    except ConnectionError as e:
                #print e 
                print ("wifi down")
                print("ouss out cause wifi down now: %s" %datetime.datetime.today())
                try:
                        host = '13.95.148.9'
                        port = 8086
                        DBNAME = 'monitor'
                        USER = 'root'
                        PASSWORD = 'root'

                        from influxdb import InfluxDBClient
                        client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME) 
                        j=1
                        while 1:
                            i=1
                            while i<701:    
                                w=test_ping.have_internet()
                                if w==1:
                                    raise Exception
                                else:
                                    i=i+1
                                    ser = serial.Serial('/dev/ttyAMA0', 38400)
                                    response1 = ser.readline()
                                    z = response1.split(",")
                                    if len(z)>=6:
                                        now1 = datetime.datetime.today()
                                        now = 1000000000*int(now1.strftime('%s'))
                                        p1=float(z[3])/600
                                        p2=float(z[4])/600
                                        p3=float(z[5])/600
                                        if i==700:
                                            j=j+1
                                        f=open("test_file%s.txt"%j,"a+")
                                        f.write("two_sec,measure_type=Irms1 value=%s %s \ntwo_sec,measure_type=Irms2 value=%s %s \ntwo_sec,measure_type=Irms3 value=%s %s \ntwo_sec,measure_type=RealP1 value=%s %s \ntwo_sec,measure_type=RealP2 value=%s %s \ntwo_sec,measure_type=RealP3 value=%s %s \ntwo_sec,measure_type=Vrms value=%s %s \n" % (float(z[0]), now, float(z[1]), now, float(z[2]), now, float(z[3]), now, float(z[4]), now, float(z[5]), now, float(z[6]), now) )
                                        f.close()
                                        n=open("test_file_kwh%s.txt"%j,"a+")
                                        n.write("two_sec_kwh,measure_type=RealP1(kwh) value_kWh=%s %s \ntwo_sec_kwh,measure_type=RealP2(kwh) value_kWh=%s %s \ntwo_sec_kwh,measure_type=RealP3(kwh) value_kWh=%s %s \n" % (p1, now, p2, now, p3, now) )  
                                    print("wifi's down --> sending data to file %s now: %s" %(j, datetime.datetime.today()))    
                except Exception:
                    print ("wifi is up")
                    print("local out cause wifi up, now : %s" %datetime.datetime.today()) 
                    for n in range(1, j+1): 
                        with open("test_file%s.txt"%n,"r") as input:
                            flux=input.read()
                        r=client.request('write?db=monitor', method=u'POST', params=None, data=flux, expected_response_code=204, headers=None)
                        with open("test_file_kwh%s.txt"%n,"r") as input1:
                            flux1=input1.read()
                        s=client.request('write?db=monitor', method=u'POST', params=None, data=flux1, expected_response_code=204, headers=None)     
                    print("data transformed successfully to ouss now : %s" %datetime.datetime.today())
                    try:
                        for n in range(1, j+1):
                            os.remove("test_file%s.txt"%n)
                            os.remove("test_file_kwh%s.txt"%n)
                        print("file deleted successfully now : %s" %datetime.datetime.today())
                    except OSError:
                        pass
                except KeyboardInterrupt:
                        ser.close()                     

    except Exception:
        print ("wifi is up again")
    except KeyboardInterrupt:
        ser.close()
        print ("out of try")           

