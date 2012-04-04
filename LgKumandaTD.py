import http.client
from tkinter import *
import xml.etree.ElementTree as etree
import socket
import re

lgtv = {}
lgtv["pairingKey"] = "DDGWUF"
headers = {"Content-Type": "application/atom+xml"}
cmdCodes = [('Ses +', '2'), ('Ses --', '3'), ('Kanal +', '0'), ('Kanal --', '1'), \
           ('Bilgi', '170'), ("Ekran 4:3", "118"), ("Ekran 16:9", "119"),("Ekran ++", "121"), \
           ("Dil Seç", "10"), ("Geri Dön", "91"), ("Record", "189"), ("Play", "176"), ("Pause", "186"), \
           ("Stop", "177"), ("Rewind", "143"), ("F.Forward", "142"),  ("<", "7"), (">", "6"), \
           ("^", "64"), ("v", "65"), ("OK",  "68")]
mytree = etree.parse("mychannels.xml")
channels = mytree.getroot()


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
    #        print (gotstr)
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
    return ipaddress



lgtv["ipaddress"] =  getip()
conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
pairCmd = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthReq</type><value>" \
           + lgtv["pairingKey"] + "</value></auth>"
conn.request("POST", "/hdcp/api/auth", pairCmd, headers=headers)
r1 = conn.getresponse()
tree = etree.XML(r1.read())
lgtv["session"] = tree.find('session').text


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

indxx = 0
for each in channels:
    elem = etree.Element("idx")
    elem.text=str(indxx)
    indxx += 1
    each.append(elem)

master = Tk()

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

buttons = [Uutton(master, chnl[6].text, text=chnl[5].text, height=1, width=17, activebackground='light grey', anchor=W) for chnl in channels]


msgboxButton = Label(master, text='', height=1, width=19, bd=4, bg='blue', fg="yellow", relief=SUNKEN, anchor=W)

buttons += [msgboxButton]


buttons += [Cutton(master, commandcode, text=commandtext, height=1, width=10, bg="light green", activebackground='yellow', anchor=W) for (commandtext, commandcode) in cmdCodes]


iddr=0
for button in buttons:
    button.grid(row = iddr%26, column = iddr//26)
    iddr += 1


master.title("LgKumandaTD")


master.mainloop()
