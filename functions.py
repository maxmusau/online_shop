import bcrypt

def password_hash(password):
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    print("Bytes ", bytes)
    print("Salt ", salt)
    print("Hash ", hash.decode())
    return hash.decode()
password_hash("nairobi")
# what is the hashed password

def password_verify(input_password, hash):
    userBytes = input_password.encode()
    result = bcrypt.checkpw(userBytes, hash.encode())
    print("Status ", result)
    return result

def decrypt(data):
    key = load_key()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(data)
    print("Decrypted ", decrypted_data.decode())
    return decrypted_data.decode()

def encrypt(data):
    key = load_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    print("Before Encr", data)
    print("After Encr ", encrypted_data.decode())
    return encrypted_data.decode()

from cryptography.fernet import  Fernet
def write_key():
    key = Fernet.generate_key()
    with open('key.key', "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("key.key", "rb").read()

