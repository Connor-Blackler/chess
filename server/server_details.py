"""Details the server will host on"""

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 51542

def initial_digest_key() -> str:
    """the digest key used when sending the initial unique digest key to the client"""
    return "d6398aca-a3c0-4642-9867-3a7a3a64e704"
