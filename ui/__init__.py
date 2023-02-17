from .window.general import GeneralWindow
from .window.log import LogWindow
from .window.settings import SettingsWindow

class GreenyyUiManager():
    def __init__(self) -> None:    
        self.generalWindow = GeneralWindow()
        self.settingsWindow = SettingsWindow()
        self.logWindow = LogWindow()
        self.interconnect()

    def interconnect(self):
        self.generalWindow.meiDevices.triggered.connect(self.settingsWindow.show0)
        self.generalWindow.meiRules.triggered.connect(self.settingsWindow.show1)
        self.generalWindow.meiLog.triggered.connect(self.logWindow.show)

    def deviceIntegration(self, dm):
        for d in dm.devices:
            self.generalWindow.meiPlants.addAction(d.address)
