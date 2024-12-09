from dotenv import load_dotenv
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Load environment variables from the .env file
load_dotenv()

# Now you can access your environment variables
aes_key = os.getenv("NOT_MY_KEY")
if aes_key is None:
    print("Error: NOT_MY_KEY is not set.")
else:
    aes_key = aes_key.encode("utf-8")
    
    # Ensure the AES key length is valid for AES-256 (32 bytes)
    key_length = 32  # for AES-256
    if len(aes_key) < key_length:
        # If the key is too short, pad it with null bytes (you could use other padding schemes)
        aes_key = aes_key.ljust(key_length, b'\0')
    elif len(aes_key) > key_length:
        # If the key is too long, truncate it to the correct length
        aes_key = aes_key[:key_length]

    print(f"Using AES key: {aes_key}")
    
    # Now you can use the key for encryption or decryption
    # Example: Encrypting some data using AES in CBC mode
    data = b"Some data to encrypt"
    
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    print(f"Encrypted data: {ciphertext.hex()}")
