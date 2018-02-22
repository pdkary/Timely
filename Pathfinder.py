import sys
sys.path.append('C:\Users\pdkar\Desktop\Python\M.O.R.R.I')
from GraphClass import *

import simplejson, urllib
import geocoder


city = 'Orangeville ON'
def getLatLong(address,city):
    try:
        g = geocoder.google(address + city)
        return g.latlng
    except AttributeError:
        print 'Could not recognize :',address
    

def driveTime(ad1,ad2):
    orig_coord = ad1
    dest_coord = ad2
    url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins="+str(orig_coord)+"&destinations="+str(dest_coord)+"&mode=driving&language=en-EN&sensor=false"
    result= simplejson.load(urllib.urlopen(url))
    driving_time = result
    time = result['rows'][0]['elements'][0]['duration']['text']
    num = time.split()[::2]
    if len(num) == 1:
        return int(num[0])
    if len(num) == 2:
        return time,int(num[0])*60 + int(num[1])
    elif len(num) == 3:
        return int(num[0])*24*60 + int(num[1])*60 + int(num[2])
    else:
        return 'time limit exceeded'
    

def addressbook(alist):
    address = Graph()
    for x in alist:
        address.add_node(x)
    while alist:
        node = alist[0]
        for x in alist[1:]:
            address.add_edge(node,x,driveTime(node,x))
        alist.pop(0)

    return address

##l = ['28 forest park rd Orangeville ON','6 brookhaven cres Orangeville ON','215 elmwood cres Orangeville ON']
##
##g = addressbook(l)
##g.traveller('28 forest park rd Orangeville ON')

                             
    
            





        
