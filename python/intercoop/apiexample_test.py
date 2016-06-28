# -*- encoding: utf-8 -*-

import unittest
import os
import shutil
from yamlns import namespace as ns
from . import crypto
from . import apiexample
from . import packaging
from . import unsecuredatastorage

class KeyRingMock(object):
    def __init__(self, keys):
        self.keys = keys
    def get(self, key):
        return self.keys[key]

class ExampleApi_Test(unittest.TestCase):

    yaml=u"""\
intercoopVersion: '1.0'
originpeer: testpeer
origincode: 666
name: Perico de los Palotes
address: Percebe, 13
city: Villarriba del Alcornoque
state: Albacete
postalcode: '01001'
country: ES
"""

    def setUp(self):
        self.keyfile = 'testkey.pem'
        self.pubfile = 'testkey-public.pem'
        self.key = crypto.loadKey(self.keyfile)
        self.pub = crypto.loadKey(self.pubfile)
        self.keyring = KeyRingMock(dict(
            testpeer=self.pub,
            ))

        self.datadir='apiexamplestorage'
        try: os.makedirs(self.datadir)
        except: pass
        self.storage = unsecuredatastorage.DataStorage(self.datadir)

        app = apiexample.IntercoopApi('testapi', self.storage, self.keyring).app

        app.config['TESTING'] = True
        self.client = app.test_client()

    def cleanUp(self):
        try:
            shutil.rmtree(self.datadir)
        except: pass
        
    def tearDown(self):
        self.cleanUp()


    def test__protocolVersion_get(self):
        r = self.client.get('/protocolVersion')
        self.assertEqual(
            ns.loads(r.data),
            ns(protocolVersion=packaging.protocolVersion),
            )

    def test__peermember_post__ok(self):
        g = packaging.Generator(self.key)
        data = ns.loads(self.yaml)
        package = g.produce(data)

        r = self.client.post('/peermember', data=package)

        data = ns.loads(r.data)
        self.assertEqual(r.status_code, 200)
        self.assertRegex(data.uuid, '^[0-9a-f\-]+$')

    def test__peermember_post__badPeer(self):
        g = packaging.Generator(self.key)
        data = ns.loads(self.yaml)
        data.originpeer = 'badpeer'
        package = g.produce(data)

        r = self.client.post('/peermember', data=package)

        self.assertEqual(r.status_code, 403)
        self.assertEqual(ns.loads(r.data), ns(
            error = 'BadPeer',
            message = "The entity 'badpeer' is not a recognized one",
            ))

    def test__peermember_post__badSignature(self):
        g = packaging.Generator(self.key)
        data = ns.loads(self.yaml)
        package = ns.loads(g.produce(data))
        package.payload = crypto.encode(self.yaml+'\n')
        package = package.dump()

        r = self.client.post('/peermember', data=package)

        self.assertEqual(ns.loads(r.data), ns(
            error = 'BadSignature',
            message = "Signature verification failed, untrusted content",
            ))
        self.assertEqual(r.status_code, 403)

    def test__peermember_post__missingField(self):
        g = packaging.Generator(self.key)
        data = ns.loads(self.yaml)
        del data.originpeer
        package = g.produce(data)

        r = self.client.post('/peermember', data=package)

        self.assertEqual(ns.loads(r.data), ns(
            error = 'MissingField',
            message = "Required field 'originpeer' missing on the payload",
            ))
        self.assertEqual(r.status_code, 400)

    def test__peermember_get(self):
        values = ns.loads(self.yaml)
        uuid = self.storage.store(values)

        data = ns(uuid=uuid)

        r = self.client.get('/peermember/{}'.format(uuid))

        self.assertEqual(ns.loads(r.data), values)
        self.assertEqual(r.status_code, 200)

    def test__peermember_get__notFound(self):
        uuid = '01020304-0506-0708-090a-0b0c0d0e0f10'
        data = ns(uuid=uuid)

        r = self.client.get('/peermember/{}'.format(uuid))

        self.assertEqual(ns.loads(r.data), ns(
            error = 'NoSuchUuid',
            message = "No personal data available for uuid "
                "'01020304-0506-0708-090a-0b0c0d0e0f10'",
            ))
        self.assertEqual(r.status_code, 404)



# vim: ts=4 sw=4 et