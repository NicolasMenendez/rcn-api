import web3
from contracts.event import EventHandler


class SetURIProvider(EventHandler):
    signature = "SetURIProvider(address)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    def handle(self):
        return []
