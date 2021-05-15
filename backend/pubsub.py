import time

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction


pnconfig = PNConfiguration()
pnconfig.dameon = True
pnconfig.subscribe_key = "sub-c-f44f7d76-b1e2-11eb-b076-ba6f25ae3261"
pnconfig.publish_key = "pub-c-feb9fe27-6b9a-4892-892b-1764ed7e6db1"

CHANNELS = {
    "TEST": "TEST",
    "BLOCK": "BLOCK",
    "TRANSACTION": "TRANSACTION"
}


class Listener(SubscribeCallback):
    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_object):
        print(
            f"\n-- Channel: {message_object.channel} | {message_object.message}")

        if message_object.channel == CHANNELS["BLOCK"]:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.chain_replacement(potential_chain)
                self.transaction_pool.clear_blockchain_transactions(
                    self.blockchain)
                print(f"\n -- Successfully replaced local chain.")

            except Exception as e:
                print(f"\n -- Did not replace chain: {e}")

        elif message_object.channel == CHANNELS["TRANSACTION"]:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print("\n -- Set the new transaction in the transaction pool.")


class PubSub:
    """
    Handles the Publish/subscribe layer of the application.
    Provides teh communication between nodes of the blockchain network.
    """

    def __init__(self, blockchain, transaction_pool):
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(
            CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))

    def publish(self, channel, message):
        """
        This method takes care of publichsing a message object to the channel
        """
        self.pubnub.publish().channel(channel).message(message).sync()

    def broadcast_block(self, block):
        """
        Broadcast a block object to all nodes.
        """
        self.publish(CHANNELS["BLOCK"], block.to_json())

    def broadcast_transaction(self, transaction):
        """
        Broadcast a transaction to all of the nodes.
        """
        self.publish(CHANNELS["TRANSACTION"], transaction.to_json())


def main():
    pubsub = PubSub()

    time.sleep(1)

    pubsub.publish(CHANNELS["TEST"], {"foo": "bar"})


if __name__ == "__main__":
    main()
