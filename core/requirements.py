from core.modules import *

app = QApplication(sys.argv)

# folders
_RootPath = pl.Path(__file__).resolve().parent.parent
_DataFolderPath = _RootPath / "data"
_WidgetsFolderPath = _RootPath / "widgets"

_ResourcesFolderPath = _RootPath / "res"
_IconFolderPath = _ResourcesFolderPath / "icons"

# files
_SettingsPath =  _RootPath / "settings.json"

def __rootpath__(path : pl.Path | str):
    return _RootPath / path

# create folders
_DataFolderPath.mkdir(exist_ok=True)
_WidgetsFolderPath.mkdir(exist_ok=True)

suffixes = [".svg",".png",".jpg",".jpeg",".webp"]

class _Icons:
    def __init__(self):
        for subfolder in os.listdir(_IconFolderPath):
            for iconFile in os.listdir(_IconFolderPath / subfolder):
                attr = iconFile
                for suffix in suffixes:
                    attr = attr.removesuffix(suffix)
                setattr(self,attr,QPixmap(_IconFolderPath / subfolder / iconFile))

class Logger:
    class Prefix:
        LOG = "[LOG]"
        WARN = "[WARNING]"
        ERROR = "[ERROR]"
        ASK = "[?]"
        INFO = "[INFO]"
        FATALERROR = "[FATALERROR]"

        UNDEFINED = "[UNDEFINED]"

    class Color:
        NORMAL = colorama.Fore.WHITE
        GREEN = colorama.Fore.GREEN
        YELLOW = colorama.Fore.YELLOW
        RED = colorama.Fore.RED

    @staticmethod
    def log(message : str,logType : int | str = 0) -> None:
        match logType:
            case Logger.Prefix.LOG | 0:
                prefix = Logger.Prefix.LOG
                prefixCol = Logger.Color.GREEN
            case Logger.Prefix.WARN | 1:
                prefix = Logger.Prefix.WARN
                prefixCol = Logger.Color.YELLOW
            case Logger.Prefix.ERROR | 2:
                prefix = Logger.Prefix.ERROR
                prefixCol = Logger.Color.RED
            case Logger.Prefix.ASK | 3:
                prefix = Logger.Prefix.ASK
                prefixCol = Logger.Color.YELLOW
            case Logger.Prefix.INFO | 4:
                prefix = Logger.Prefix.INFO
                prefixCol = Logger.Color.GREEN
            case Logger.Prefix.FATALERROR | "fatalerror":
                prefix = Logger.Prefix.FATALERROR
                prefixCol = Logger.Color.RED
            case _:
                prefix = Logger.Prefix.UNDEFINED
                prefixCol = Logger.Color.NORMAL

        print(f"{prefixCol}{prefix} {Logger.Color.NORMAL}{message}")

    @staticmethod
    def ask(message : str) -> str:
        return input(f"{Logger.Color.YELLOW}{Logger.Prefix.ASK} {Logger.Color.NORMAL}{message}")

class ExceptionLogger(Logger):
    def KeyError(key : str,detail : str = None):
        ExceptionLogger.exception(f"KeyError: {key}",KeyError,detail)
    def OSError(error : str,detail : str = None):
        ExceptionLogger.exception(f"System I/O Error occurred: {error}",OSError,detail)

    def exception(message : str,exceptionType : Exception | str = Exception,detail : str = None):
        if not isinstance(exceptionType,str) and isinstance(exceptionType,type):
            exceptionType = exceptionType().__class__.__name__
        ExceptionLogger.log(f"{message} | {exceptionType=} | {detail=}",2)
            

