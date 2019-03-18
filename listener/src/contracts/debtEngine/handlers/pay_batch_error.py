import web3
from contracts.event import EventHandler
from models import Commit
import utils

class PayBatchError(EventHandler):
    signature = "PayBatchError(bytes32,address)"
    signature_hash = web3.Web3.sha3(text=signature).hex()

    # def _parse(self):
    #     self._data = self._event.get("data")
    #     self._id = self._event.get("topics")[1].hex()
    #     self._oracle = self._data
    #     self._block_number = self._event.get('blockNumber')
    #     self._transaction = self._event.get('transactionHash').hex()

    def _normalize(self):
        self._args["_id"] = utils.add_0x_prefix(self._args["_id"].hex())

    def handle(self):
        commit = Commit()

        commit.opcode = "pay_batch_error_debt_engine"
        commit.timestamp = self._block_timestamp()
        commit.proof = self._transaction

        data = {
            "id": self._args.get("_id"),
            "oracle": self._args.get("_oracle")
        }

        commit.data = data

        return [commit]
