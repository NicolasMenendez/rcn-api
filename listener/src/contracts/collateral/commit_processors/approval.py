from contracts.commit_processor import CommitProcessor


class Approval(CommitProcessor):
    def __init__(self):
        self.opcode = "approval"

    def process(self, commit, *args, **kwargs):
        pass