T = typing.TypeVar("T")    
TY = typing.TypeVar("TY",bound=type) 
class FileManager[T]:
    path : str = None
    class msg:
        def TryLoadFile(path):
            Logger.log(f"try load {path=}.",0)
        def TrySaveFile(path):
            Logger.log(f"try save {path=}.",0)

        def LoadSucceed():
            Logger.log(f"load succeed")
        def LoadFailed():
            Logger.log(f"load failed")

        def SaveSucceed():
            Logger.log(f"load succeed")
        def SaveFailed():
            Logger.log(f"load failed")

        def FileNotFound(path : str):
            Logger.log(f"cannot find {path=}.",1)
        def FileFounded(path : str):
            Logger.log(f"{path=} founded.",4)

        def FilePathNotSetError():
            ExceptionLogger.exception("file need to set","FilePathNotSetError","FileLoader.load need path argument for load the file. for example: 'folder/subfolder/file.txt'.")

        def FileNotFoundError(path : str,detail : str = None):
            ExceptionLogger.exception(f"{path=} Not found.",FileNotFoundError,detail)
        def PermissionError(path : str,detail : str = None):
            ExceptionLogger.exception(f"{path=} Do not have permission to access.",PermissionError,detail)
        def UnicodeDecodeError(path : str,detail : str = None):
            ExceptionLogger.exception(f"{path=} Encoding mismatch. Ensure the file is saved in UTF-8 format.",UnicodeDecodeError,detail)

    @staticmethod
    def load(
        path : pl.Path | str = None,
        detail : str | None = None,
        failReturn : T = None,
        jsonFormat : bool = False,
        customObjectClass : TY | type | None = None,
        encoding : str | None = None
        ):
        if path is None:
            if not FileManager.path:
                FileManager.msg.FilePathNotSetError();FileManager.msg.LoadFailed()
                return failReturn
            path = FileManager.path
        try:
            FileManager.msg.TryLoadFile(path)
            with open(path,"r",encoding=encoding) as file:
                if jsonFormat:
                    data = json.load(file)
                else:
                    data = file.read()

            if isinstance(customObjectClass,type):
                data = customObjectClass(data)

        except FileNotFoundError:
            FileManager.msg.FileNotFoundError(path,detail);FileManager.msg.LoadFailed()
        except PermissionError:
            FileManager.msg.PermissionError(path,detail);FileManager.msg.LoadFailed()
        except UnicodeDecodeError:
            FileManager.msg.UnicodeDecodeError(path,detail);FileManager.msg.LoadFailed()
        except OSError as err:
            ExceptionLogger.OSError(err,detail);FileManager.msg.LoadFailed()
        except KeyError as err:
            ExceptionLogger.KeyError(err,detail);FileManager.msg.LoadFailed()
        except Exception as err:
            ExceptionLogger.exception(err,detail=detail);FileManager.msg.LoadFailed()
        else:
            FileManager.msg.LoadSucceed()
            return data

    @staticmethod
    def save(
        data : str | typing.Any,
        path : pl.Path | str = None,
        detail : str | None = None,
        jsonFormat : bool = False,
        encoding : str | None = None
        ):
        if path is None:
            if not FileManager.path:
                FileManager.msg.FilePathNotSetError();FileManager.msg.SaveFailed()
                return False
            path = FileManager.path
        try:
            FileManager.msg.TrySaveFile(path)
            with open(path,"w",encoding=encoding) as file:
                if jsonFormat:
                    json.dump(data,file)
                else:
                    file.write(data)

        except Exception as err:
            ExceptionLogger.exception(err,Exception,detail);FileManager.msg.SaveFailed()
        else:
            FileManager.msg.SaveSucceed()
            return True

    @staticmethod
    def find(path : pl.Path | str = None):
        if path is None:
            if not FileManager.path:
                FileManager.msg.FilePathNotSetError()
            path = FileManager.path
        v = pl.Path(path).exists()
        if v:
            FileManager.msg.FileFounded(path)
        else:
            FileManager.msg.FileNotFound(path)
        return v

