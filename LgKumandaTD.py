import http.client
from tkinter import *
import xml.etree.ElementTree as etree
import socket
import re
import sys
dialogMsg =""
lgtv = {}

headers = {"Content-Type": "application/atom+xml"}
cmdCodes = [('Ses +', '2'), ('Ses --', '3'), ('Kanal +', '0'), ('Kanal --', '1'), \
           ('Bilgi', '170'), ("Ekran 4:3", "118"), ("Ekran 16:9", "119"),("Ekran ++", "121"), \
           ("Dil Seç", "10"), ("Geri Dön", "91"), ("Record", "189"), ("Play", "176"), ("Pause", "186"), \
           ("Stop", "177"), ("Rewind", "143"), ("F.Forward", "142"),  ("<", "7"), (">", "6"), \
           ("^", "64"), ("v", "65"), ("OK",  "68")]
mytree = etree.parse("mychannels.xml")
channels = mytree.getroot()
lgtv["pairingKey"] = mytree.find("pairingKey").text

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


def getSessionid():
    global conn
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    pairCmd = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthReq</type><value>" \
            + lgtv["pairingKey"] + "</value></auth>"
    conn.request("POST", "/hdcp/api/auth", pairCmd, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != "OK" : return httpResponse.reason
    tree = etree.XML(httpResponse.read())
    return tree.find('session').text


def displayKey():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    reqKey = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthKeyReq</type></auth>"
    conn.request("POST", "/hdcp/api/auth", reqKey, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != "OK" : sys.exit("Network Hatası")
    return httpResponse.reason


def getPairingKey():
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
    displayKey()
    root = Tk()
    root.withdraw()
    dialogMsg = "TV Ekranında verilen Pairing Key\nveya Eşleme Anahtarı\ndegerini aşağıdaki kutuya\nörneğin ABCDEF seklinde giriniz\n"
    d = MyDialog(root, dialogMsg)
    root.wait_window(d.top)
    lgtv["pairingKey"] = result
    root.destroy()


def changechannel(intval):
    chchanCmd = "<?xml version=\"1.0\" encoding=\"utf-8\"?><command><session>" \
                + lgtv["session"]  \
                + "</session><type>HandleChannelChange</type>" \
                +  etree.tostring(channels[intval][1]) \
                +  etree.tostring(channels[intval][2]) \
                +  etree.tostring(channels[intval][3]) \
                +  etree.tostring(channels[intval][4]) \
                + "</command>"
    conn.request("POST", "/hdcp/api/dtv_wifirc",chchanCmd , headers=headers)
    r1 = conn.getresponse()
    msgboxButton.config(text = "==> Kanal: " + channels[intval][1].text + ' ' + r1.reason)

def handleCommand(cmdcode):
    cmdText = "<?xml version=\"1.0\" encoding=\"utf-8\"?><command><session>" \
                + lgtv["session"]  \
                + "</session><type>HandleKeyInput</type><value>" \
                + cmdcode \
                + "</value></command>"
    conn.request("POST", "/hdcp/api/dtv_wifirc", cmdText, headers=headers)
    r1 = conn.getresponse()
    msgboxButton.config(text = "==> Kod: " + cmdcode + " " + r1.reason)

def go(val):
    intval = int(val)
    changechannel(intval)
class Uutton(Button):
    def __init__(self, master=None, idx=None, **kw):
        Button.__init__(self, master=None, **kw)
        self["command"]=lambda: go(idx)

def doCmd(cmdcode):
    handleCommand(cmdcode)
class Cutton(Button):
    def __init__(self, master=None, cmdcode=None, **kw):
        Button.__init__(self, master=None, **kw)
        self["command"]=lambda: doCmd(cmdcode)


lgtv["ipaddress"] =  getip()
theSessionid = getSessionid()
pairinKeyChanged = False
while theSessionid == "Unauthorized" :
    getPairingKey()
    pairinKeyChanged = True
    theSessionid = getSessionid()
if len(theSessionid) < 8 : sys.exit("SessionId alInamadı:" + theSessionid)
lgtv["session"] = theSessionid

if pairinKeyChanged:
    mytree.find("pairingKey").text = lgtv["pairingKey"]
    mytree.write("mychannels.xml", encoding="UTF-8")

channels.remove(mytree.find("pairingKey"))

indxx = 0
for each in channels:
    elem = etree.Element("idx")
    elem.text=str(indxx)
    indxx += 1
    each.append(elem)

master = Tk()
buttons = [Uutton(master, chnl[6].text, text=chnl[5].text, height=1, width=17, \
          activebackground='light grey', anchor=W) for chnl in channels]

msgboxButton = Label(master, text='', height=1, width=19, bd=4, bg='blue', fg="yellow", relief=SUNKEN, anchor=W)

buttons += [msgboxButton]

buttons += [Cutton(master, commandcode, text=commandtext, height=1, width=10, \
           bg="light green", activebackground='yellow', anchor=W)  \
           for (commandtext, commandcode) in cmdCodes]

iddr=0
for button in buttons:
    button.grid(row = iddr%26, column = iddr//26)
    iddr += 1

master.title("LgKumandaTD")
master.mainloop()
