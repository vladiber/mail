import bs4
import asyncore
from smtpd import SMTPServer
from email.parser import Parser
from email.mime import multipart , text
from StringIO import StringIO
import email
import magic, os
import zipfile
import rarfile
import PyPDF2
import ms_offcrypto_tool
import smtplib
from subprocess import call
import pyclamd
import elastic
import uuid
import Decrypt
from tnefparse import TNEF
from email.mime.text import MIMEText
import socket

class EmlServer(SMTPServer):
    no = 0
    def process_message(self, peer, mailfrom, rcpttos, data):
              
        e = email.message_from_string(data)
        #name = '%s-%d' % (datetime.now().strftime('%Y%m%d%H%M%S'),
        #    self.no)
        print "reseived mail from %s" % mailfrom
        m_uuid = uuid.uuid4()
        name  = 'korobka/%s' % (m_uuid)
        dirname = 'process/%s' % (m_uuid)
        filename = '%s.eml' % (name)
        open(filename, 'wb').write(data)
        elastic.WriteES(mailfrom,rcpttos,m_uuid,0)

        path = os.makedirs(dirname)
        newmsg = extractAttachment(e,dirname,m_uuid)
        open(filename + "-new", 'wb').write(newmsg)
        print '%s saved.' % filename
        self.no += 1
        nh = smtplib.SMTP('localhost',25)
        a = nh.sendmail(mailfrom,rcpttos,newmsg)
        print a

def extractAttachment(msg, dirname, uuid):
    lip = socket.gethostbyname(socket.gethostname())
    an = 0
    base_url = '''http://%s:4000/''' % lip
    FlagLink = False
    kuku = False
    #print msg.get_payload()
    for msgrep in msg.walk():
        i = 0
        if msgrep.is_multipart():
            payload=msgrep.get_payload()
            link ="""<a href=3D"%s/%s/show">Somae file are here </a></head>""" % (base_url, str(uuid))
            newpayload = []
            q_att = []
            for attachment in payload:
                print attachment.get_content_type()
                if "html" in attachment.get_content_type():    
                    if FlagLink:
                        hhh = attachment.get_payload()
                        a = hhh.split("</head>")
                        newhhh = a[0]+link+a[1]
                        attachment.set_payload(newhhh)

                att_name = attachment.get_filename(None)
                if att_name is not None:
                    
                    if att_name.lower() in ["winmail.dat","win.dat"]:
                        file_buf = attachment.get_payload(decode=True)
                        winmail = TNEF(file_buf)
                        for att in winmail.attachments:
                            print att.name

                    f = writeFile(att_name, attachment,dirname)
                    a = Decrypt.Check_Encryption(f)
                    if not a:
                        file_buf = attachment.get_payload(decode=True)
                        res = clamcheck_buf(file_buf)
                        print str(res).lower()
                        if "encrypted" not in str(res).lower():
                            newpayload.append(attachment)
                        else:
                            q_att.append(att_name)
                    else:
                        q_att.append(att_name)
                        FlagLink = True
                else:
                    newpayload.append(attachment)
                i+=1
            msgrep.set_payload(newpayload)
            if not q_att == []:
                elastic.UpdateAtts(q_att,uuid)
    
    #if FlagLink:
    #    msg = ModHtml(uuid,msg)
    
    
    return msg.as_string()

def clamcheck(file):
    cd = pyclamd.ClamdNetworkSocket('127.0.0.1',3310)
    ret = cd.scan_stream(open(file))
    return ret

def ModHtml(uuid,msg):
    for msgrep in msg.walk():
        if msgrep.is_multipart():
            payload=msgrep.get_payload()
            for attachment in payload:
                if "html" in attachment.get_content_type():    
                    try:
                        hhh = attachment.get_payload()
                        soup = bs4.BeautifulSoup(hhh)
                        new_link = soup.new_tag("a", href="hhttp://192.168.204.131:4000/" + str(uuid) + "/show")
                        new_link.string = "LINK"
                        soup.head.append(new_link)
                        attachment.set_payload(str(soup))
                        return msg
                    except Exception as e:
                        print e.message
                        return msg

def clamcheck_buf(buf):
    cd = pyclamd.ClamdNetworkSocket('127.0.0.1',3310)
    ret = cd.scan_stream(buf)
    return ret

def printIT(m, filename):
    print 'Magic: %s\n\tSaved File as: %s\n' % (m, filename)


def writeFile(filename, payload , dirname):
    try:
        file_location = dirname + '/' + filename
        open(file_location, 'wb').write(payload.get_payload(decode=True))
    except (TypeError, IOError):
        pass
    return file_location

        
def run():
    foo = EmlServer(('0.0.0.0', 10025),None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    run()