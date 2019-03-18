import web3
from contracts.event import EventHandler
from models import Commit
import utils


class SettledLend(EventHandler):
    signature = "SettledLend(bytes32,address,uint256)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    # def _parse(self):
    #     self._id = self._event.get("topics")[1].hex()
    #     data = self._event.get("data")
    #     splited_data = split_every(64, data)
    #     self._lender = splited_data[0]
    #     self._tokens = splited_data[1]
    #     self._block_number = self._event.get('blockNumber')
    #     self._transaction = self._event.get('transactionHash').hex()

    def _normalize(self):
        self._args["_id"] = utils.add_0x_prefix(self._args["_id"].hex())

    def handle(self):
        commit = Commit()

        commit.opcode = "settled_lend_loan_manager"
        commit.timestamp = self._block_timestamp()
        commit.proof = self._transaction

        data = {
            "id": self._args.get("_id"),
            "lender": self._args.get("_lender"),
            "tokens": self._args.get("_tokens")
        }

        commit.data = data

        return [commit]
