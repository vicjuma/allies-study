from fastapi.testclient import TestClient
import unittest
from app import app

class ApplicationTestCases(unittest.TestCase):
    def setUp(self):
        self.testapp = TestClient(app)

    def tearDown(self):
        self.testapp = None


    def testUserCrud(self):
        pass

    def testTaskCrud(self):
        pass

    def testWorkerCrud(self):
        pass

    def testPaymentFuncs(self):
        pass


    def testAuthenticationUtils(self):
        pass


if __name__ == '__main__':
    unittest.main()
