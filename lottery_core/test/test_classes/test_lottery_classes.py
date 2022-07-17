from lottery_core.classes.lottery_classes import LotteryParticipantRawData, LotteryParticipantProcessedData, \
    get_lottery_participants_processed_data_list, \
    get_lottery_participants_processed_data_sha256
from lottery_core.classes.winning_ticket_generators import WinningTicketGenerator_uint32
from lottery_core.lottery_lib import random_string_generator


def get_test_WTGuint32():
    return WinningTicketGenerator_uint32(server_seed='123', btc_block_hash='123')


def get_random_participant_data(user_id, num_tickets: int):
    uniq = random_string_generator(5)
    rand_str = random_string_generator(5)
    return LotteryParticipantRawData(user_id, uniq, rand_str, num_tickets)


def test_LotteryParticipantRawData():
    obj = LotteryParticipantRawData(1, '123', '123', 3)
    str_list = obj.ticket_strings
    hashes_list = obj.ticket_hashes_sha256

    assert str_list[0].endswith('1')
    assert str_list[2].endswith('3')
    assert isinstance(hashes_list, list)
    assert len(hashes_list) == 3


def test_LotteryParticipantProcessedData():
    obj = LotteryParticipantProcessedData(user_id=1, ticket_numbers=(8, 10))
    assert obj.tickets_count == 2
    assert obj.has_ticket_with_number(10)
    assert not obj.has_ticket_with_number(-1)


def test_get_lottery_participants_processed_data_sha256():
    raw_data_user1 = LotteryParticipantRawData(user_id=1, unique_str='123', mutable_str='123', num_tickets=2)
    raw_data_user2 = LotteryParticipantRawData(user_id=4, unique_str='55', mutable_str='23', num_tickets=3)

    hashes_list = sorted(raw_data_user1.ticket_hashes_sha256 + raw_data_user2.ticket_hashes_sha256)

    serial_numbers_user1 = []
    for hh in raw_data_user1.ticket_hashes_sha256:
        serial_numbers_user1.append(hashes_list.index(hh))

    processed = get_lottery_participants_processed_data_sha256(raw_participant_data=raw_data_user1,
                                                               ordered_ticket_hashes=hashes_list)

    assert processed.tickets_count == 2
    assert set(processed.ticket_serial_numbers) == set(serial_numbers_user1)


def test_get_lottery_participants_processed_data_list():
    raw_data = [LotteryParticipantRawData(user_id=1, unique_str='123', mutable_str='123', num_tickets=2),
                LotteryParticipantRawData(user_id=4, unique_str='55', mutable_str='23', num_tickets=3)]
    result = get_lottery_participants_processed_data_list(raw_data)
    for ii in result:
        assert isinstance(ii, LotteryParticipantProcessedData)
