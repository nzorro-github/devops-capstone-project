"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    def test_list_all_accounts(self):
        """It should send a list of dict of all existing accounts"""
        
        # creates 3 accounts
        accounts = []
        for i in range(3):
            accounts.append(AccountFactory())
        
        response = self.client.post(
              BASE_URL,
              json=accounts[0].serialize(),
              content_type="application/json"
            )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get('/accounts')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_accounts = response.get_json()
        self.assertEqual(len(returned_accounts), 1)
        self.assertEqual(accounts[0].name, returned_accounts[0]['name'])
        self.assertEqual(accounts[0].phone_number, returned_accounts[0]['phone_number'])

        # create remaining accounts
        for i in range(1,3):
            response = self.client.post(
              BASE_URL,
              json=accounts[i].serialize(),
              content_type="application/json"
            )
        
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            response = self.client.get('/accounts')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            returned_accounts = response.get_json()
            self.assertEqual(len(returned_accounts), i+1)

            for acc in returned_accounts:
                account = Account.find(acc['id'])
                self.assertIsNotNone(account)
                self.assertEqual(account.name, acc['name'])
                self.assertEqual(account.email, acc['email'])
                self.assertEqual(account.phone_number, acc['phone_number'])


    def test_read_accounts(self):
            """It should respond with a json of the account with given id"""
            
            # creates 1 account
            account = AccountFactory()
            
            response = self.client.post(
                BASE_URL,
                json=account.serialize(),
                content_type="application/json"
                )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            response = self.client.get("/accounts")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected_account = response.get_json()[0] # there is only one
            self.assertIsNotNone(expected_account)

            response = self.client.get(f"/accounts/{expected_account['id']}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Checks for inexistent id
            response = self.client.get(f"/accounts/2023")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
