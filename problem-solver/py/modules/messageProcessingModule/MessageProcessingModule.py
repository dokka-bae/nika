from sc_kpm import ScModule
from .ConfigSettingsAgent import ConfigSettingsAgent


class MessageProcessingModule(ScModule):
    def __init__(self):
        super().__init__(ConfigSettingsAgent())
