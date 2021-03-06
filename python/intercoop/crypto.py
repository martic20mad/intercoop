# -*- encoding: utf-8 -*-

"""
Simple interface to common cryptographic actions.
"""

class _deps:
    "Hides dependencies on external modules"
    import uuid
    import base64
    from Crypto.Hash import SHA
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5

def uuid():
    return str(_deps.uuid.uuid4())

def encode(text):
    "Encode text into base64 (as text)"
    return bencode(text.encode('utf8'))

def decode(b64string):
    "Decode base64 (as text) back into text"
    return bdecode(b64string).decode('utf8')

def bencode(binaryStream):
    "Encode bytes (binary) as base64 (as text)"
    return _deps.base64.urlsafe_b64encode(binaryStream).decode('utf8')

def bdecode(b64string):
    "Decode base64 (as text) back into bytes (binary)"
    return _deps.base64.urlsafe_b64decode(b64string.encode('utf8'))

def sha(text):
    "Returns the SHA of a text"
    return _deps.SHA.new(text.encode('utf-8'))

def generateKey(filename=None, publicfilename=None):
    key = _deps.RSA.generate(2048)
    if filename:
        exportKey(key, filename, publicfilename)
    return key

def exportKey(key, filename, publicfilename=None):
    with open(filename,'wb') as f:
        f.write(key.exportKey('PEM'))
    if publicfilename is not None:
        exportPublicKey(key, publicfilename)

def exportPublicKey(key, filename):
    public = key.publickey()
    with open(filename,'wb') as f:
        f.write(public.exportKey('PEM'))

def loadKey(filename):
    with open(filename,'rb') as f:
        return _deps.RSA.importKey(f.read())

def sign(privatekey, text):
    signer = _deps.PKCS1_v1_5.new(privatekey)
    return bencode(signer.sign(sha(text)))

def isAuthentic(publickey, text, signature):
    verifier = _deps.PKCS1_v1_5.new(publickey)
    decodedSignature = bdecode(signature)
    return verifier.verify(sha(text), decodedSignature)


# vim: ts=4 sw=4 et
