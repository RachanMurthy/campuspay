import random
import string
import json

def generate_random_string(length=32):
    """Generate a random string of alphanumeric characters of a given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def json_dump_file(path, filename, content):
        with open(path + filename, 'w') as keyfile:
            json.dump(content, keyfile)

def json_read_file(path, filename):
     with open(path + filename, 'r') as keyfile:
        encrypted_key = json.load(keyfile)
        return encrypted_key