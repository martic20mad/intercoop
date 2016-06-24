# -*- encoding: utf-8 -*-

import unittest
from . import crypto
import os


class Crypto_Test(unittest.TestCase):

    plain = "this is the content\n"
    base64 = "dGhpcyBpcyB0aGUgY29udGVudAo="
    signed = (
        "AxmEUIQBd82wC4-9Jm337gWbvMapcLMVvE3Ord9wvnFmvuMUW7qzO-uI8Iac"
        "rW6uPWM-93g9Y6q2YjfeQCZl_JB7lJorY5PLgSXhvu0-TcCPFkaIEAh7-4Tl"
        "lQx_-hwoN1Q3REOy-pB12iJZf9XrrOejfGG83kqXmXElSeS5RAWKwt2FcJFL"
        "IZIRZ9CDHRvX31428YURv-HlmpklwBE_t6WSJmc-b4dCcTDKih-eJ3OteDvM"
        "csN_0H76uzEZTbJf3GwH8m5lCjNkWKVufBP_J2aQ-LvtgKiuyZI6lP9TcffV"
        "da9k4vdM2zoPDtGTAxZQz68suevbGbAM_fYnBge2FA=="
        )

    def setUp(self):
        self.maxDiff = None
        self.keyfile = 'testkey.pem'
        self.pubfile = 'testkey-public.pem'

        if not os.access(self.keyfile, os.F_OK):
            crypto.generateKey(self.keyfile, self.pubfile)

        self.key = crypto.loadKey(self.keyfile)
        self.public = crypto.loadKey(self.pubfile)

    def test_encode_unicode(self):
        encoded = crypto.encode(self.plain)
        self.assertMultiLineEqual(self.base64, encoded)

    def test_decode_unicode(self):
        decoded = crypto.decode(self.base64)
        self.assertMultiLineEqual(self.plain, decoded)

    def test_decode_incorrectBase64Padding(self):
        with self.assertRaises(Exception) as ctx:
            crypto.decode('AA')
        self.assertEqual(str(ctx.exception),
            "Incorrect padding")

    def test_decode_nonBase64Chars(self):
        with self.assertRaises(UnicodeError) as ctx:
            crypto.decode('AB//')
        errormsg = str(ctx.exception)
        # Py2 does not have hyphen
        errormsg = errormsg.replace('utf8', 'utf-8')
        self.assertEqual(errormsg,
            "'utf-8' codec can't decode byte 0xff "
            "in position 2: invalid start byte")

    def test_sign(self):
        signature = crypto.sign(self.key, self.plain)
        self.assertMultiLineEqual(signature, self.signed)

    def test_sign_withNoPrivate_fails(self):
        with self.assertRaises(TypeError) as ctx:
            crypto.sign(self.public, self.plain)
        self.assertIn(ctx.exception.args[0], [
            "No private key", #  Py3
            "Private key not available in this object", # Py2
            ])

    def test_isAuthentic_whenOk(self):
        result = crypto.isAuthentic(self.public, self.plain, self.signed)
        self.assertTrue(result)

    def test_isAuthentic_whenPayloadChanged(self):
        badPayload = "this is NOT the content\n"
        result = crypto.isAuthentic(self.public, badPayload, self.signed)
        self.assertFalse(result)

class CryptoUnicode_Test(Crypto_Test):

    plain = u"ñáéíóúç\n"
    base64 = u"w7HDocOpw63Ds8O6w6cK"
    signed = (
        "H-4O0KH70jaYshXHcmROBZW09wCpsHb_gbaCrmnxbm3pdV3XYDRwLkY_YmPTab"
        "TizhImcwMCFO-MI4d9dQprS-tbb28hx5xlxZhHhYusSoTkDqMgjjPLBD_WjNvh"
        "aLc2FnRtYwiq4Mk6_OC94wD_zWlrMmAhPE7mQvLROSj1f9s-2HF3gtpfz2qfVo"
        "rwfQR5NfuMVbsuNSEBlgVSUytjShmGLwNIjAQHLVZCrGe5T3oSieHVD1rq2W5n"
        "TC_veaatz7M8UZ5UeqfcS-bzISA0mvOVfeuNZ4UkEgGMGtz7SMCps6qVIyN3UN"
        "iyWKxUpB0Pswa4Xj-iXSk1Po3GnfQWJQ=="
        )



unittest.TestCase.__str__ = unittest.TestCase.id



if __name__ == "__main__":
    import sys
    unittest.main()


# vim: ts=4 sw=4 et
