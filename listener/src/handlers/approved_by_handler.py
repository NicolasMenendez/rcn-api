import web3
from .event_handler import EventHandler
from handlers import utils

class ApprovedByHandler(EventHandler):
    signature = 'ApprovedBy(uint256,address)'
    signature_hash = web3.Web3.sha3(text=signature)

    def _parse(self):
        data = self._event.get('data')[2:]
        splited_args = utils.split_every(64, data)
        self._index = utils.to_int(splited_args[0])
        self._address = utils.to_address(splited_args[1])

    def do(self):
        pass