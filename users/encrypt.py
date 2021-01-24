from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import base64
import sys, json, os

def generate_keys():
	try:
		key = RSA.generate(4096)
		privkey = key.exportKey()
		pubkey = key.publickey().exportKey()
		f = open(os.path.dirname(os.path.abspath(__file__)) + "/private_key.pem","w")
		f.write(privkey)
		f.close()

		f = open(os.path.dirname(os.path.abspath(__file__)) + "/public_key.pem","w")
		f.write(pubkey)
		f.close()
	except Exception as e:
		raise e

def encrypt_message(msg):
	try:
		f = open(os.path.dirname(os.path.abspath(__file__)) + "/public_key.pem","r")
		rsa_key = RSA.importKey(f.read())
		f.close()
		cipher = PKCS1_v1_5.new(rsa_key)
		cipherText = base64.b64encode(cipher.encrypt(msg))
		return cipherText
	except Exception as e:
		return None

def main():
	inp = sys.argv[1]
	if inp == "generate":
		generate_keys()
	if inp == "encrypt":
		inp2 = sys.argv[2]
		print(encrypt_message(inp2))

if __name__ == "__main__":
	main()
