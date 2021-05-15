from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.config import MINING_REWARD_INPUT
from backend.wallet.wallet import Wallet


class Blockchain:
    """
    Blockchain: a public ledger of transactions. 
    Implemented as a list of blocks - data sets of transactions.
    """

    def __repr__(self):
        return f"Blockchain: {self.chain}"

    def __init__(self):
        self.chain = [Block.genesis()]

    def add_block(self, data):
        self.chain.append(Block.mine_block(self.chain[-1], data))

    def chain_replacement(self, chain):
        """replace the lcoal chain with the incoming one if the following rules apply:
        1) The incoming chain must be longer than the local one.
        2) The incoming chain must be formatted properly
        """
        if len(chain) <= len(self.chain):
            raise Exception(
                "Cannot replace with the incoming chain. The incoming chain must be longer.")

        try:
            Blockchain.is_valid_chain(chain)
        except Exception as e:
            raise Exception(
                f"Cannot replace. The incoming chain is invalid: {e}.")

        self.chain = chain

    def to_json(self):
        """
        The goal of this method is to serialize the blockchain into a list of blocks.
        """

        return list(map(lambda block: block.to_json(), self.chain))

    @staticmethod
    def from_json(chain_json):
        """Deserialize a list of serialized blocks into a blockchain instance.
        The result will contain a chain list of Block instances.
        """
        blockchain = Blockchain()
        blockchain.chain = list(
            map(lambda block_json: Block.from_json(block_json), chain_json))

        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """validate the incoming chain using the following rules:
        1) The chain must start with the genesis block.
        2) Blocks must be formatted correctly.
        3) All transactions in the chain must be valid.
        """
        if chain[0] != Block.genesis():
            raise Exception("The genesis block must be valid.")

        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i-1]

            Block.is_valid_block(last_block, block)

        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforce the rules of a chain compoesd of blocks of transactions.
        1) Each transaction must only appear once in the chain.
        2) There can only be one mining reward per block.
        3) Each transaction must be valid.
        """
        transaction_ids = set()

        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False

            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(
                        f"Transaction: {transaction.id} is not unique.")

                transaction_ids.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(
                            "There can only be one mining reward per block.",
                            f"Check block with this has: {block.hash}.")
                    has_mining_reward = True

                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[0:i]

                    historic_balance = Wallet.calculate_balance(
                        historic_blockchain,
                        transaction.input["address"]
                    )

                    if historic_balance != transaction.input["amount"]:
                        raise Exception(
                            f"The transaction {transaction.id} has an invalid input amount.")

                Transaction.is_valid_transaction(transaction)


def main():
    blockchain = Blockchain()
    blockchain.add_block("one")
    blockchain.add_block("two")

    print(blockchain)


if __name__ == "__main__":
    main()
