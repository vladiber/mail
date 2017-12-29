from flask import Flask ,request ,render_template ,jsonify
import elastic
import json
from jinja2 import Template
import Decrypt
import smtplib 
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.message import Message
import magic
import pyclamd
app = Flask(__name__)

Gid = 0
@app.route('/<elid>/show',methods = ['GET','POST'])
def index(elid):
    global Gid
    Gid = elid
    m = elastic.GetMail(elid)
    a= m.attachments
    if a == None:
        
        return render_template('wx.html')
    else:
        return render_template('show.html',my_list=a)
@app.route('/config')
def config():
    conf = elastic.GetConfig(1)
    lp = conf.local_port
    nhp = conf.next_hop_port
    nhh = conf.next_hop_host
    return render_template('settings.html',lp=lp,nhp=nhp,nhh=nhh)

@app.route('/saveset')
def save():
    lp = request.args.get('lport')
    nhh = request.args.get('nhhost')
    nhp = request.args.get('nhport')
    a = elastic.WriteConfig(nhh,nhp,lp)
    return json.dumps({"result":a})

@app.route('/check')
def check():
    p = request.args.get('pass', 0, type=str)
    id = request.args.get('id')
    name = request.args.get('name')
    file_loc = 'process/' + Gid +'/'+ name
    res,clamres = Decrypt.Decrypt_file(file_loc,p)

    if res == True:
        
        elastic.UpdateTags("Decrypted " ,Gid)
        
        if "FOUND" in str(clamres):
            print clamres['stream'][1]
            elastic.UpdateVirus(clamres, Gid)
            sendNotification(name,Gid)
        else:
            sendFileToUser(Gid,file_loc,name)
    else:
        elastic.UpdateTags("Dec_failed: "+ name,Gid)
        
    return json.dumps({"result":res,"id":id,"name":name})

def sendNotification(name,id):
    m = elastic.GetMail(id)
    to = str(m.mail_to[0])
    
    root = MIMEMultipart()
    root["From"] = "Mail System <mail@vm.dom>"
    root["To"] = to
    root["Subject"] = "Virus Found in %s" % name
    root.add_header('Content-Type','plain/text')
    ms = smtplib.SMTP("localhost",25)
    res = ms.sendmail("mail@test.dom",to,root.as_string())

def sendFileToUser(id,file_loc,name):
    fp = open(file_loc,'rb')
    m = elastic.GetMail(id)
    to = str(m.mail_to[0])
    
    root = MIMEMultipart()
    root["From"] = "Mail System <mail@vm.dom>"
    root["To"] = to
    root["Subject"] = "Your file %s is released" % name
    #ctype = magic.from_file(file_loc,True)
    ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    msg = MIMEBase(maintype, subtype)
    msg.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(msg)
    

    msg.add_header('Content-Disposition', 'attachment', filename=name)
    
    root.attach(msg)
    ms = smtplib.SMTP("localhost",25)
    res = ms.sendmail("mail@test.dom",to,root.as_string())
def clamcheck(file):
    cd = pyclamd.ClamdNetworkSocket('127.0.0.1',3310)
    ret = cd.scan_stream(open(file))
    return ret

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4000)
    