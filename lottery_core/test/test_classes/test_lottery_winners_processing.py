import pytest

from lottery_core.classes.lottery_classes import LotteryParticipantProcessedData, LotteryParticipantRawData, \
    get_lottery_participants_processed_data_list
from lottery_core.classes.lottery_winners_processing import WinnerData, WinnerDataHolder, WinningProcessorBase, \
    WP_OneWinningUserOneTicket, apply_winning_ticket, WP_MultipleWinners
from lottery_core.classes.ticket_validator import TicketValidator
from lottery_core.classes.winning_ticket_generators import WinningTicketGenerator_uint32
from lottery_core.test.test_classes.test_lottery_classes import get_test_WTGuint32


def test_WinnerData():
    obj = WinnerData(1)
    ticket_number = 123
    obj.add_winning_ticket(ticket_number)
    assert obj.winning_tickets == [ticket_number]


def test_WinnerDataHolder():
    holder = WinnerDataHolder()
    user1 = WinnerData(1)

    holder.add_winner(user1)
    holder.add_winner_by_id(1)
    assert holder.winners_dict[1] == user1

    assert holder.has_winner_with_id(1)
    assert not holder.has_winner_with_id(2)

    assert holder.get_user_with_id(1)
    assert not holder.get_user_with_id(2)

    user1.add_winning_ticket(2)
    user_obtained: WinnerData = holder.get_user_with_id(1)
    assert user_obtained.winning_tickets == [2]


def test_WinningProcessorBase():
    wtg = get_test_WTGuint32()
    participants_processed = [
        LotteryParticipantProcessedData(user_id=1, ticket_numbers=(2, 3)),
        LotteryParticipantProcessedData(user_id=2, ticket_numbers=(4, 5))
    ]

    obj = WinningProcessorBase(participants_processed_data=participants_processed, winning_ticket_generator=wtg)

    assert obj.get_user_id_by_ticket(3) == 1

    with pytest.raises(ValueError):
        assert obj.get_user_id_by_ticket(22)

    assert obj.held_tickets_count == 4


def test_WP_OneWinningUserOneTicket():
    tickets_per_user = 2

    participants = [
        LotteryParticipantRawData(user_id=1, unique_str='1', mutable_str='1', num_tickets=tickets_per_user),
        LotteryParticipantRawData(user_id=2, unique_str='2', mutable_str='1', num_tickets=tickets_per_user),
        LotteryParticipantRawData(user_id=3, unique_str='3', mutable_str='1', num_tickets=tickets_per_user),
    ]
    processed_participants_data = get_lottery_participants_processed_data_list(participants)

    winning_ticket_generator = WinningTicketGenerator_uint32(server_seed='1', btc_block_hash='1')
    winner_generator = WP_OneWinningUserOneTicket(participants_processed_data=processed_participants_data,
                                                  winning_ticket_generator=winning_ticket_generator)

    winners_data = winner_generator.get_winners_data()
    assert winners_data.user_id == 3
    assert winners_data.winning_tickets == [2]


def test_apply_winning_ticket():
    user_id = 1
    user_tickets = [1, 2, 3, 4, 5, 6]

    rest_tickets = [10, 11]
    all_tickets = user_tickets + rest_tickets

    ticket_validator = TicketValidator(all_tickets)
    winner_data_holder = WinnerDataHolder()
    winning_ticket_1 = 5
    winning_ticket_2 = 6
    max_wins_per_user = 2

    apply_winning_ticket(user_id=user_id, user_tickets=user_tickets, ticket_validator=ticket_validator,
                         winner_data_holder=winner_data_holder, winning_ticket=winning_ticket_1,
                         max_wins_per_user=max_wins_per_user)

    winner_user: WinnerData = winner_data_holder.get_user_with_id(user_id)

    assert winner_user.winning_tickets == [5]
    assert ticket_validator.serial_numbers_valid == [1, 2, 3, 4, 6, 10, 11]

    apply_winning_ticket(user_id=user_id, user_tickets=user_tickets, ticket_validator=ticket_validator,
                         winner_data_holder=winner_data_holder, winning_ticket=winning_ticket_2,
                         max_wins_per_user=max_wins_per_user)

    assert winner_user.winning_tickets == [5, 6]
    assert ticket_validator.serial_numbers_valid == rest_tickets


def test_WP_MultipleWinners():
    # EXAMPLE for 2 tickets per user

    # {1: ['aa3c0532b02b70f38f75a993261085eaec15435d87659bc4eb17d4bf5037de58',
    #      'b2b18caa50222ed850b395048fcdd1c0ce986e6e06da23a0a1965d395e229fd1'],
    #  2: ['a046d505cc645e8c77d65bd0e336a1dbf0217bd58c6f9ef5c7b87493abe59608',
    #      '6f231b6f802ef27e40dce87ae4234d9f8da11272c2ec07414632e7d9db9782da'],
    #  3: ['4d93145eb5dd7c3f1a0d64b57a2d37741c8903643c6ea898df40eac450324404',
    #      '89185ba943f25231805512ce23f3b9ba646cd104f80d04e4d7add8f117ff65d0']}

    #   N                                HASHES ORDERED                                USER
    #   0   ['4d93145eb5dd7c3f1a0d64b57a2d37741c8903643c6ea898df40eac450324404',        3
    #   1    '6f231b6f802ef27e40dce87ae4234d9f8da11272c2ec07414632e7d9db9782da',        2
    #   2    '89185ba943f25231805512ce23f3b9ba646cd104f80d04e4d7add8f117ff65d0',        3
    #   3    'a046d505cc645e8c77d65bd0e336a1dbf0217bd58c6f9ef5c7b87493abe59608',        2
    #   4    'aa3c0532b02b70f38f75a993261085eaec15435d87659bc4eb17d4bf5037de58',        1
    #   5    'b2b18caa50222ed850b395048fcdd1c0ce986e6e06da23a0a1965d395e229fd1']        1

    def _get_winner_data(max_prizes_count: int, max_wins_per_user: int):
        tickets_per_user = 2
        participants = [
            LotteryParticipantRawData(user_id=1, unique_str='1', mutable_str='1', num_tickets=tickets_per_user),
            LotteryParticipantRawData(user_id=2, unique_str='2', mutable_str='1', num_tickets=tickets_per_user),
            LotteryParticipantRawData(user_id=3, unique_str='3', mutable_str='1', num_tickets=tickets_per_user),
        ]
        participants = get_lottery_participants_processed_data_list(participants)
        wtg = WinningTicketGenerator_uint32(server_seed='1', btc_block_hash='1')

        wg = WP_MultipleWinners(participants_processed_data=participants, winning_ticket_generator=wtg)
        return wg.get_winners_data(max_prizes_count=max_prizes_count, max_wins_per_user=max_wins_per_user)

    with pytest.raises(AssertionError):
        _get_winner_data(max_prizes_count=0, max_wins_per_user=1)
    with pytest.raises(AssertionError):
        _get_winner_data(max_prizes_count=1, max_wins_per_user=0)
    with pytest.raises(AssertionError):
        _get_winner_data(max_prizes_count=7, max_wins_per_user=2)

    wd1 = _get_winner_data(max_prizes_count=1, max_wins_per_user=1)
    assert wd1.winner_tickets_fifo_list == [2]

    wd2 = _get_winner_data(max_prizes_count=2, max_wins_per_user=1)
    assert wd2.winner_tickets_fifo_list == [2, 1]

    wd3 = _get_winner_data(max_prizes_count=6, max_wins_per_user=2)
    assert set(wd3.winner_tickets_fifo_list) == set(range(6))
