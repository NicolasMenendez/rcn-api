from event_buffer import EventBuffer
from listener import Listener
from processor import Processor
from contract_manager import ContractManager
from contracts.debtEngine.debt_engine import debt_engine
from contracts.installmentsModel.installments import installments
from mongoengine import connect

all_contracts = [debt_engine, installments]

contract_manager = ContractManager(all_contracts)


def run():
    connect(db="rcn", host="localhost")
    buffer = EventBuffer()
    processor = Processor(buffer, contract_manager)
    listener = Listener(buffer, contract_manager)
    listener.run()


if __name__ == '__main__':
    run()
