from core.requirements import *
from core.widgets import BaseContent
from widgets.ClockWidget import ClockWidget

class Home(BaseContent):
    def __init__(self, title = "Home"):
        super().__init__(title)
        self.setName()

    def fillContent(self, container):
        container.layout().addWidget(ClockWidget())
        container.layout().addStretch()