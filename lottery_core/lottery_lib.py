from hashlib import sha256
from math import floor
import string
import random


# Ticket number range 0...4 294 967 295 [uint32]. One ticket wins only one prize
MAX_TICKET_COUNT = 4294967296
MAX_TICKET_NUMBER = MAX_TICKET_COUNT - 1


def random_string_generator(char_num: int, chars=string.ascii_letters + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(char_num))


def char_to_hex(s: str, strip_x=False):
    code = ord(s)
    if strip_x:
        return format(code, 'x')
    else:
        return hex(code)


def hex_sha256_from_string(s: str):
    return sha256(str.encode(s)).hexdigest()


def bytes_sha256_from_string(s: str):
    return sha256(str.encode(s)).digest()


def str_len_64_select_elements(sequence, num_to_select: int):
    seq_length = len(sequence)

    if num_to_select == 0 or not seq_length == 64 or not seq_length % num_to_select == 0:
        raise ValueError

    mul = int(seq_length / num_to_select)

    out_list = []
    for i in range(num_to_select):
        ind = i * mul
        out_list.append(sequence[ind])

    return tuple(out_list)


def get_uint32_from_str_len_4(s: str):
    """
     abcd is 0x61 0x62 0x63 0x64
     then value is 0x64636261 == 1684234849
    """

    if not len(s) == 4:
        raise ValueError

    char_hex_list = [char_to_hex(i, strip_x=True) for i in s]
    merged_hex = ''.join(reversed(char_hex_list))
    return int(merged_hex, 16)


def get_winning_ticket_uint32(num_tickets: int, string_to_hash: str):
    if num_tickets == 1:
        return 0

    if not 1 < num_tickets <= MAX_TICKET_NUMBER or not string_to_hash:
        raise ValueError

    hashed_hex = hex_sha256_from_string(string_to_hash)

    # generate string from hash; each char will be treated as byte further
    num_characters_to_select = 4
    selected_data = str_len_64_select_elements(
        hashed_hex, num_characters_to_select)
    selected_string = ''.join(selected_data)

    num1 = get_uint32_from_str_len_4(selected_string)

    # round down
    return floor(num_tickets * num1 / MAX_TICKET_NUMBER)
