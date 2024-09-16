class Transaction:
    def __init__(
        self, offset_name, transaction_date, credit, transaction_details, source
    ):
        self.transaction_date = transaction_date
        self.credit = credit
        self.transaction_details = transaction_details
        self.offset_name = offset_name
        self.source = source

    def to_dict(self):
        return {
            "offset_name": self.offset_name,
            "transaction_date": self.transaction_date,
            "credit": self.credit,
            "transaction_details": self.transaction_details,
            "source": self.source,
        }
