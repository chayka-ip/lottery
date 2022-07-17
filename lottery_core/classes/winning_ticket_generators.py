from lottery_core.lottery_lib import get_winning_ticket_uint32


class WinningTicketGenerator_uint32:
    def __init__(self, server_seed: str, btc_block_hash: str):
        self.server_seed = server_seed
        self.btc_block_hash = btc_block_hash
        self.__validate()

    def __validate(self):
        assert self.server_seed
        assert self.btc_block_hash

    def get_winning_source_string(self, winning_position: int):
        assert winning_position >= 0
        return f'{self.server_seed}:{self.btc_block_hash}:{winning_position}'

    def get_winning_ticket(self, winning_position: int, num_tickets: int):
        winning_string = self.get_winning_source_string(winning_position)
        return get_winning_ticket_uint32(num_tickets=num_tickets, string_to_hash=winning_string)
        
        
class WinningTicketGenerator2_uint32(WinningTicketGenerator_uint32):
    def __init__(self, server_seed: str, btc_block_hash: str, participant_list_hash: str):
        super().__init__(server_seed, btc_block_hash)
        self.participant_list_hash = participant_list_hash
        self.__validate()

    def __validate(self):
        super().__validate()
        assert self.participant_list_hash

    def get_winning_source_string(self, winning_position: int):
        assert winning_position >= 0
        return f'{self.server_seed}:{self.participant_list_hash}:{self.btc_block_hash}:{winning_position}'

