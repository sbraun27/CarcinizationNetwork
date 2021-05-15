import pytest

from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import GENESIS_DATA
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction


def test_blockchain_instance():
    blockchain = Blockchain()

    assert blockchain.chain[0].hash == GENESIS_DATA["hash"]


def test_add_block():
    blockchain = Blockchain()
    data = "test-data"

    blockchain.add_block(data=data)

    assert blockchain.chain[-1].data == data


@pytest.fixture
def blockchain_init():
    blockchain = Blockchain()
    for i in range(3):
        blockchain.add_block([Transaction(Wallet(), "recipient", i).to_json()])

    return blockchain


def test_is_valid_chain(blockchain_init):
    Blockchain.is_valid_chain(blockchain_init.chain)


def test_is_valid_chain_bad_genesis(blockchain_init):
    blockchain_init.chain[0].hash = "evil_hash"

    with pytest.raises(Exception, match="The genesis block must be valid."):
        Blockchain.is_valid_chain(blockchain_init.chain)


def test_chain_replacement(blockchain_init):
    blockchain = Blockchain()
    blockchain.chain_replacement(blockchain_init.chain)

    assert blockchain.chain == blockchain_init.chain


def test_chain_replacement_not_longer(blockchain_init):
    blockchain = Blockchain()

    with pytest.raises(Exception, match="Cannot replace with the incoming chain. The incoming chain must be longer."):
        blockchain_init.chain_replacement(blockchain.chain)


def test_chain_replacement_bad_chain(blockchain_init):
    blockchain = Blockchain()
    blockchain_init.chain[1].hash = "evil_hash"

    with pytest.raises(Exception, match="Cannot replace. The incoming chain is invalid:"):
        blockchain.chain_replacement(blockchain_init.chain)


def test_valid_transaction_chain(blockchain_init):
    Blockchain.is_valid_transaction_chain(blockchain_init.chain)


def test_invalid_transaction_chain_duplicate_transactions(blockchain_init):
    transaction = Transaction(Wallet(), "recipient", 1).to_json()
    blockchain_init.add_block([transaction, transaction])

    with pytest.raises(Exception, match="is not unique."):
        Blockchain.is_valid_transaction_chain(blockchain_init.chain)


def test_invalid_transaction_chain_multiple_mining_rewards(blockchain_init):
    reward_1 = Transaction.reward_transaction(Wallet()).to_json()
    reward_2 = Transaction.reward_transaction(Wallet()).to_json()

    blockchain_init.add_block([reward_1, reward_2])

    with pytest.raises(Exception, match="There can only be one mining reward per block."):
        Blockchain.is_valid_transaction_chain(blockchain_init.chain)


def test_invalid_transaction_chain_malformed_transaction(blockchain_init):
    bad_transaction = Transaction(Wallet(), "recipient", 1)
    bad_transaction.input["signature"] = Wallet().sign(
        bad_transaction.output)

    blockchain_init.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception):
        Blockchain.is_valid_transaction_chain(blockchain_init.chain)


def test_invalid_transaction_chain_bad_historic_balance(blockchain_init):
    wallet = Wallet()
    bad_transaction = Transaction(wallet, "recipient", 1)
    bad_transaction.output[wallet.address] = 9999

    bad_transaction.input["amount"] = 10000

    bad_transaction.input["signature"] = wallet.sign(bad_transaction.output)

    blockchain_init.add_block([bad_transaction.to_json()])

    with pytest.raises(Exception, match="invalid input amount."):
        Blockchain.is_valid_transaction_chain(blockchain_init.chain)
