import pytest

from lottery_core.lottery_lib import char_to_hex, hex_sha256_from_string, str_len_64_select_elements, \
    get_uint32_from_str_len_4, get_winning_ticket_uint32


def test_char_to_hex():
    assert char_to_hex('s') == '0x73'
    assert char_to_hex('s', True) == '73'
    assert not char_to_hex('d', True) == '73'


def test_hex_sha256_from_string():
    s = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
    assert hex_sha256_from_string('123') == s


def test_str_len_64_select_elements():
    str_64_len = hex_sha256_from_string('123')
    hashed = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'

    r1 = str_len_64_select_elements(str_64_len, 1)
    assert r1 == ('a',)

    r2 = str_len_64_select_elements(str_64_len, 2)
    assert r2 == ('a', 'a')

    r4 = str_len_64_select_elements(str_64_len, 4)
    assert r4 == ('a', '4', 'a', '9')

    assert str_len_64_select_elements(str_64_len, 64) == tuple(hashed)

    with pytest.raises(ValueError):
        assert str_len_64_select_elements(str_64_len, 0)
        assert str_len_64_select_elements(str_64_len, 65)
        assert str_len_64_select_elements(str_64_len, 7)
        assert str_len_64_select_elements('', 4)


def test_get_uint32_from_str_len_4():
    s = 'abcd'
    assert get_uint32_from_str_len_4(s) == 1684234849


def test_get_winning_ticket_uint32():
    num_tickets = 25
    s = '12345'
    r1 = get_winning_ticket_uint32(num_tickets, s)
    r2 = get_winning_ticket_uint32(1, '111')
    assert r1 == 9
    assert r2 == 0

    with pytest.raises(ValueError):
        assert get_winning_ticket_uint32(5, '')
        assert get_winning_ticket_uint32(4294967295 + 1, '123')
