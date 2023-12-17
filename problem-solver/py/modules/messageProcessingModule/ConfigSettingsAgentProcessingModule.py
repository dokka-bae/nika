from sc_kpm import ScModule
from .ConfigSettingsAgent import ConfigSettingsAgent


class ConfigSettingsAgentProcessingModule(ScModule):
    def __init__(self):
        super().__init__(ConfigSettingsAgent())
