from lottery_core.classes.lottery_classes import LotteryParticipantProcessedData
from lottery_core.classes.ticket_validator import TicketValidator
from lottery_core.classes.winning_ticket_generators import WinningTicketGenerator_uint32


class WinnerData:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.winning_tickets = []

    def add_winning_ticket(self, serial_number: int):
        assert serial_number not in self.winning_tickets
        self.winning_tickets.append(serial_number)

    @property
    def winning_tickets_count(self):
        return len(self.winning_tickets)


class WinnerDataHolder:
    def __init__(self):
        self.winners_dict = {}  # {id: WinnerData}
        self.winner_tickets_fifo_list: list = []

    def add_winner(self, obj: WinnerData):
        if obj:
            self.winners_dict[obj.user_id] = obj

    def add_winner_by_id(self, user_id: int):
        if user_id not in self.winners_dict:
            self.winners_dict[user_id] = WinnerData(user_id=user_id)

    def has_winner_with_id(self, user_id: int):
        return user_id in self.winners_dict

    def get_user_with_id(self, user_id: int):
        return self.winners_dict.get(user_id, None)

    def add_winning_ticket_to_fifo(self, serial_number: int):
        self.winner_tickets_fifo_list.append(serial_number)


class WinningProcessorBase:
    def __init__(self, participants_processed_data: list, winning_ticket_generator: WinningTicketGenerator_uint32):
        self.participants_processed_data = participants_processed_data
        self.winning_ticket_generator = winning_ticket_generator
        self.__validate()

    def __validate(self):
        assert self.winning_ticket_generator
        assert self.participants_processed_data
        for ii in self.participants_processed_data:
            assert isinstance(ii, LotteryParticipantProcessedData)

    def get_user_id_by_ticket(self, ticket_serial_number: int):
        for p in self.participants_processed_data:
            participant: LotteryParticipantProcessedData = p
            if participant.has_ticket_with_number(ticket_serial_number):
                return participant.user_id
        raise ValueError

    def get_user_by_id(self, user_id: int):
        for p in self.participants_processed_data:
            participant: LotteryParticipantProcessedData = p
            if participant.user_id == user_id:
                return participant

    @property
    def held_tickets_count(self):
        count = 0
        for p in self.participants_processed_data:
            participant: LotteryParticipantProcessedData = p
            count += participant.tickets_count
        return count

    def create_ticket_validator(self):
        serial_number_list = []
        for p in self.participants_processed_data:
            participant: LotteryParticipantProcessedData = p
            serial_number_list += participant.ticket_serial_number_list

        serial_number_list.sort()
        return TicketValidator(serial_numbers_valid=serial_number_list)


class WP_OneWinningUserOneTicket(WinningProcessorBase):
    def get_winners_data(self):
        tickets_count = self.held_tickets_count
        winning_ticket = self.winning_ticket_generator.get_winning_ticket(winning_position=1, num_tickets=tickets_count)
        winner_user_id = self.get_user_id_by_ticket(winning_ticket)

        winner_data = WinnerData(winner_user_id)
        winner_data.add_winning_ticket(winning_ticket)

        return winner_data


class WP_MultipleWinners(WinningProcessorBase):
    def get_winners_data(self, max_prizes_count: int, max_wins_per_user: int):
        assert max_prizes_count > 0
        assert 0 < max_wins_per_user <= max_prizes_count

        winner_data_holder = WinnerDataHolder()
        ticket_validator = self.create_ticket_validator()
        tickets_count = self.held_tickets_count

        wp_min = 1
        wp_max = max_prizes_count + 1

        for winning_position in range(wp_min, wp_max):
            assert ticket_validator.has_valid_tickets

            computed_winning_ticket = self.winning_ticket_generator.get_winning_ticket(
                winning_position=winning_position,
                num_tickets=tickets_count)

            winning_ticket = ticket_validator.get_this_or_next_valid_number(computed_winning_ticket)

            user_id = self.get_user_id_by_ticket(winning_ticket)
            participant_processed = self.get_user_by_id(user_id=user_id)
            assert participant_processed
            user_tickets = participant_processed.ticket_serial_number_list

            max_wins_per_user = max_wins_per_user
            apply_winning_ticket(user_id=user_id, user_tickets=user_tickets, ticket_validator=ticket_validator,
                                 winner_data_holder=winner_data_holder, winning_ticket=winning_ticket,
                                 max_wins_per_user=max_wins_per_user)

        return winner_data_holder


def apply_winning_ticket(user_id: int, user_tickets, ticket_validator: TicketValidator,
                         winner_data_holder: WinnerDataHolder, winning_ticket: int, max_wins_per_user: int):
    winner_data_holder.add_winning_ticket_to_fifo(winning_ticket)
    winner_data = winner_data_holder.get_user_with_id(user_id)
    if not winner_data:
        winner_data = WinnerData(user_id)
        winner_data_holder.add_winner(winner_data)

    winner_data.add_winning_ticket(winning_ticket)
    ticket_validator.remove_number(winning_ticket)

    if winner_data.winning_tickets_count >= max_wins_per_user:
        ticket_validator.remove_number_list(user_tickets)

# todo: add prize distribution
