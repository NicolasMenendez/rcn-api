from models import Collateral
from models import CollateralState
from contracts.commit_processor import CommitProcessor


class Started(CommitProcessor):
    def __init__(self):
        self.opcode = "started_collateral"

    def process(self, commit, *args, **kwargs):
        data = commit.data

        collateral = Collateral.objects.get(id=data["id"])
        collateral.status = data.get("status")

        collateral.save()
        commit.save()

        for collateral in Collateral.objects(debt_id=data.get("id"), id__ne=collateral.id):
            collateral.status = CollateralState.TO_WITHDRAW.value
            collateral.save()
