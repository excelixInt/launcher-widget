from core.widgets import *

class MusicPlayerWidget(BaseWidget):
    def __init__(self,title = "Music Player"):
        super().__init__(title)
        self.heightOpen = 500