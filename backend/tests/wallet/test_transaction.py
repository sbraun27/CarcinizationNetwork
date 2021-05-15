from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT

import pytest


def test_transaction():
    sender_wallet = Wallet()
    recipient_address = "test_recipient"
    amount = 50
    transaction = Transaction(sender_wallet, recipient_address, amount)

    assert transaction.output[recipient_address] == amount
    assert transaction.output[sender_wallet.address] == sender_wallet.balance - amount

    assert "timestamp" in transaction.input
    assert transaction.input["amount"] == sender_wallet.balance
    assert transaction.input["address"] == sender_wallet.address
    assert transaction.input["public_key"] == sender_wallet.public_key

    assert Wallet.verify(
        transaction.input["public_key"],
        transaction.output,
        transaction.input["signature"]
    )


def test_transaction_exceed_balance():
    with pytest.raises(Exception, match="Amount exceeds balance."):
        transaction = Transaction(Wallet(), "recipient", 9901)


def test_update_exceeds_balance():
    sender_wallet = Wallet()
    recipient_address = "test_recipient"
    amount = 50
    transaction = Transaction(sender_wallet, recipient_address, amount)

    with pytest.raises(Exception, match="Amount exceeds balance."):
        transaction.update(sender_wallet, "new_recipient", 9999)


def test_update_success():
    sender_wallet = Wallet()
    first_recipient = "first_recipient"
    first_amount = 50

    second_recipient = "second_recipient"
    second_amount = 51

    transaction = Transaction(sender_wallet, first_recipient, first_amount)
    transaction.update(sender_wallet, second_recipient, second_amount)

    assert transaction.output[second_recipient] == second_amount
    assert transaction.output[sender_wallet.address] == sender_wallet.balance - \
        first_amount - second_amount
    assert Wallet.verify(
        transaction.input["public_key"],
        transaction.output,
        transaction.input["signature"]
    )

    first_again_amount = 25
    transaction.update(sender_wallet, first_recipient, first_again_amount)

    assert transaction.output[first_recipient] == first_amount + \
        first_again_amount
    assert transaction.output[sender_wallet.address] == sender_wallet.balance - \
        first_amount - second_amount - first_again_amount
    assert Wallet.verify(
        transaction.input["public_key"],
        transaction.output,
        transaction.input["signature"]
    )


def test_validate_transaction():
    Transaction.is_valid_transaction(Transaction(Wallet(), "recipient", 50))


def test_validate_transaction_invalid_output():
    sender_wallet = Wallet()

    transaction = Transaction(sender_wallet, "recipient", 50)
    transaction.output[sender_wallet.address] = 9001

    with pytest.raises(Exception, match="The transaction is invalid because of the output values."):
        Transaction.is_valid_transaction(transaction)


def test_validate_transaction_invalid_signature():
    transaction = Transaction(Wallet(), "recipient", 50)
    transaction.input["signature"] = Wallet().sign(transaction.output)

    with pytest.raises(Exception, match="Invalid Signature."):
        Transaction.is_valid_transaction(transaction)


def test_reward_transaction():
    miner_wallet = Wallet()
    transaction = Transaction.reward_transaction(miner_wallet)

    assert transaction.input == MINING_REWARD_INPUT
    assert transaction.output[miner_wallet.address] == MINING_REWARD


def test_validate_reward_transaction():
    miner_wallet = Wallet()
    reward_transaction = Transaction.reward_transaction(miner_wallet)
    Transaction.is_valid_transaction(reward_transaction)


def test_invalid_reward_transaction_extra_recipient():
    miner_wallet = Wallet()
    reward_transaction = Transaction.reward_transaction(miner_wallet)
    reward_transaction.output["extra_recipient"] = 60

    with pytest.raises(Exception, match="Invalid mining reward."):
        Transaction.is_valid_transaction(reward_transaction)


def test_invalid_reward_transaction_invalid_amount():
    miner_wallet = Wallet()
    reward_transaction = Transaction.reward_transaction(miner_wallet)
    reward_transaction.output[miner_wallet.address] = 9999

    with pytest.raises(Exception, match="Invalid mining reward."):
        Transaction.is_valid_transaction(reward_transaction)
