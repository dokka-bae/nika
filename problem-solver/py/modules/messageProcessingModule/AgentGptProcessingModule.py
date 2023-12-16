from sc_kpm import ScModule
from .AgentGptAssistent import AgentGptAssistent


class AgentGptProcessingModule(ScModule):
    def __init__(self):
        super().__init__(AgentGptAssistent())
