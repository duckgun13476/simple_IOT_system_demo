import mpyaes

# Generate key and IV


# Create AES cipher object


# Encrypt a message

def aes_encode(message = "message"):
    key = b'\xc8\xdd\x8f\xb8\xa6\xcc\xf7f\xdc\x18\xf0\xab\xba\xff\x1aO'  # 16 bytes key
    IV = b'\x15\xfe\xb4\xbf\xab\xd4\xfe\x13\xefki\xd2\x9a\xabf\x15'
    aes = mpyaes.new(key, mpyaes.MODE_CBC, IV)
    
    ciphertext = bytes(aes.encrypt(message))
    #print(ciphertext)
    return ciphertext

#print(aes_encode(message="-ID-{0}T{1:.2f}H{2:.1f}BP{3:.3f}W{4}A{5:.3f}L{6:.1f}R{7:.2f}V{8:.2f}E{9:.1f}CT{10:.2f}P{11:.2f}I{12:.2f}D{13:.2f}S{14:.2f}"))