from models import Descriptor
import os
from ethereum_connection import EthereumConnection
from ethereum_connection import ContractConnection

MODEL_ADDRESS = "0x2B1d585520634b4c7aAbD54D73D34333FfFe5c53"

ABI_PATH = os.path.join(
    "/project/contracts/installmentsModel",
    "abi.json"
)
URL_NODE = "https://ropsten.node.rcn.loans:8545/"

eth_conn = EthereumConnection(URL_NODE)


class LoanManagerInterface():
    def __init__(self, contract_connection):
        self.__contract_connection = contract_connection
        self.fn = self.__contract_connection.contract.functions

    def get_request_data(self, _id):
        request_data = self.fn.requests(_id).call()
        # print(request_data);
        # print("loanID=",_id)
        parsed_request_data = self.__parse_data(request_data)
        parsed_request_data["currency"] = self.get_currency(int(_id, 16))
        parsed_request_data["status"] = str(self.get_status(int(_id, 16)))
        parsed_request_data["descriptor"] = self.get_descriptor(parsed_request_data)

        return parsed_request_data

    def __parse_data(self, request_data):
        parsed_data = {}
        parsed_data["open"] = request_data[0]
        parsed_data["approved"] = request_data[1]
        parsed_data["position"] = request_data[2]
        parsed_data["expiration"] = request_data[3]
        parsed_data["amount"] = request_data[4]
        parsed_data["cosigner"] = request_data[5]
        parsed_data["model"] = request_data[6]
        parsed_data["creator"] = request_data[7]
        parsed_data["oracle"] = request_data[8]
        parsed_data["borrower"] = request_data[9]
        parsed_data["salt"] = request_data[10]
        parsed_data["loanData"] = request_data[11].hex()

        return parsed_data

    def get_directory(self):
        return self.fn.getDirectory().call()

    def get_currency(self, _id):
        return self.fn.getCurrency(_id).call().hex()

    def get_due_time(self, _id):
        return self.fn.getDueTime(_id).call()

    def get_status(self, _id):
        return self.fn.getStatus(_id).call()

    def get_descriptor(self, parsed_request_data):

        contract_connectionModel = ContractConnection(eth_conn, MODEL_ADDRESS, ABI_PATH)
        contractModel = contract_connectionModel.contract.functions
        loanData = parsed_request_data["loanData"]

        descriptor = {}

        if str(loanData) != "":
            validate = contractModel.validate(loanData).call()

            (firstObligationAmount, firstObligationTime) = contractModel.simFirstObligation(loanData).call()

            totalObligation = contractModel.simTotalObligation(loanData).call()
            duration = contractModel.simDuration(loanData).call()

            durationPercentage = ((totalObligation / int(parsed_request_data["amount"])) - 1) * 100
            interestRate = (durationPercentage * 360 * 86000) / duration 

            descriptor["first_obligation"] = str(firstObligationAmount)
            descriptor["total_obligation"] = str(totalObligation)
            descriptor["duration"] = str(duration)
            descriptor["interest_rate"] = str(interestRate)
            descriptor["punitive_interest_rate"] = str(contractModel.simPunitiveInterestRate(loanData).call())
            descriptor["frequency"] = str(contractModel.simFrequency(loanData).call())
            descriptor["installments"] = str(contractModel.simInstallments(loanData).call())

        else:
            descriptor["first_obligation"] = "0"
            descriptor["total_obligation"] = "0"
            descriptor["duration"] = "0"
            descriptor["interest_rate"] = "0"
            descriptor["punitive_interest_rate"] = "0"
            descriptor["frequency"] = "0"
            descriptor["installments"] = "0"
        return descriptor


