import os
from contract import Contract
from ethereum_connection import EthereumConnection
from ethereum_connection import ContractConnection

from .debt_engine_interface import DebtEngineInterface


ADDRESS = "0x2a878750a122EC3D6a193A4C6003Ecd8E98feB17"

ABI_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "abi.json"
)
URL_NODE = "https://ropsten.node.rcn.loans:8545/"

eth_conn = EthereumConnection(URL_NODE)
contract_connection = ContractConnection(eth_conn, ADDRESS, ABI_PATH)

debt_engine_interface = DebtEngineInterface(contract_connection)

from .handlers.approval import Approval
from .handlers.approval_for_all import ApprovalForAll
from .handlers.created import Created
from .handlers.created2 import Created2
from .handlers.created3 import Created3
from .handlers.error import Error
from .handlers.error_recover import ErrorRecover
from .handlers.paid import Paid
from .handlers.pay_batch_error import PayBatchError
from .handlers.readed_oracle import ReadedOracle
from .handlers.readed_oracle_batch import ReadedOracleBatch
from .handlers.withdrawn import Withdrawn
from .handlers.transfer import Transfer

from .commit_processors.created_debt import CreatedDebt
from .commit_processors.error import Error as ErrorCommitProcessor
from .commit_processors.error_recover import ErrorRecover as ErrorRecoverCommitProcessor
from .commit_processors.paid import Paid as PaidCommitProcessor
from .commit_processors.readed_oracle import ReadedOracle as ReadedOracleCommitProcessor

commit_processors = [
    CreatedDebt(),
    ErrorCommitProcessor(),
    ErrorRecoverCommitProcessor(),
    PaidCommitProcessor(),
    ReadedOracleCommitProcessor()
]
schedule_processors = []

EVENTS_HANDLERS = [
    Approval,
    ApprovalForAll,
    Created,
    Created2,
    Created3,
    Error,
    ErrorRecover,
    Paid,
    PayBatchError,
    ReadedOracle,
    ReadedOracleBatch,
    Withdrawn,
    Transfer
]


debt_engine = Contract(
    "DebtEngine",
    EVENTS_HANDLERS,
    commit_processors,
    schedule_processors,
    contract_connection
)
