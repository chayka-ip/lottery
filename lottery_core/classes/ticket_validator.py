class TicketValidator:
    def __init__(self, serial_numbers_valid: list):
        self.serial_numbers_valid = sorted(serial_numbers_valid)

    def has_valid_number(self, serial_number: int):
        return serial_number in self.serial_numbers_valid

    def remove_number(self, serial_number: int):
        if serial_number in self.serial_numbers_valid:
            self.serial_numbers_valid.remove(serial_number)

    def remove_number_list(self, number_list: list):
        for ii in number_list:
            self.remove_number(ii)

    @property
    def has_valid_tickets(self):
        return not self.serial_numbers_valid  == []

    def get_this_or_next_valid_number(self, serial_number: int):
        if self.has_valid_number(serial_number):
            return serial_number
        else:
            return self.get_next_valid_number_ring_mode(serial_number)

    def get_next_valid_number_ring_mode(self, serial_number: int):
        return self._get_nearby_valid_number_ring_mode(serial_number=serial_number, get_next=True)

    def get_past_valid_number_ring_mode(self, serial_number: int):
        return self._get_nearby_valid_number_ring_mode(serial_number=serial_number, get_next=False)

    def _get_nearby_valid_number_ring_mode(self, serial_number: int, get_next=True):
        """ring mode means that first element follows after last in forward direction
            and last follows after first in backward direction
        """
        if not self.has_valid_tickets:
            raise Exception

        first = self.serial_numbers_valid[0]
        last = self.serial_numbers_valid[-1]

        if get_next:
            if serial_number >= last:
                return first
            for ii in self.serial_numbers_valid:
                if ii > serial_number:
                    return ii
        else:
            if serial_number <= first:
                return last
            for ii in self.serial_numbers_valid[::-1]:
                if ii < serial_number:
                    return ii

