
import Decrypt
import plugins
import os
import socket
import elastic
#isen = Decrypt.Check_Encryption("/home/vladib/mail/Book1.xlsx")
#print os.path.abspath(os.path.dirname("process/a.zip"))
#plugins.Decryptzip('/home/vladib/mail/mail.zip','1')
l = socket.gethostbyname(socket.gethostname())
elastic.WriteConfig('dd')