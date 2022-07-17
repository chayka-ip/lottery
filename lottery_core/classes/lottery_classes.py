from lottery_core.classes.ticket_validator import TicketValidator
from lottery_core.classes.winning_ticket_generators import WinningTicketGenerator_uint32
from lottery_core.lottery_lib import hex_sha256_from_string


class LotteryData:
    def __init__(self, max_user_count: int, prize_fund: float, max_tickets_per_user: int, max_prizes_count: int,
                 max_wins_per_user: int):
        self.max_user_count = max_user_count
        self.prize_fund = prize_fund
        self.max_tickets_per_user = max_tickets_per_user
        self.max_prizes_count = max_prizes_count
        self.max_wins_per_user = max_wins_per_user

        self.__validate()

        # todo: add time stuff - when starts/ends and etc

    def __validate(self):
        assert self.max_user_count > 0
        assert self.prize_fund >= 0
        assert self.max_tickets_per_user > 0
        assert self.max_prizes_count > 0
        assert self.max_wins_per_user > 0
        assert self.max_wins_per_user <= self.max_tickets_per_user

    @property
    def tickets_sold(self):
        return

    @property
    def tickets_left(self):
        return

    @property
    def users_participating_count(self):
        return


class LotteryParticipantRawData:
    """unique_string - guarantees unique hashes being generated; generated once user is registered in the lottery """

    def __init__(self, user_id: int, unique_str: str, mutable_str: str, num_tickets: int):
        self.user_id = user_id
        self.unique_str = unique_str
        self.mutable_str = mutable_str
        self.num_tickets = num_tickets

        self.__validate()

    def __validate(self):
        assert self.user_id >= 0
        assert self.unique_str
        assert self.mutable_str
        assert self.num_tickets > 0

    @property
    def ticket_strings(self):
        out_data = []
        if self.num_tickets > 0:
            for ticket_number in range(1, self.num_tickets + 1):
                s = f'{self.unique_str}-{self.mutable_str}:{ticket_number}'
                out_data.append(s)
        return out_data

    @property
    def ticket_hashes_sha256(self):
        out_data = []
        for item in self.ticket_strings:
            s = hex_sha256_from_string(item)
            out_data.append(s)
        return out_data


class LotteryParticipantProcessedData:
    def __init__(self, user_id: int, ticket_numbers: tuple):
        self.user_id = user_id
        self.ticket_serial_numbers = ticket_numbers

        self.__validate()

    def __validate(self):
        assert self.user_id >= 0

    @property
    def tickets_count(self):
        return len(self.ticket_serial_numbers)

    def has_ticket_with_number(self, serial_number: int):
        return serial_number in self.ticket_serial_numbers

    @property
    def ticket_serial_number_list(self):
        return list(self.ticket_serial_numbers)


def get_lottery_participants_processed_data_sha256(raw_participant_data: LotteryParticipantRawData,
                                                   ordered_ticket_hashes: list):
    ticket_serial_numbers = []
    for hh in raw_participant_data.ticket_hashes_sha256:
        assert hh in ordered_ticket_hashes
        num = ordered_ticket_hashes.index(hh)
        ticket_serial_numbers.append(num)

    t = tuple(ticket_serial_numbers)
    return LotteryParticipantProcessedData(raw_participant_data.user_id, t)


def get_lottery_participants_processed_data_list(lottery_participants_raw_data: list):
    for ii in lottery_participants_raw_data:
        if not isinstance(ii, LotteryParticipantRawData):
            raise ValueError

    # each hash represents serial ticket number
    ticket_hashes_ordered = []
    for user in lottery_participants_raw_data:
        ticket_hashes_ordered += user.ticket_hashes_sha256
    ticket_hashes_ordered.sort()

    processed_data = []
    for user in lottery_participants_raw_data:
        processed_user = get_lottery_participants_processed_data_sha256(user, ticket_hashes_ordered)
        processed_data.append(processed_user)

    return processed_data
