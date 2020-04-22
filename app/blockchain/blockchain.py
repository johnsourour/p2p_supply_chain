from hashlib import sha256
import json
import time

from .transaction import TransactionList, OffersList, Transaction
from .smartContract import SmartContract


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions or []
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.smart_contracts = []

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.smart_contracts = []
        self.purchase_requests = []
        self.offers = []
        self.account_block = None

    def get_account_wallet_hash(self):
        if self.account_block is None:
            self.init_account()
        return self.account_block.hash


    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def handle_smart_contracts(self, transactions):
        """
        This function handle current smart contract related transactions and waits to trigger its transaction
        """
        new_transactions = []
        for tx in transactions:
            if Transaction(tx).get_type() == Transaction.OFFER:
                new_contract = SmartContract(tx)
                self.smart_contracts.append(new_contract)
                ## price from seller HERE and add to new_transactions
                ## 2*price from buyer HERE and add to new_transactions
            else:
                self.purchase_requests.append(tx)
        tmp_purchase = self.purchase_requests
        tmp_offers = self.smart_contracts
        for purchase in self.purchase_requests:
            product_key_hash = Transaction(purchase).get_content()
            price = Transaction(purchase).get_amount()
            for offer in self.smart_contracts:
                if offer.purchase(price, product_key_hash):
                    tmp_purchase.remove(purchase)
                    tmp_offers.remove(offer)
                    ## 2*price to seller HERE and add to new_transactions
                    ## price to buyer HERE and add to new_transactions
                    break

        self.purchase_requests = tmp_purchase
        self.smart_contracts = tmp_offers
        return new_transactions



    def filter_transactions(self, transactions):
        """
        This function filters the unconfirmed transaction so that the smart contract related transactions are saved           and not mined, and then handles smart contracts and triggers any of them in case the conditions are met
        """
        to_mine = []
        to_process_smart_contract = []
        for tx in transactions:
            current_tx = Transaction(tx)
            type = current_tx.get_type()
            if type == Transaction.OFFER or type == Transaction.PURCHASE or type == Transaction.VERIFICATION:
                to_process_smart_contract.append(tx)
            else:
                to_mine.append(tx)

        smart_contracts_processed = self.handle_smart_contracts(to_process_smart_contract)
        for tx in smart_contracts_processed:
            to_mine.append(tx)

        return to_mine


    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        to_mine_transactions = self.filter_transactions(self.unconfirmed_transactions)
        last_block = self.last_block



        # No fee for block generation
        new_block = Block(index=last_block.index + 1,
                          transactions=to_mine_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True

    def init_account(self):
        """
        Init new user account (wallet) and register it in the blockchain
        """
        last_block = self.last_block

        # No fee for block generation
        new_block = Block(index=last_block.index + 1,
                          transactions=[],
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        if self.add_block(new_block, proof):
            self.account_block = new_block
            return True
        return False

    def create_smart_contract(self):
        """
        Init new smart contract and register it in the blockchain
        """
        last_block = self.last_block

        # No fee for block generation
        new_block = Block(index=last_block.index + 1,
                          transactions=[],
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        if self.add_block(new_block, proof):
            self.smart_contracts.append(new_block)
            return new_block
        return None
    
    @property
    def transactions(self):
        transactions = []
        for block in self.chain:
            transactions.extend(block.transactions)
        return TransactionList(self.get_account_wallet_hash(), transactions)
    #
    # @property
    # def offers(self):
    #     transactions = []
    #     for block in self.chain:
    #         transactions.extend(block.transactions)
    #     return OffersList(self.get_account_wallet_hash(), transactions)
