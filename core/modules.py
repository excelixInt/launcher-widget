# utils
import sys , os , json , typing , math , webbrowser , colorama , requests , subprocess , numpy
import pathlib as pl
import ctypes
from ctypes import wintypes

# PySide6
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,QHBoxLayout,QLayout,QGridLayout,QScrollArea,QSizePolicy,QGraphicsBlurEffect,
    QStackedWidget
    )

from PySide6.QtGui import (
    Qt ,
    QPixmap,
    QPainter,
    QPainterPath,
    QFont
    )

from PySide6.QtCore import (
    QAbstractNativeEventFilter ,
    QRect , 
    QPoint , 
    QSize,
    QMargins,
    QPropertyAnimation,
    QDate,QTime,QTimer,QEasingCurve,QParallelAnimationGroup
    )

from PySide6.QtSvg import (
    QtSvg,QSvgRenderer,QSvgGenerator
)