JSONType = typing.Dict[str,typing.Any] | typing.List | str | int | float | bool 
class JSONDict:
    def __init__(self,pathOrObject : pl.Path | JSONType = None,default : JSONType = None):
        self._data = default
        if not pathOrObject:
            return
        if isinstance(pathOrObject,pl.Path):
            self.load(pathOrObject)
            return
        self._data = pathOrObject

    def __getitem__(self, key):
        return self._data[key]

    def get(self,path : str): 
        return dictGetter(self._data,path)

    def set(self,path : str,value : typing.Any):
        dictSetter(self._data,path,value)

    def load(self,path : pl.Path | str):
        self._data = FileManager.load(path,f"load {path} to {self.__class__.__name__}",self._data,True)

    def save(self,path : pl.Path | str):
        FileManager.save(self._data,path,f"save {self.__class__.__name__} to {path}",True)

DT = typing.TypeVar("DT",bound=dict)
def dictGetter(dictObject : DT | dict,path : str):
    keys = path.split(".")
    for i in range(len(keys)):
        v = dictObject[keys[i]]
        dictObject = v
    return dictObject

def dictSetter(dictObject : DT | dict,path : str,value : typing.Any):
    keys = path.split(".")
    last = keys[-1]
    keys.remove(last)
    for i in range(len(keys)):
        v = dictObject[keys[i]]
        dictObject = v
    dictObject[last] = value

def InvalidSideModeError(root,detail : str):
    ExceptionLogger.exception(f"Invalid sideMode {root.sideMode}",detail=detail)

class Styles:
    def __init__(self,root : QWidget,themeFolder : str = None):
        self.root = root
        self.themes = __rootpath__("themes")
        self.themes.mkdir(exist_ok=True)

        self.widgets = STYLEDEFAULT_WIDGETS
        self.leftmode = STYLEDEFAULT_LEFTMODE
        self.rightmode = STYLEDEFAULT_RIGHTMODE

        self.themeFolder = themeFolder
        self.load()

    def load(self):
        Logger.log("style loading")
        self.widgets = FileManager.load(self.widgetsPath,"load widgets style",self.widgets,encoding="utf-8")
        self.leftmode = FileManager.load(self.leftmodePath,"leftmode widgets style",self.leftmode,encoding="utf-8")
        self.rightmode = FileManager.load(self.rightmodePath,"rightmode widgets style",self.rightmode,encoding="utf-8")

    @property
    def widgetsPath(self):
        return __rootpath__(self.themes / self.themeFolder / "widgets.qss")
    @property
    def leftmodePath(self):
        return __rootpath__(self.themes / self.themeFolder / "leftmode.qss")
    @property
    def rightmodePath(self):
        return __rootpath__(self.themes / self.themeFolder / "rightmode.qss")

    def apply(self):
        stylesheet = ""
        match self.root.sideMode:
            case self.root.LEFTMODE:
                Logger.log(f"style apply to {self.root.sideMode=}")
                stylesheet = f"{self.leftmode}\n{self.widgets}"
            case self.root.RIGHTMODE:
                Logger.log(f"style apply to {self.root.sideMode=}")
                stylesheet = f"{self.rightmode}\n{self.widgets}"
            case _:
                Logger.log(f"failed to apply style {self.root.sideMode=}")
                InvalidSideModeError(self.root,f"when applying style using {self.__class__.__name__}.apply()")
                return
            
        self.root.setStyleSheet(stylesheet)
        Logger.log(f"{self.__class__.__name__}.apply() succeed")
                

# default
SETTINGS = JSONDict(_SettingsPath)
ICONS = _Icons()

SETTINGSDEFAULT = {
    "appName":"ExceLauncher",
    "themeFolder":"default",
    "defaultSideMode":"rightmode",
    "animation":{
        "duration":200,
        "easing":"OutBack"
    },
    "hotkeyTrigger":{
        "keyMod":1,
        "key":79
    }
}   

STYLEDEFAULT_WIDGETS = """

"""
STYLEDEFAULT_LEFTMODE = """

"""
STYLEDEFAULT_RIGHTMODE = """

"""