import struct

"""
Credit for decode section of this script to kerrickstaley/parse_serato_crates.py 
- https://gist.github.com/kerrickstaley/8eb04988c02fa7c62e75c4c34c04cf02
"""


def decode_struct(data):
    ret = []
    i = 0
    while i < len(data):
        tag = data[i:i + 4].decode('ascii')
        length = struct.unpack('>I', data[i + 4:i + 8])[0]
        value = data[i + 8:i + 8 + length]
        value = decode(value, tag=tag)
        ret.append((tag, value))
        i += 8 + length
    return ret


def decode_unicode(data):
    return data.decode('utf-16-be')


def decode_unsigned(data):
    return struct.unpack('>I', data)[0]


def noop(data):
    return data


DECODE_FUNC_FULL = {
    None: decode_struct,
    'vrsn': decode_unicode,
    'sbav': noop,
}

DECODE_FUNC_FIRST = {
    'o': decode_struct,
    't': decode_unicode,
    'p': decode_unicode,
    'u': decode_unsigned,
    'b': noop,
}


def decode(data, tag=None):
    if tag in DECODE_FUNC_FULL:
        decode_func = DECODE_FUNC_FULL[tag]
    else:
        decode_func = DECODE_FUNC_FIRST[tag[0]]

    return decode_func(data)


def load_crate(file_ame):
    with open(file_ame, 'rb') as f:
        return decode(f.read())


"""
Thanks again to kerrickstaley
"""


def encode_struct(data):
    ret = b''
    for tag, value in data:
        ret += encode(value, tag=tag)
    return ret


def encode_unicode(text):
    return text.encode('utf-16-be')


def encode_unsigned(num):
    return struct.pack('>I', num)


def noop(data):
    return data


ENCODE_FUNC_FULL = {
    'vrsn': encode_unicode,
    'sbav': noop,
}

ENCODE_FUNC_FIRST = {
    'o': encode_struct,
    't': encode_unicode,
    'p': encode_unicode,
    'u': encode_unsigned,
    'b': noop,
}


def encode(data, tag=None):
    if tag in ENCODE_FUNC_FULL:
        encode_func = ENCODE_FUNC_FULL[tag]
    else:
        encode_func = ENCODE_FUNC_FIRST[tag[0]]

    encoded_data = encode_func(data)
    length = len(encoded_data)
    return tag.encode('ascii') + struct.pack('>I', length) + encoded_data


def save_crate(crate, file_ame):
    with open(file_ame, 'wb+') as f:
        f.write(encode_struct(crate))
