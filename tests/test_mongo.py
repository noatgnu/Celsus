import motor
from tornado import gen
from tornado.escape import json_encode, json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.testing import AsyncTestCase, gen_test
from io import BytesIO, StringIO


client = motor.motor_tornado.MotorClient("mongodb://root:mongo-celsus@localhost/")
db = client.college

class TestMongo(AsyncTestCase):
    @gen_test
    def test_mongo(self):
        test = yield db["test-table"].find_one({
            "_id": "1"
        })
        print(test)
        d = yield db["test"].insert_one({"id": "213124123", "value": "2412516124125215"})
        found = yield db["test"].find_one({"id": "213124123"})
        print(found)
