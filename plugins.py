import PyPDF2
import os
from subprocess import call
import zipfile
import rarfile
import magic
import ms_offcrypto_tool
import pyclamd

def isProtectedpdf(file_location):
    pdf = PyPDF2.PdfFileReader(file_location)
    return pdf.isEncrypted

def Decryptpdf(file_location,passwd):
    tckdir = os.path.dirname(file_location) + '/tocheck'
    tckfile = tckdir + '/' + os.path.basename(file_location)
    if not os.path.exists(tckdir):
        os.mkdir(tckdir)
    ret = call(["pdftk",file_location,"input_pw",passwd,"output",tckfile])
    print ret
    if ret == 0:
        ret = True
    else:
        ret = False
    return ret,tckfile

def isProtectedoffice(file_location):
    return True

def isProtectedrar(file_location):
    enc = False
    rf = rarfile.RarFile(file_location)
    enc = rf.needs_password()
    return enc


def isProtectedzip(file_location):
    enc = False
    zf = zipfile.ZipFile(file_location)
    for zinfo in zf.infolist():
        is_encrypted = zinfo.flag_bits & 0x1
        if is_encrypted:
            print '%s is encrypted!' % zinfo.filename
            enc = True
    return enc


def Decryptoffice(file_location, passwd):
    tckdir = os.path.dirname(file_location) + '/tocheck'
    tckfile = tckdir + '/' + os.path.basename(file_location)
    try:
        file = ms_offcrypto_tool.OfficeFile(file_location)
        file.load_password(passwd)
        print 'Try to decript'
        dec_buf = file.decrypt()
        print 'Checking...'
        test = magic.from_buffer(dec_buf,True)
        print test
        if "pgp" in test or "octet" in test:
            print 'decrypt failed'
            return False
        else:
            if not os.path.exists(tckdir):
                os.makedirs(tckdir)
            fn = os.path.basename(file_location)
            dec_file = open(tckfile,'wb')
            dec_file.write(dec_buf)
            return True,tckfile
            


    except Exception as e:
        print e
        return False,tckfile

def Decryptzip(file_location,passws):
    encrypted_zip = zipfile.ZipFile( file_location  )
    encrypted_zip.setpassword(passws)
    print encrypted_zip.namelist()
    tckdir =  os.path.abspath(os.path.dirname(file_location)) + '/tocheck'
    tckfile = tckdir + '/' + os.path.basename(file_location)
    if not os.path.exists(tckdir):
        os.mkdir(tckdir)
    ret = call(["unzip","-P",passws, "-o",file_location,"-d",tckdir])
    print ret
    if ret == 0:
        ret = call(["zip",tckfile, "-r",  tckdir])
        if not ret ==0:
            print ret
            return False , tckfile
        else:
            return True , tckfile 
    else:
        return False , tckfile