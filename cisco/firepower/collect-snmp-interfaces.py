#!/usr/bin/python
import netsnmp
import datetime
import pickle
import os
import time
import pprint


hosts = ["firewall.example.com"]
output_path = "/data/firepower/"
snmp_community = "public"

workingDirectory = "./work"



def snmpGet(host):
    #session = netsnmp.Session(Version=2, DestHost=host, Community=snmp_community)
    args = {
    "Version": 2, 
    "DestHost": host, 
    "Community": snmp_community
    }
    try:
        a_file = open(workingDirectory+"/"+host+".pkl", "rb")
        lastSample = pickle.load(a_file)
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        print "Warning! No last sample detected"
        lastSample = None
        
                
    
    newSample = dict()
    for idx in netsnmp.snmpwalk(netsnmp.Varbind("IF-MIB::ifIndex"), **args):
        ifname, oper, cin, cout, ifspeed = netsnmp.snmpget(
        netsnmp.Varbind("IF-MIB::ifName", idx),
        netsnmp.Varbind("IF-MIB::ifOperStatus", idx),
        netsnmp.Varbind("IF-MIB::ifHCInOctets", idx),
        netsnmp.Varbind("IF-MIB::ifHCOutOctets", idx),
        netsnmp.Varbind("IF-MIB::ifSpeed", idx),
        **args)
        assert(ifname is not None and
            cin is not None and
            cout is not None) 
        
        #Skip internal interfaces
        if ifname  == "Internal-Data0/1" or ifname  == "diagnostic" or ifname  == "nlp_int_tap" or ifname  == "ccl_ha_nlp_int_tap" or ifname  == "ha_ctl_nlp_int_tap" or ifname  == "failover" :
            continue
        
        # Only look at interfaces that are up
        if oper != "1": 
            continue

        newSample[ifname] =  {
                    'cin': cin,
                    'cout': cout,
                    'ts': time.time()
        }
        
        if(lastSample is not None):
            # Formula: https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/8141-calculate-bandwidth-snmp.html
            deltaSeconds    = int(newSample[ifname]['ts']) - int(lastSample[ifname]['ts'])
            deltaIn         = int(newSample[ifname]['cin']) - int(lastSample[ifname]['cin'])
            deltaOut        = int(newSample[ifname]['cout']) - int(lastSample[ifname]['cout'])
            utilizationIn   = ( float(deltaIn) * 8 ) / ( float(deltaSeconds) * 1024 * 1024) # Mbps
            utilizationOut   = ( float(deltaOut) * 8 ) / ( float(deltaSeconds) * 1024 * 1024 ) #Mbps

            #print("{} utz in: {} utz out: {}".format( ifname, utilizationIn, utilizationOut))
        
            fp = open(output_path+host+"-interfaces.csv","a+")
            now = datetime.datetime.now()
            log = "{},{},{},{}".format(now,ifname,utilizationIn,utilizationOut)

            fp.write(log+'\n')
            fp.close()
        else:
            print("Warning! No last sample detected - skipping")
    a_file = open(workingDirectory+"/"+host+".pkl", "wb")
    pickle.dump(newSample, a_file)
    a_file.close()

    
    
def main():
    #Create working directory if not exitsts
    if not os.path.exists(workingDirectory):
        os.makedirs(workingDirectory)

    for host in hosts:
        #print("Polling host {}".format(host))
        snmpGet(host)
   

if __name__ == "__main__":
    main()
