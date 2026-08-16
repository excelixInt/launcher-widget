from __future__ import annotations
from core.requirements import *
from core.requirements import __rootpath__

# Custom Widget
class WidgetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.uiContainer = QWidget()
        self.uiContainer.setObjectName("container")
        self.uiLayout : QVBoxLayout | QHBoxLayout = None

    @property
    def root(self):
        return self.layout()
    
    def _placeStart(self):
        self.root.addWidget(self.uiContainer)
    
    def _noMargin(self):
        self.uiLayout.setContentsMargins(0,0,0,0)
        self.root.setContentsMargins(0,0,0,0)

class RoundIconWidget(QLabel):
    def __init__(self, image_path=None, size=100, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

        if image_path:
            self.set_image(image_path)

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            return

        pixmap = pixmap.scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        rounded = QPixmap(*self.size().toTuple())
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, *self.size().toTuple())

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.setPixmap(rounded)

    def set_size(self, size):
        self.setFixedSize(size, size)

def pixmapButton(
    pixmap : QPixmap,
    name : str,
    buttonSize : QSize = QSize(35,35),
    pixmapSize : QSize = QSize(25,25),
    onClick : typing.Callable | typing.Any = None,
    aspectMode : Qt.AspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio,
    transformationMode : Qt.TransformationMode = Qt.TransformationMode.SmoothTransformation
    ):
    label = QLabel()
    if pixmapSize:
        if aspectMode and transformationMode:
            pixmap = pixmap.scaled(QSize(pixmapSize),aspectMode,transformationMode)
        elif aspectMode:
            pixmap = pixmap.scaled(QSize(pixmapSize),aspectMode)
        elif transformationMode:
            pixmap = pixmap.scaled(QSize(pixmapSize),transformationMode=transformationMode)
        else:
            pixmap = pixmap.scaled(QSize(pixmapSize))
    if buttonSize:
        label.setFixedSize(QSize(buttonSize))
    if onClick:
        label.mousePressEvent = onClick

    label.setToolTip(name)
    label.setPixmap(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setObjectName(name)
    label.setProperty("tag","pixmapButton")
    return label

# Widget Panels
class BaseWidget(QWidget):
    class Head(QWidget):
        def __init__(self,widget : BaseWidget,title : str = "",**kw):
            super().__init__()
            self.setFixedHeight(47)
            QHBoxLayout(self).setAlignment(Qt.AlignmentFlag.AlignTop)

            buttonSize = QSize(30,30)
            self.layout().setContentsMargins(0,0,0,0)

            self.setObjectName("widget-head")
            self.widget = widget

            self.title = QLabel(title)
            self.title.setObjectName("widget-title")
            self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self.hideButtonPixmap = {"hide":ICONS.get("menu.arrow_up"),"show":ICONS.get("menu.arrow_down")}
            self.hideButton = pixmapButton(QPixmap(),"hideButton",buttonSize,None,self.hideBody)
            self._updateHideButtonPixmap()

            self.layout().addWidget(self.title,stretch=1)
            self.layout().addWidget(self.hideButton)

        def hideBody(self,ev):
            if self.body.isHidden():
                self.body.show()
            else:
                self.body.hide()
            self._updateHideButtonPixmap()
            self._updateWidgetHeight()

        def _updateHideButtonPixmap(self):
            if self.body.isHidden():
                self.hideButton.setPixmap(self.hideButtonPixmap["show"])
            else:
                self.hideButton.setPixmap(self.hideButtonPixmap["hide"])

        def _updateWidgetHeight(self):
            anim1 = QPropertyAnimation(self.widget,b"minimumHeight")
            anim1.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
            anim1.setDuration(SETTINGS.get("animation.duration"))

            anim2 = QPropertyAnimation(self.widget,b"maximumHeight")
            anim2.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
            anim2.setDuration(SETTINGS.get("animation.duration"))

            if self.body.isHidden():
                Logger.log(f"hide widgets : {self.widget.objectName()}")
                anim1.setStartValue(self.widget.heightOpen)
                anim2.setStartValue(self.widget.heightOpen)

                anim1.setEndValue(self.height())
                anim2.setEndValue(self.height())
            else:
                Logger.log(f"show widgets : {self.widget.objectName()}")
                anim1.setStartValue(self.height())
                anim2.setStartValue(self.height())
                
                anim1.setEndValue(self.widget.heightOpen)
                anim2.setEndValue(self.widget.heightOpen)
            self.widget.anim1 = anim1
            self.widget.anim2 = anim2
            anim1.start()
            anim2.start()

        @property
        def body(self):
            return self.widget.body

    class Body(QWidget):
        def __init__(self,widget : BaseWidget,**kw):
            super().__init__()
            self.show()
            self.setObjectName("widget-body")
            self.widget = widget

    def __init__(self,title : str = ""):
        super().__init__()
        QVBoxLayout(self).setContentsMargins(0,0,0,0)
        self.setProperty("tag","Widget")
        self.setName()
        self.data = DynamicDict({})
        
        self.heightOpen = 200
        self.setMaximumHeight(self.heightOpen)

        self.container = QWidget()
        QVBoxLayout(self.container)
        self.container.setObjectName(f"{self.objectName()}-container")

        self.body = self.Body(self)
        self.head = self.Head(self,title)
        self.head._updateWidgetHeight()

        self.fillBodyContent(self.body)

        self.container.layout().addWidget(self.head)
        self.container.layout().addWidget(self.body,stretch=1)
        self.layout().addWidget(self.container)

    def fillBodyContent(self,body : Body):...

    def setContainerLayout(self,layout : QLayout):
        self.container.setLayout(layout)
        return layout

    def setName(self):
        self.setObjectName(self.__class__.__name__)

    def loadData(self):
        Logger.log(f"{self.objectName()}.loadData()")
        path = __rootpath__(f"data/widgets/{self.objectName()}.json")
        if not path.exists():
            with open(path,"w") as f:
                json.dump({},f,indent=4)
        self.data = DynamicDict(path)

class BaseContent(QWidget):
    def __init__(self,parent : QWidget,title : str = ""):
        super().__init__(parent)
        self.setProperty("tag","Content")
        self.setName()
        self.data = DynamicDict({})
        
        self.title = title

        QVBoxLayout(self)
        self.container = QWidget()
        QVBoxLayout(self.container)
        self.container.setObjectName(f"{self.objectName()}-container")

        self.fillContent(self.container)
        self.layout().addWidget(self.container)


    def fillContent(self,container : QWidget):...

    def setContainerLayout(self,layout : QLayout):
        self.container.setLayout(layout)

    def setName(self):
        self.setObjectName(self.__class__.__name__)

    def loadData(self):
        Logger.log(f"{self.objectName()}.loadData()")
        path = __rootpath__(f"data/contents/{self.objectName()}.json")
        if not path.exists():
            with open(path,"w") as f:
                json.dump({},f,indent=4)
        self.data = DynamicDict(path)