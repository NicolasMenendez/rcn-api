import os
from contract import Contract
from ethereum_connection import EthereumConnection
from ethereum_connection import ContractConnection

from .loan_manager_interface import LoanManagerInterface


ADDRESS = "0x978ef6D2bd7559181e6Ac82fFa5C875364d9071b"

ABI_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "abi.json"
)
URL_NODE = "https://ropsten.node.rcn.loans:8545/"

eth_conn = EthereumConnection(URL_NODE)
contract_connection = ContractConnection(eth_conn, ADDRESS, ABI_PATH)

loan_manager_interface = LoanManagerInterface(contract_connection)

from .handlers.approved import Approved
from .handlers.approved_error import ApprovedError
from .handlers.approved_rejected import ApprovedRejected
from .handlers.canceled import Canceled
from .handlers.cosigned import Cosigned
from .handlers.lent import Lent
from .handlers.readed_oracle import ReadedOracle
from .handlers.requested import Requested
from .handlers.settled_cancel import SettledCancel
from .handlers.settled_lend import SettledLend
from .handlers.approved_by_callback import ApprovedByCallback
from .handlers.approved_by_signature import ApprovedBySignature
from .handlers.borrower_by_callback import BorrowerByCallback
from .handlers.borrower_by_signature import BorrowerBySignature
from .handlers.creator_by_callback import CreatorByCallback
from .handlers.creator_by_signature import CreatorBySignature

from .commit_processors.approved import Approved as ApprovedCommitProcessor
from .commit_processors.canceled import Canceled as CanceledCommitProcessor
from .commit_processors.cosigned import Cosigned as CosignedCommitProcessor
from .commit_processors.lent import Lent as LentCommitProcessor
from .commit_processors.requested import Requested as RequestedCommitProcessor
from .commit_processors.approved_error import ApprovedError as ApprovedErrorCommitProcessor
from .commit_processors.approved_rejected import ApprovedRejected as ApprovedRejectectCommitProcessor
from .commit_processors.readed_oracle import ReadedOracle as ReadedOracleCommitProcessor
from .commit_processors.settled_cancel import SettledCancel as SettledCancelCommitProcessor
from .commit_processors.settled_lend import SettledLend as SettledLendCommitProcessor


commit_processors = [
    ApprovedCommitProcessor(),
    CanceledCommitProcessor(),
    CosignedCommitProcessor(),
    LentCommitProcessor(),
    RequestedCommitProcessor(),
    ApprovedErrorCommitProcessor(),
    ReadedOracleCommitProcessor(),
    ApprovedRejectectCommitProcessor(),
    SettledCancelCommitProcessor(),
    SettledLendCommitProcessor()
]

schedule_processors = []

event_handlers = [
    Approved,
    ApprovedError,
    ApprovedRejected,
    Canceled,
    Cosigned,
    Lent,
    ReadedOracle,
    Requested,
    SettledCancel,
    SettledLend,
    ApprovedByCallback,
    ApprovedBySignature,
    BorrowerByCallback,
    BorrowerBySignature,
    CreatorByCallback,
    CreatorBySignature
]

loan_manager = Contract(
    "LoanManager",
    event_handlers,
    commit_processors,
    schedule_processors,
    contract_connection
)
