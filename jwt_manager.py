from jwt import encode, decode

# Create a JWT token
def create_jwt_token(data: dict):
    token: str = encode(payload=data, key='my_secret_key', algorithm='HS256')
    return token

# Validate a JWT token
def validate_token(token: str) -> dict:
    data: dict = decode(token, 'my_secret_key', algorithms=['HS256'])
    return data