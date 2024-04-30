from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from dashboard.lib.log_color import log
# Assume these are the same key and IV used in MicroPython
key = b'\xc8\xdd\x8f\xb8\xa6\xcc\xf7f\xdc\x18\xf0\xab\xba\xff\x1aO'  # 16 bytes key
IV = b'\x15\xfe\xb4\xbf\xab\xd4\xfe\x13\xefki\xd2\x9a\xabf\x15'



def aes_decode(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, IV)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data

# Initialize cipher


# Assume 'encrypted_data' is the ciphertext received
if __name__ == "__main__":
    encrypted_data = b'\x9cr\xfa"28p\xba\xb9\xd9\xdc\'\xe5%\x19vD\x17\xff\xa2\x9fYBe\n\xcfPk]!\xa3\x9d'
    k=aes_decode(encrypted_data)
    print("解码:",k)
    try:

        print(k.decode())
    except Exception as e:
        log.error(f"错误: {e}")

