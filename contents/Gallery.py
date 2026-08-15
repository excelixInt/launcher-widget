from core.requirements import *
from core.widgets import BaseContent

class Gallery(BaseContent):
    def __init__(self, title = "Home"):
        super().__init__(title)
        self.setName()