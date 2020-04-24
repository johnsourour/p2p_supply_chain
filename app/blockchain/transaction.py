
class Transaction:
  SEND_MONEY    = 'send_money'
  OFFER         = 'offer'
  PURCHASE      = 'purchase'
  VERIFICATION  = 'verification'
  UNDEFINED     = 'undefined'

  def __init__(self, data):
    self.data = data or {}

  @property
  def get_type(self):
    """
    type of the transaction - send_money, offer, verification, undefined
    """
    return self.data.get('type', Transaction.UNDEFINED)


  @property
  def from_account(self):
    return self.data.get('from_account', '')

  @property
  def to_account(self):
    return self.data.get('to_account', '')

  @property
  def get_content(self):
    return self.data.get('content', '')

  @property
  def amount(self):
    return float(self.data.get('amount', 0))

  def is_linked(self, account_id):
    return self.from_account == account_id or self.to_account == account_id

  def is_offer(self):
    global OFFER
    return self.get_type() == OFFER


class TransactionList:
  def __init__(self, account_id, transactions):
    """
    transactions - the list of transactions as dict
    """
    self.account_id = account_id
    self.transactions = [tx for tx in transactions if Transaction(tx).is_linked(account_id)]

  @property
  def balance(self):
    amount = 0.0
    for _tx in self.transactions:
      tx = Transaction(_tx)
      amount += -tx.amount if tx.from_account == self.account_id else tx.amount
    return amount
