import elastic
import rarfile
import zipfile
import os
import ms_offcrypto_tool
from subprocess import call
import magic
from plugins import *
import plugins
import pyclamd
supported = ["pdf","zip","rar","cdfv2 enc"]

def enc_type(file_location):
    mg = magic.from_file(file_location).lower()
    print mg
    if "cdfv2 enc" in mg:
        return "office"
    f = "unsupported"
    r = False
    for i in supported:
        if i in mg:
            f = i
    return f
    
def Check_Encryption(file_location):
    
    f = enc_type(file_location)
    if not f == "unsupported":
        en_method = getattr(plugins,'isProtected'+f)
        r = en_method(file_location)
        print r
        print '%s Type %s' % (file_location, f )
    else:
        print '%s Unsupported Type or not encrypted' % (file_location)
        r = False
    return r

def Decrypt_file(file_location,passwd):
    f = enc_type(file_location)
    en_method = getattr(plugins,'Decrypt'+f)
    res,tocheck = en_method(file_location,passwd)
    if res:
        clamres = clamcheck(tocheck)
    else:
        return res,None
    return res,clamres

def clamcheck(file):
    cd = pyclamd.ClamdNetworkSocket('127.0.0.1',3310)
    ret = cd.scan_stream(open(file))
    return ret
def clamcheck_buf(buf):
    cd = pyclamd.ClamdNetworkSocket('127.0.0.1',3310)
    ret = cd.scan_stream(buf)
    print ret
    return ret