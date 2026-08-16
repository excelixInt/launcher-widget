from core.widgets import *

class AppLauncherWidget(BaseWidget):
    def __init__(self,title = "App Launcher"):
        super().__init__(title)

    def fillBodyContent(self, body):
        bodyLayout = QVBoxLayout(body)
        bodyLayout.setContentsMargins(0,0,0,0)

        self.scrollArea = QScrollArea()
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.containerItem = QWidget() 
        self.containerItem.setObjectName("itemContainer")
        self.containerItemLayout = QVBoxLayout(self.containerItem)
        self.containerItemLayout.setSpacing(2)
        self.containerItemLayout.setContentsMargins(0,0,0,0)
        self.containerItemLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.loadApps()
        self.scrollArea.setWidget(self.containerItem)
        bodyLayout.addWidget(self.scrollArea)
        

    def clearContainer(self,layout : QLayout):
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            if widget := item.widget():
                widget.setParent(None)
                widget.deleteLater()
            elif sub_layout := item.layout():
                self.clearContainer(sub_layout)

    def loadApps(self):
        self.loadData()
        self.clearContainer(self.containerItemLayout)
        for name , path in self.data._data.items():
            item = QPushButton(name)
            item.setObjectName(name)
            item.setProperty("tag","app")
            self.containerItemLayout.addWidget(item)
            
            if not pl.Path(path).exists() or not path:
                item.setProperty("error","true")
                continue

            def func(name,path):
                Logger.log(f"opening {name} from {path}")
                subprocess.Popen([path])
            
            item.mousePressEvent = lambda ev , name=name , path=path : func(name,path)
            
