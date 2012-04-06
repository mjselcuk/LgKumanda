import http.client
from tkinter import *
import xml.etree.ElementTree as etree
import socket
import re
import sys
lgtv = {}
dialogMsg =""
headers = {"Content-Type": "application/atom+xml"}
lgtv["pairingKey"] = "DDGWUF"

class MyDialog:
    def __init__(self, parent, dialogMsg):
        top = self.top = Toplevel(parent)
        Label(top, text = dialogMsg, justify="left").pack()
        self.e = Entry(top)
        self.e.pack(padx=5)
        self.e.focus_set()
        b = Button(top, text="Tamam", command=self.ok)
        b.pack(pady=5)
        top.bind("<Return>", self.ok)
        top.title("LG Kumanda")
        top.geometry("410x250+10+10")
    def ok(self,dummy=None):
        global result
        result = self.e.get()
        self.top.destroy()


def getip():
    strngtoXmit =   'M-SEARCH * HTTP/1.1' + '\r\n' + \
                    'HOST: 239.255.255.250:1900'  + '\r\n' + \
                    'MAN: "ssdp:discover"'  + '\r\n' + \
                    'MX: 2'  + '\r\n' + \
                    'ST: urn:schemas-upnp-org:device:MediaRenderer:1'  + '\r\n' +  '\r\n'

    bytestoXmit = strngtoXmit.encode()
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.settimeout(3)
    found = False
    gotstr = 'notyet'
    i = 0
    ipaddress = None
    sock.sendto( bytestoXmit,  ('239.255.255.250', 1900 ) )
    while not found and i <= 5 and gotstr == 'notyet':
        try:
            gotbytes, addressport = sock.recvfrom(512)
            gotstr = gotbytes.decode()
        except:
            i += 1
            sock.sendto( bytestoXmit, ( '239.255.255.250', 1900 ) )
        if re.search('LGE', gotstr):
            ipaddress, _ = addressport
            found = True
        else:
            gotstr = 'notyet'
        i += 1
    sock.close()
    if not found : sys.exit("LG tv bulunamadi")
    return ipaddress


def displayKey():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    reqKey = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthKeyReq</type></auth>"
    conn.request("POST", "/hdcp/api/auth", reqKey, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != "OK" : sys.exit("Network Hatası")
    return httpResponse.reason


def getSessionid():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    pairCmd = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthReq</type><value>" \
            + lgtv["pairingKey"] + "</value></auth>"
    conn.request("POST", "/hdcp/api/auth", pairCmd, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != "OK" : return httpResponse.reason
    tree = etree.XML(httpResponse.read())
    return tree.find('session').text


def getPairingKey():
    displayKey()
    root = Tk()
    root.withdraw()
    dialogMsg = "TV Ekranında verilen Pairing Key\nveya Eşleme Anahtarı\ndegerini aşağıdaki kutuya\nörneğin ABCDEF seklinde giriniz\n"
    d = MyDialog(root, dialogMsg)
    root.wait_window(d.top)
    lgtv["pairingKey"] = result

def handleCommand(cmdcode):
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    cmdText = "<?xml version=\"1.0\" encoding=\"utf-8\"?><command><session>" \
                + lgtv["session"]  \
                + "</session><type>HandleKeyInput</type><value>" \
                + cmdcode \
                + "</value></command>"
    conn.request("POST", "/hdcp/api/dtv_wifirc", cmdText, headers=headers)
    httpResponse = conn.getresponse()


#main()

lgtv["ipaddress"] = getip()
theSessionid = getSessionid()
while theSessionid == "Unauthorized" :
    getPairingKey()
    theSessionid = getSessionid()

if len(theSessionid) < 8 : sys.exit("SessionId alInamadı:" + theSessionid)

lgtv["session"] = theSessionid


dialogMsg =""
for lgkey in lgtv :
    dialogMsg += lgkey + ": " + lgtv[lgkey] + "\n"

dialogMsg += "LG TV nizde başariyla kumanda oturumu  açıldı.\n"
dialogMsg += "=" * 28 + "\n"
dialogMsg += "Bir komut kodu yani 0 - 255 arasinda bir rakam girin.\n"
dialogMsg += "Çıkış için 255 den büyük bir rakam girin.\n"
dialogMsg += "Örneğin:\n"
dialogMsg += "EZ_ADJUST    menu için   255 \n"
dialogMsg += "IN START       menu için   251 \n"
dialogMsg += "Installation    menu için   207 \n"
dialogMsg += "POWER_ONLY  mode için  254 \n"
dialogMsg += "UYARI: POWER_ONLY mode nedir bilmiyorsanız 254 GİRMEYİN! "


result = "91"
while int(result) <= 255:
    root = Tk()
    root.withdraw()
    d = MyDialog(root, dialogMsg)
    root.wait_window(d.top)
    handleCommand(result)