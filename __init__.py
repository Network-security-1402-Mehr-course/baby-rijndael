from .baby_rijndael import BabyRijndael

BLOCK_SIZE = 2
KEY_SIZE = BLOCK_SIZE

def bytes_to_state(b: bytes) -> BabyRijndael.State:
    assert len(b) == BLOCK_SIZE
    return [[b[i]//16, b[i]%16] for i in range(BLOCK_SIZE)]

def state_to_bytes(s: BabyRijndael.State) -> bytes:
    return bytes(s[i][0]*16 + s[i][1] for i in range(BLOCK_SIZE))

def encrypt(plain: bytes, key: bytes) -> bytes:
    br = BabyRijndael(bytes_to_state(plain), bytes_to_state(key))
    br.encrypt()
    return state_to_bytes(br.state)

def decrypt(cipher: bytes, key: bytes) -> bytes:
    br = BabyRijndael(bytes_to_state(cipher), bytes_to_state(key))
    br.decrypt()
    return state_to_bytes(br.state)
