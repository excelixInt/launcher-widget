from __future__ import annotations
from core.widgets import *
from core.requirements import _SettingsPath , _DataFolderPath , __rootpath__

# WidgetLoader
AttachableWidgets : typing.Dict[str,type[BaseWidget]] = {}
for file in os.listdir(__rootpath__("widgets")):
    if not file.endswith(".py"):
        continue
    widgetName = file.removesuffix(".py")
    widgetRoot = __import__(f"widgets.{widgetName}")
    widgetModule = getattr(widgetRoot,widgetName)
    try:
        widget = getattr(widgetModule,widgetName)
    except AttributeError:
        ExceptionLogger.exception(f"cannot find {widgetName} in {file}",AttributeError,"class name and file name unmatched.")
    except Exception as e:
        ExceptionLogger.exception(f"{e}",detail=f"something went wrong when collecting {widgetName} in {file}")
    else:
        AttachableWidgets[widgetName] = widget

# ContentLoader
ContentGroup: typing.Dict[str,type[BaseContent]] = {}
for file in os.listdir(__rootpath__("contents")):
    if not file.endswith(".py"):
        continue
    contentName = file.removesuffix(".py")
    contentRoot = __import__(f"contents.{contentName}")
    contentModule = getattr(contentRoot,contentName)
    try:
        content = getattr(contentModule,contentName)
    except AttributeError:
        ExceptionLogger.exception(f"cannot find {contentName} in {file}",AttributeError,"class name and file name unmatched.")
    except Exception as e:
        ExceptionLogger.exception(f"{e}",detail=f"something went wrong when collecting {contentName} in {file}")
    else:
        ContentGroup[contentName] = content

