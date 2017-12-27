import sys, hashlib, base64, binascii, functools
from struct import pack, unpack

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5

import olefile
from xml.dom.minidom import parseString

SEGMENT_LENGTH = 4096

def hashCalc(i, algorithm):
    if algorithm == "SHA512":
        return hashlib.sha512(i)
    else:
        return hashlib.sha1(i)

def decrypt(key, keyDataSalt, hashAlgorithm, ifile):
    obuf = b''
    totalSize = unpack('<I', ifile.read(4))[0]
    sys.stderr.write("totalSize: {}\n".format(totalSize))
    ifile.seek(8)
    for i, ibuf in enumerate(iter(functools.partial(ifile.read, SEGMENT_LENGTH), b'')):
        saltWithBlockKey = keyDataSalt + pack('<I', i)
        iv = hashCalc(saltWithBlockKey, hashAlgorithm).digest()
        iv = iv[:16]
        aes = AES.new(key, AES.MODE_CBC, iv)
        dec = aes.decrypt(ibuf)
        obuf += dec
    #ofile.write(obuf)
    return obuf

def generate_skey_from_privkey(privkey, encryptedKeyValue):
    privkey = PKCS1_v1_5.new(RSA.importKey(privkey))
    skey = privkey.decrypt(encryptedKeyValue, None)
    return skey

def generate_skey_from_password(password, saltValue, hashAlgorithm, encryptedKeyValue, spinValue, keyBits):
    block3 = bytearray([0x14, 0x6e, 0x0b, 0xe7, 0xab, 0xac, 0xd0, 0xd6])
    # Initial round sha512(salt + password)
    h = hashCalc(saltValue + password.encode("UTF-16LE"), hashAlgorithm)

    # Iteration of 0 -> spincount-1; hash = sha512(iterator + hash)
    for i in range(0, spinValue, 1):
        h = hashCalc(pack("<I", i) + h.digest(), hashAlgorithm)

    h2 = hashCalc(h.digest() + block3, hashAlgorithm)
    # Needed to truncate skey to bitsize
    skey3 = h2.digest()[:keyBits//8]

    # AES encrypt the encryptedKeyValue with the skey and salt to get secret key
    aes = AES.new(skey3, AES.MODE_CBC, saltValue)
    skey = aes.decrypt(encryptedKeyValue)
    return skey

def parseinfo(ole):
    ole.seek(8)
    xml = parseString(ole.read())
    keyDataSalt = base64.b64decode(xml.getElementsByTagName('keyData')[0].getAttribute('saltValue'))
    keyDataHashAlgorithm = xml.getElementsByTagName('keyData')[0].getAttribute('hashAlgorithm')
    password_node = xml.getElementsByTagNameNS("http://schemas.microsoft.com/office/2006/keyEncryptor/password", 'encryptedKey')[0]
    spinValue = int(password_node.getAttribute('spinCount'))
    encryptedKeyValue = base64.b64decode(password_node.getAttribute('encryptedKeyValue'))
    passwordSalt = base64.b64decode(password_node.getAttribute('saltValue'))
    passwordHashAlgorithm = password_node.getAttribute('hashAlgorithm')
    passwordKeyBits = int(password_node.getAttribute('keyBits'))
    info = {
        'keyDataSalt': keyDataSalt,
        'keyDataHashAlgorithm': keyDataHashAlgorithm,
        'encryptedKeyValue': encryptedKeyValue,
        'spinValue': spinValue,
        'passwordSalt': passwordSalt,
        'passwordHashAlgorithm': passwordHashAlgorithm,
        'passwordKeyBits': passwordKeyBits,
    }
    return info

class OfficeFile:
    def __init__(self, file):
        ole = olefile.OleFileIO(file)
        self.file = ole
        self.info = parseinfo(ole.openstream('EncryptionInfo'))
        self.secret_key = None
    def load_skey(self, secret_key):
        self.secret_key = secret_key
    def load_password(self, password):
        self.secret_key = generate_skey_from_password(password, self.info['passwordSalt'], self.info['passwordHashAlgorithm'], self.info['encryptedKeyValue'], self.info['spinValue'], self.info['passwordKeyBits'])
    def load_privkey(self, private_key):
        self.secret_key = generate_skey_from_privkey(private_key, self.info['encryptedKeyValue'])
    def decrypt(self):
        dec = decrypt(self.secret_key, self.info['keyDataSalt'], self.info['keyDataHashAlgorithm'], self.file.openstream('EncryptedPackage'))
        return dec

def main():
    
    
    file = OfficeFile('Book1.xlsx')

    file.load_password('P@ssw0rd')

    file.decrypt(open('1.xlsx','wb'))

if __name__ == '__main__':
    main()
