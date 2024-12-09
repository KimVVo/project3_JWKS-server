import unittest
import threading
import requests
from datetime import datetime, timezone
import json

# Import the server code here
from JWKS import app, get_db_connection, hostName, serverPort

class TestHTTPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize the database and start the Flask app server"""
        get_db_connection()  # Ensure DB connection is initialized
        cls.server_thread = threading.Thread(target=app.run, kwargs={'host': hostName, 'port': serverPort, 'debug': False})
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        """Shut down the Flask server"""
        # Flask server should shut down gracefully. Ensure your app can handle this.
        requests.post(f"http://{hostName}:{serverPort}/shutdown")
        cls.server_thread.join()

    def test_jwks_endpoint(self):
        """Test the JWKS endpoint to verify JSON Web Key Set is returned"""
        url = f"http://{hostName}:{serverPort}/.well-known/jwks.json"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        keys = response.json()
        self.assertIn("keys", keys)
        self.assertGreater(len(keys["keys"]), 0)

    def test_auth_endpoint(self):
        """Test the authentication endpoint"""
        url = f"http://{hostName}:{serverPort}/auth"
        
        # Use valid credentials as defined in the auth route
        data = {
            "username": "test_user",  # Make sure this matches a valid username in the DB
            "password": "test_password"  # Make sure this is the correct password
        }

        response = requests.post(url, json=data)

        # Check that the response code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the response has the correct structure
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Authentication successful")

    def test_auth_endpoint_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        url = f"http://{hostName}:{serverPort}/auth"
        data = {
            "username": "wrong_user",
            "password": "wrong_password"
        }
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Invalid credentials")

    def test_store_private_key(self):
        """Test storing a private key endpoint"""
        url = f"http://{hostName}:{serverPort}/store_private_key"
        data = {
            "private_key": "my_secret_key"
        }
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Private key stored securely.")

    def test_retrieve_private_key(self):
        """Test retrieving a private key endpoint"""
        url = f"http://{hostName}:{serverPort}/get_private_key"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("private_key", response_data)
        self.assertEqual(response_data["private_key"], "my_secret_key")

    def test_invalid_methods(self):
        """Test invalid methods (PUT, PATCH, DELETE) for /auth endpoint"""
        url = f"http://{hostName}:{serverPort}/auth"
        methods = ["PUT", "PATCH", "DELETE", "HEAD"]
        for method in methods:
            response = requests.request(method, url)
            self.assertEqual(response.status_code, 405)

if __name__ == "__main__":
    unittest.main()
