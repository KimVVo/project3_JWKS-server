import unittest
import json
from JWKS import create_app, get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        with self.app.app_context():
            conn = get_db_connection()
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL,
                            email TEXT UNIQUE,
                            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS keys (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            private_key BLOB NOT NULL)''')
            conn.commit()
            conn.close()

    def tearDown(self):
        self.app_context.pop()

    def test_register_user(self):
        response = self.client.post('/register', json={'username': 'testuser', 'email': 'test@example.com'})
        logging.debug(response.data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('password', data)

    def test_store_private_key(self):
        response = self.client.post('/store_private_key', json={'private_key': 'my_secret_key'})
        logging.debug(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Private key stored securely.')

    def test_retrieve_private_key(self):
        self.client.post('/store_private_key', json={'private_key': 'my_secret_key'})
        response = self.client.get('/get_private_key')
        logging.debug(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['private_key'], 'my_secret_key')

    def test_authentication(self):
        self.client.post('/register', json={'username': 'testuser', 'email': 'test@example.com'})
        response = self.client.post('/auth', json={'username': 'testuser', 'password': 'testpassword'})
        logging.debug(response.data)
        self.assertEqual(response.status_code, 401)  # Should fail since password is randomly generated

if __name__ == '__main__':
    unittest.main()