# App
class Root(QWidget):
    LEFTMODE = "leftmode"
    RIGHTMODE = "rightmode"
    class RootElement(QWidget):
        def __init__(self,root : Root,w:int,h:int):
            super().__init__(parent=root)
            self.data : DynamicDict
            self.root = root
            self.resize(w,h)
            self.setName()
            self.container = QWidget()
            self.container.setObjectName("container")
            self.containerLayout : QHBoxLayout | QVBoxLayout = None
            
        def isOpen(self) -> bool:...
        def loadData(self):
            self.data = DynamicDict(__rootpath__(_DataFolderPath / f"{self.objectName()}.json"))
        def setName(self):
            self.setObjectName(self.__class__.__name__)
            
    class Sidebar(RootElement):
        class Part(QWidget):
            def __init__(self,sidebar : Root.Sidebar):
                super().__init__()
                self.sidebar = sidebar
                self.setName()
                self.setProperty("tag",f"{sidebar.objectName()}-Part")
                QVBoxLayout(self).setContentsMargins(0,0,0,0)

                self.content = QWidget()
                self.content.setObjectName("content")
                self.contentLayout = None

            def setName(self):
                self.setObjectName(self.__class__.__name__)

        class Head(Part):
            def __init__(self, sidebar):
                super().__init__(sidebar)
                self.contentLayout = QHBoxLayout(self.content)
                self.contentLayout.setContentsMargins(0,0,0,0)

                # profileImage
                
                self.profileImage = RoundIconWidget(__rootpath__(self.sidebar.data.get("profileImage")),size=50)
                self.profileImage.setObjectName("profileImage")

                # title
                self.title = QLabel(self.sidebar.data.get("title"))
                self.title.setObjectName("title")
                self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                # buttons
                buttonSize = QSize(40,40)
                # sideButton
                self.sideButton = pixmapButton(QPixmap(),"sideButton",buttonSize,None,self.changeSide,None,None)
                self._updateChangeSideButtonIcon()
                # closeButton
                self.closeButton = pixmapButton(ICONS.get("menu.close"),"closeButton",buttonSize,None,self.closeSidebar,None,None)
            
                # place
                self.contentLayout.addWidget(self.profileImage)
                self.contentLayout.addWidget(self.title)
                self.contentLayout.addWidget(self.sideButton)
                self.contentLayout.addWidget(self.closeButton)
                self.layout().addWidget(self.content)

            def changeSide(self,event : typing.Any):
                match self.sidebar.root.sideMode:
                    case Root.LEFTMODE:
                        self.sidebar.root.setSide(Root.RIGHTMODE)
                    case Root.RIGHTMODE:
                        self.sidebar.root.setSide(Root.LEFTMODE)
                    case _:
                        InvalidSideModeError(self,self.changeSide.__name__)
                self._updateChangeSideButtonIcon()

            def closeSidebar(self,event : typing.Any):
                self.sidebar.setOpen(False)
                self.sidebar.root.panelcontainer.setFullWidth()
                
            def _updateChangeSideButtonIcon(self):
                match self.sidebar.root.sideMode:
                    case Root.LEFTMODE:
                        self.sideButton.setPixmap(ICONS.get("menu.toright"))
                    case Root.RIGHTMODE:
                        self.sideButton.setPixmap(ICONS.get("menu.toleft"))
                    case _:
                        InvalidSideModeError(self,self._updateChangeSideButtonIcon.__name__)

        class Body(Part):
            def __init__(self, sidebar):
                super().__init__(sidebar)
                self.contentLayout = QVBoxLayout(self.content)
                self.contentLayout.setContentsMargins(0,0,0,0)
                
                self.scrollArea = QScrollArea(widgetResizable=True,alignment=Qt.AlignmentFlag.AlignTop)
                self.scrollArea.setObjectName("scrollarea")
                self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

                # contents
                for widget in self.sidebar.data.get("widgets"):
                    if widget not in AttachableWidgets.keys():
                        ExceptionLogger.exception(f"widget : {widget} not found",KeyError,"the widget may did not load correctly.")
                        continue
                    self.contentLayout.addWidget(AttachableWidgets[widget]())
                
                self.contentLayout.addStretch()
                self.contentLayout.setSpacing(2)

                self.scrollArea.setWidget(self.content)
                self.layout().addWidget(self.scrollArea)

        class Foot(Part):
            def __init__(self, sidebar):
                super().__init__(sidebar)
                self.contentLayout = QHBoxLayout(self.content)
                self.contentLayout.setContentsMargins(0,0,0,0)
                
                self.scrollArea = QScrollArea(widgetResizable=True,alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.scrollArea.setObjectName("scrollarea")
                self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

                # contents
                for key , link in self.sidebar.root.connections.items():
                    if key in ICONS.get("connections").keys():
                        pixmap = ICONS.get(f"connections.{key}")
                    else:
                        pixmap = ICONS.get(f"connections.link")
                    btn = pixmapButton(pixmap,key,onClick=lambda ev , l=link: webbrowser.open(l))
                    self.contentLayout.addWidget(btn)

                self.scrollArea.setWidget(self.content)
                self.layout().addWidget(self.scrollArea)
                
        def __init__(self, root, w, h):
            super().__init__(root, w, h)
            self.loadData()
            QVBoxLayout(self)
            self.containerLayout = QVBoxLayout(self.container)

            self.head = self.Head(self)
            self.body = self.Body(self)
            self.foot = self.Foot(self)

            self.containerLayout.addWidget(self.head)
            self.containerLayout.addWidget(self.body,stretch=1)
            self.containerLayout.addWidget(self.foot)
        
            self.layout().addWidget(self.container)

        def isOpen(self) -> bool:
            match self.root.sideMode:
                case Root.LEFTMODE:
                    return self.geometry().left() >= 0
                case Root.RIGHTMODE:
                    return self.geometry().right() <= self.root.width()
                case _:
                    InvalidSideModeError(self,self.isOpen.__name__)

        def setOpen(self,value : bool = True):
            Logger.log(f"{self.objectName()}.setOpen({value})")
            if (self.isOpen() and value) or (not self.isOpen() and not value):
                if value:
                    Logger.log(f"{self.objectName()} already opened",1)
                    return
                Logger.log(f"{self.objectName()} already closed",1)
                return

            rectClose : QRect
            rectOpen : QRect
            match self.root.sideMode:
                case Root.LEFTMODE:
                    rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.leftmode.close")
                    rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.leftmode.open")
                case Root.RIGHTMODE:
                    rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.rightmode.close")
                    rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.rightmode.open")
                case _:
                    InvalidSideModeError(self,self.setOpen.__name__)

            anim = QPropertyAnimation(self, b"geometry")
            anim.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
            anim.setDuration(SETTINGS.get("animation.duration"))

            if value:
                self.show()
                self.raise_()
                self.activateWindow()
                anim.setStartValue(rectClose)
                anim.setEndValue(rectOpen)
            else:
                anim.finished.connect(self.hide)
                anim.setStartValue(rectOpen)
                anim.setEndValue(rectClose)

            self.anim = anim
            anim.start()

    class PanelContainer(RootElement):
        class Part(QWidget):
            def __init__(self,panelcontainer : Root.PanelContainer):
                super().__init__()
                self.panelcontainer = panelcontainer
                self.setName()
                self.setProperty("tag",f"{panelcontainer.objectName()}-Part")
                QVBoxLayout(self).setContentsMargins(0,0,0,0)

                self.content = QWidget()
                self.content.setObjectName("content")
                self.contentLayout = None

            def setName(self):
                self.setObjectName(self.__class__.__name__)

        class Head(Part):
            def __init__(self, panelcontainer):
                super().__init__(panelcontainer)
                self.contentLayout = QHBoxLayout(self.content)
                self.contentLayout.setContentsMargins(0,0,0,0)

                # title
                self.title = QLabel(self.panelcontainer.data.get("title"))
                self.title.setObjectName("title")
                self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # buttons
                buttonSize = QSize(40,40)
                self.closeButton = pixmapButton(ICONS.get("menu.close"),"closeButton",buttonSize,None,self.closePanelContainer,None,None)
            
                # place
                self.contentLayout.addWidget(self.title)
                self.contentLayout.addWidget(self.closeButton)
                self.layout().addWidget(self.content)

            def closePanelContainer(self,ev):
                self.panelcontainer.setOpen(False)

        class Body(Part):
            class Navbar(QWidget):
                def __init__(self,contentstacker : Root.PanelContainer.Body.ContentStacker):
                    super().__init__()
                    self.setObjectName(self.__class__.__name__)
                    QHBoxLayout(self).setContentsMargins(0,0,0,0)
                    self.contentstacker = contentstacker

                    self.container = QWidget()
                    self.container.setObjectName(f"{self.objectName()}-container")
                    self.containerLayout = QHBoxLayout(self.container)
                    self.containerLayout.setContentsMargins(0,0,0,0)
                    
                    self.loadContentTabs()
                    self.layout().addWidget(self.container)

                def loadContentTabs(self):
                    for i , content in enumerate([self.contentstacker.widget(i) for i in range(self.contentstacker.count())]):
                        btn = QLabel(content.objectName(),alignment=Qt.AlignmentFlag.AlignCenter)
                        btn.setProperty("tag","textButton")
                        btn.mousePressEvent = lambda ev , idx=i: self.contentstacker.setCurrentContentByIndex(idx)
                        self.containerLayout.addWidget(btn)

            class ContentStacker(QStackedWidget):
                def __init__(self, bindWidget : Root.PanelContainer.Body):
                    super().__init__()
                    self.setObjectName(self.__class__.__name__)
                    self.bindWidget = bindWidget
                    self.animGroup = QParallelAnimationGroup(self)
                    self.loadContents()

                def loadContents(self):
                    for contentName in self.bindWidget.panelcontainer.data.get("contents"):
                        contentName : str
                        if not contentName in ContentGroup.keys():
                            ExceptionLogger.exception(f"content : {contentName} not found",KeyError,"the content may did not load correctly.")
                            continue
                        content = ContentGroup[contentName](self)
                        self.addWidget(content)

                def setCurrentContentByIndex(self,index : int):
                    if self.currentIndex() == index or index < 0 or index >= self.count():
                        return

                    current_index = self.currentIndex()
                    current_content = self.widget(current_index)
                    next_content = self.widget(index)

                    # next
                    if current_index < index:
                        next_startGeometry = self.rightContentRect
                        current_endGeometry = self.leftContentRect
                    # prev
                    else:
                        next_startGeometry = self.leftContentRect
                        current_endGeometry = self.rightContentRect

                    next_content.setGeometry(next_startGeometry)
                    next_content.show()
                    next_content.raise_()

                    anim_current = QPropertyAnimation(current_content,b"geometry",self)
                    anim_current.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
                    anim_current.setDuration(SETTINGS.get("animation.duration"))
                    anim_current.setStartValue(self.displayedContentRect)
                    anim_current.setEndValue(current_endGeometry)

                    anim_next = QPropertyAnimation(next_content,b"geometry",self)
                    anim_next.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
                    anim_next.setDuration(SETTINGS.get("animation.duration"))
                    anim_next.setStartValue(next_startGeometry)
                    anim_next.setEndValue(self.displayedContentRect)
                        
                    self.animGroup.addAnimation(anim_current)
                    self.animGroup.addAnimation(anim_next)
                    
                    self.animGroup.finished.connect(lambda: self._on_animation_finished(index))
                    self.animGroup.start()

                def _on_animation_finished(self, index: int):
                    try:
                        del self.animGroup
                        self.animGroup = QParallelAnimationGroup(self)
                    except TypeError:
                        pass
                    self.setCurrentIndex(index)

                @property
                def displayedContentRect(self):
                    return QRect(QPoint(0,0),self.bindWidget.size())
                @property
                def leftContentRect(self):
                    return QRect(QPoint(-self.bindWidget.width(),0),self.bindWidget.size())
                @property
                def rightContentRect(self):
                    return QRect(QPoint(self.bindWidget.width(),0),self.bindWidget.size())
                
            def __init__(self, panelcontainer): 
                super().__init__(panelcontainer)
                self.contentLayout = QVBoxLayout(self.content)
                self.contentLayout.setContentsMargins(0,0,0,0)

                self.contentstacker = self.ContentStacker(self)
                self.navbar = self.Navbar(self.contentstacker)
                
                self.contentLayout.setSpacing(2)
                self.contentLayout.addWidget(self.navbar)
                self.contentLayout.addWidget(self.contentstacker,stretch=1)
                self.layout().addWidget(self.content)

        def __init__(self, root, w, h):
            super().__init__(root, w, h)
            self.loadData()
            QVBoxLayout(self).setContentsMargins(5,5,5,5)
            self.containerLayout = QVBoxLayout(self.container)

            self.head = self.Head(self)
            self.body = self.Body(self)

            self.containerLayout.addWidget(self.head)
            self.containerLayout.addWidget(self.body,stretch=1)
            self.layout().addWidget(self.container)

        def isOpen(self):
            return self.geometry().bottom() <= self.root.height()

        def setOpen(self,value : bool = True):
            Logger.log(f"{self.objectName()}.setOpen({value})")
            if (self.isOpen() and value) or (not self.isOpen() and not value):
                if value:
                    Logger.log(f"{self.objectName()} already opened",1)
                    return
                Logger.log(f"{self.objectName()} already closed",1)
                return
            
            rectClose : QRect
            rectOpen : QRect
            if self.root.sidebar.isOpen():
                match self.root.sideMode:
                    case Root.LEFTMODE:
                        rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.leftmode.close")
                        rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.leftmode.open")
                    case Root.RIGHTMODE:
                        rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.rightmode.close")
                        rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.rightmode.open")
                    case _:
                        InvalidSideModeError(self,self.setOpen.__name__)
            else:
                rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.fullwidth.close")
                rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.fullwidth.open")
                
            anim = QPropertyAnimation(self, b"geometry")
            anim.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
            anim.setDuration(SETTINGS.get("animation.duration"))

            if value:
                self.show()
                self.raise_()
                self.activateWindow()
                anim.setStartValue(rectClose)
                anim.setEndValue(rectOpen)
            else:
                anim.finished.connect(self.hide)
                anim.setStartValue(rectOpen)
                anim.setEndValue(rectClose)

            self.anim = anim
            anim.start()

        def isFullWidth(self) -> bool:
            return self.width() >= self.root.width()

        def setFullWidth(self,value : bool = True):
            Logger.log(f"{self.objectName()}.setFullWidth({value})")
            if (self.isFullWidth() and value) or (not self.isFullWidth and not value):
                if value:
                    Logger.log(f"{self.objectName()} already expanded",1)
                    return
                Logger.log(f"{self.objectName()} already shrinked",1)
                return

            rectClose : QRect
            rectOpen : QRect
            match self.root.sideMode:
                case Root.LEFTMODE:
                    if self.isOpen():
                        rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.leftmode.open")
                        rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.fullwidth.open")
                    else:
                        rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.leftmode.close")
                        rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.fullwidth.close")
                case Root.RIGHTMODE:
                    if self.isOpen():
                        rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.rightmode.open")
                        rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.fullwidth.open")
                    else:
                        rectClose = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.rightmode.close")
                        rectOpen = self.root.ROOTELEMENTGEOMETRY.get(f"{self.objectName()}.fullwidth.close")
                case _:
                    InvalidSideModeError(self,self.setFullWidth.__name__)

            anim = QPropertyAnimation(self, b"geometry")
            anim.setEasingCurve(getattr(QEasingCurve.Type,SETTINGS.get("animation.easing")))
            anim.setDuration(SETTINGS.get("animation.duration"))
            if value:
                anim.setStartValue(rectClose)
                anim.setEndValue(rectOpen)
            else:
                anim.setStartValue(rectOpen)
                anim.setEndValue(rectClose)

            self.anim = anim
            anim.start()

    def __init__(self):
        super().__init__()
        self.styles = Styles(self,SETTINGS.get("style.folderName"))
        self.connections : typing.Dict[str,str] = FileManager.load(_DataFolderPath / "connections.json",detail="load connections",jsonFormat=True)
        
        # Main App Display Configure
        self.marginTop = 50
        self.marginBottom = 0

        geometry = self.screenGeometry
        geometry.setHeight(geometry.height() - (self.marginTop + self.marginBottom))
        self.setGeometry(geometry)
        self.setObjectName(self.__class__.__name__)

        Tool = Qt.WindowType.Tool
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(SETTINGS.get("appName"))

        self.sideMode = SETTINGS.get("defaultSideMode")

        # Sidebar
        self.sidebarWidth = 300
        self.sidebar = Root.Sidebar(self,self.sidebarWidth,self.height())

        # Panelcontainer
        self.panelcontainer = Root.PanelContainer(self,self.panelcontainerWidth,self.height())

        self.ROOTELEMENTGEOMETRY = DynamicDict({
                    "Sidebar":{
                        "leftmode":{
                            "close":QRect(-self.sidebarWidth,self.marginTop,self.sidebarWidth,self.elementHeight),
                            "open":QRect(0,self.marginTop,self.sidebarWidth,self.elementHeight)
                        },
                        "rightmode":{
                            "close":QRect(self.width(),self.marginTop,self.sidebarWidth,self.elementHeight),
                            "open":QRect(self.width() - self.sidebarWidth,self.marginTop,self.sidebarWidth,self.elementHeight)
                        }
                    },
                    "PanelContainer":{
                        "fullwidth":{
                            "close":QRect(0,self.height(),self.width(),self.elementHeight),
                            "open":QRect(0,self.marginTop,self.width(),self.elementHeight)
                        },
                        "leftmode":{
                            "close":QRect(self.sidebar.width(),self.height(),self.panelcontainerWidth,self.elementHeight),
                            "open":QRect(self.sidebar.width(),self.marginTop,self.panelcontainerWidth,self.elementHeight)
                        },
                        "rightmode":{
                            "close":QRect(0,self.height(),self.panelcontainerWidth,self.elementHeight),
                            "open":QRect(0,self.marginTop,self.panelcontainerWidth,self.elementHeight)
                        }
                    }
                })

        # Start + StyleApply
        self.startSetSide(self.sideMode)
        self.openSequence()

    @property
    def screenGeometry(self):
        return app.primaryScreen().geometry()

    @property
    def panelcontainerWidth(self):
        return self.width() - self.sidebar.width()

    @property
    def elementHeight(self):
        return self.height() - self.marginTop - self.marginBottom

    def allClosed(self):
        return not self.sidebar.isOpen() and not self.panelcontainer.isOpen()

    def allOpened(self):
        return self.sidebar.isOpen() and self.panelcontainer.isOpen()

    def startSetSide(self,side : str):
        do = True
        match side:
            case Root.LEFTMODE:
                self.sidebar.layout().setContentsMargins(5,5,0,5)
            case Root.RIGHTMODE:
                self.sidebar.layout().setContentsMargins(0,5,5,5)
            case _:
                InvalidSideModeError(self,self.startSetSide.__name__)
                do = False
        if do:
            self.sidebar.setGeometry(self.ROOTELEMENTGEOMETRY.get(f"{self.sidebar.objectName()}.{side}.close"))
            self.panelcontainer.setGeometry(self.ROOTELEMENTGEOMETRY.get(f"{self.panelcontainer.objectName()}.fullwidth.close"))
            self.sideMode = side
            self.styles.apply()

    def setSide(self,side : str):
        do = True
        match side:
            case Root.LEFTMODE:
                self.sidebar.layout().setContentsMargins(5,5,0,5)
            case Root.RIGHTMODE:
                self.sidebar.layout().setContentsMargins(0,5,5,5)
            case _:
                InvalidSideModeError(self,self.setSide.__name__)
                do = False
        if do:
            if self.sidebar.isOpen():
                self.sidebar.setGeometry(self.ROOTELEMENTGEOMETRY.get(f"{self.sidebar.objectName()}.{side}.open"))
                if self.panelcontainer.isOpen():
                    self.panelcontainer.setGeometry(self.ROOTELEMENTGEOMETRY.get(f"{self.panelcontainer.objectName()}.{side}.open"))
                else:
                    self.panelcontainer.setGeometry(self.ROOTELEMENTGEOMETRY.get(f"{self.panelcontainer.objectName()}.{side}.close"))
            else:
                self.sidebar.setGeometry(self.ROOTELEMENTGEOMETRY.get(f"{self.sidebar.objectName()}.{side}.close"))
                    
            self.sideMode = side
            Logger.log(f"to {side}")
            self.styles.apply()

    def openSequence(self):
        if self.allClosed():
            self.sidebar.setOpen()
            self.panelcontainer.setFullWidth(False)

        elif self.sidebar.isOpen() and not self.panelcontainer.isOpen():
            self.panelcontainer.setOpen()
        
        elif self.allOpened():
            self.sidebar.setOpen(False)
            self.panelcontainer.setFullWidth()
            
        elif not self.sidebar.isOpen() and self.panelcontainer.isOpen():
            self.panelcontainer.setOpen(False)

        Logger.log("openSequence()")

# HOTKEY
class HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def nativeEventFilter(self, eventType : typing.Any, message):
        msg = wintypes.MSG.from_address(message.__int__())
        WM_HOTKEY = 0x0312
        if msg.message == WM_HOTKEY:
            self.callback()
        return False, 0
    
# Setup
rootApp = Root()
app.setApplicationName(SETTINGS.get("appName"))

# hotkey trigger
user32 = ctypes.windll.user32
user32.RegisterHotKey(None, 1, SETTINGS.get("hotkeyTrigger.keyMod"),SETTINGS.get("hotkeyTrigger.key"))
hotkey_filter = HotkeyFilter(rootApp.openSequence)
app.installNativeEventFilter(hotkey_filter)

# Start
rootApp.show()
sys.exit(app.exec())
user32.UnregisterHotKey(None, 1)