import pytest

from lottery_core.classes.ticket_validator import TicketValidator


def test_TicketValidator():
    numbers = list(range(1, 11))
    obj = TicketValidator(numbers)

    assert obj.has_valid_number(8)

    obj.remove_number(10)
    assert not obj.has_valid_number(10)

    obj.remove_number_list([1, 2, 4, 5])
    assert obj.serial_numbers_valid == [3, 6, 7, 8, 9]


def test_TicketValidator_ring_mode():
    obj = TicketValidator([])
    with pytest.raises(Exception):
        obj.get_next_valid_number_ring_mode(1)

    numbers = list(range(1, 11))
    obj = TicketValidator(numbers)

    obj.remove_number(5)
    assert obj.get_next_valid_number_ring_mode(5) == 6
    assert obj.get_past_valid_number_ring_mode(5) == 4

    assert obj.get_next_valid_number_ring_mode(11) == 1
    assert obj.get_past_valid_number_ring_mode(-1) == 10

    assert obj.get_next_valid_number_ring_mode(10) == 1
    assert obj.get_past_valid_number_ring_mode(1) == 10

    assert obj.get_next_valid_number_ring_mode(8) == 9
    assert obj.get_past_valid_number_ring_mode(8) == 7
