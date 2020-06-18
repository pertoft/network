#!/usr/bin/python
import netsnmp
import datetime

hosts = ["fut-prod-fp01.fut.netic.dk", "fut-prod-fp01-sec.fut.netic.dk","fut-preprod-fp01.fut.netic.dk", "fut-preprod-fp01-sec.fut.netic.dk",]
hosts_os = ["fut-prod-fp01-dc1.fut.netic.dk", "fut-prod-fp01-dc4.fut.netic.dk","fut-preprod-fp01-dc1.fut.netic.dk", "fut-preprod-fp01-dc4.fut.netic.dk"]
output_path = "/data/splunk/fut/"
snmp_community = "public"


def snmpGet(host,oid):
    session = netsnmp.Session(Version=2, DestHost=host, Community=snmp_community)
    
    results_objs = netsnmp.VarList(netsnmp.Varbind(oid)) 
    session.get(results_objs)
    return results_objs

def main():
    for host in hosts:
        fp = open(output_path+host+".csv","a+")
        #Source: https://www.cisco.com/c/en/us/products/collateral/security/firepower-ngfw/white-paper-c11-741739.html#_Toc5440006
        results = snmpGet(host,'.1.3.6.1.4.1.9.9.109.1.1.1.1.8.1')    # CPU 5 minutes
        for result in results:
            now = datetime.datetime.now()
            log = "{},{}".format(now,result.val)
            #print(log) 
            fp.write(log+'\n')
        fp.close()
  
    for host in hosts_os:
        fp = open(output_path+host+".csv","a+")
        results = snmpGet(host,'.1.3.6.1.4.1.2021.11.11.0')    # CPU idle 5 minutes
        
        for result in results:
            now = datetime.datetime.now()
            log = "{},{}".format(now,(100-int(result.val))) # Subtract 100 from the idle value to determine the utilization
            #print(log)
            fp.write(log+'\n')
        fp.close()


if __name__ == "__main__":
    main()
