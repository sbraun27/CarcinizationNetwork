from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pprint import pprint


class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):
        pass

    def presence(self, pubnub, presence):
        pprint(presence.__dict__)

    def message(self, pubnub, message):
        pprint(message.__dict__)


def my_publish_callback(envelope, status):
    print(envelope, status)


pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-f44f7d76-b1e2-11eb-b076-ba6f25ae3261"
pnconfig.publish_key = "pub-c-feb9fe27-6b9a-4892-892b-1764ed7e6db1"

pubnub = PubNub(pnconfig)

pubnub.add_listener(MySubscribeCallback())

pubnub.subscribe()\
    .channels("pubnub_onboarding_channel")\
    .with_presence()\
    .execute()\

pubnub.publish()\
    .channel("pubnub_onboarding_channel")\
    .message({"sender": pnconfig.uuid, "content": "Hello From Python SDK"})\
    .pn_async(my_publish_callback)
