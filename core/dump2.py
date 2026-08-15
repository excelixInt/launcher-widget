import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QTabBar, QStackedWidget, 
                             QLabel, QPushButton, QGraphicsOpacityEffect)
from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, QParallelAnimationGroup

class AnimatedTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Create top bar and the content stack
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_bar = QTabBar()
        self.stack = QStackedWidget()
        
        self.layout.addWidget(self.tab_bar)
        self.layout.addWidget(self.stack)
        
        # 2. Track animation state
        self.current_index = 0
        self.anim_group = None
        
        # Connect tab clicks to custom animation trigger
        self.tab_bar.currentChanged.connect(self.trigger_transition)

    def addTab(self, widget, label):
        self.tab_bar.addTab(label)
        self.stack.addWidget(widget)
        # Hide pages initially except the first one
        if self.stack.count() > 1:
            widget.hide()

    def trigger_transition(self, next_index):
        if next_index == self.current_index:
            return
            
        old_widget = self.stack.widget(self.current_index)
        new_widget = self.stack.widget(next_index)
        
        # Determine sliding direction based on tab index order
        width = self.stack.width()
        if next_index > self.current_index:
            # Slide left (new tab comes from right side)
            start_pos_new = QPoint(width, 0)
            end_pos_old = QPoint(-width, 0)
        else:
            # Slide right (new tab comes from left side)
            start_pos_new = QPoint(-width, 0)
            end_pos_old = QPoint(width, 0)
            
        # Position and display the incoming widget
        new_widget.move(start_pos_new)
        new_widget.show()
        new_widget.raise_()

        # 3. Create the parallel animations
        anim_old = QPropertyAnimation(old_widget, b"pos", self)
        anim_old.setDuration(350)
        anim_old.setStartValue(QPoint(0, 0))
        anim_old.setEndValue(end_pos_old)
        anim_old.setEasingCurve(QEasingCurve.Type.InOutQuad)

        anim_new = QPropertyAnimation(new_widget, b"pos", self)
        anim_new.setDuration(350)
        anim_new.setStartValue(start_pos_new)
        anim_new.setEndValue(QPoint(0, 0))
        anim_new.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 4. Group and execute
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(anim_old)
        self.anim_group.addAnimation(anim_new)
        
        # Clean up layout state when the movement ends
        self.anim_group.finished.connect(lambda: self.finalize_transition(next_index, old_widget))
        self.anim_group.start()

    def finalize_transition(self, index, old_widget):
        old_widget.hide()
        self.stack.setCurrentIndex(index)
        self.current_index = index


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animated Tab Widget")
        self.resize(500, 400)

        # Container
        self.tabs = AnimatedTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab 1
        self.tab1 = QWidget()
        self.tab1.setStyleSheet("background-color: #34495e; color: white;")
        layout1 = QVBoxLayout(self.tab1)
        layout1.addWidget(QLabel("<h1>Home View</h1>"), )
        layout1.addWidget(QPushButton("Action Button"))

        # Tab 2
        self.tab2 = QWidget()
        self.tab2.setStyleSheet("background-color: #2c3e50; color: white;")
        layout2 = QVBoxLayout(self.tab2)
        layout2.addWidget(QLabel("<h1>Settings View</h1>"))

        # Tab 3
        self.tab3 = QWidget()
        self.tab3.setStyleSheet("background-color: #bbbbbb; color: black;")
        layout3 = QVBoxLayout(self.tab3)
        layout3.addWidget(QLabel("<h1>About View/h1>"))

        # Add to custom controller
        self.tabs.addTab(self.tab1, "Home")
        self.tabs.addTab(self.tab2, "Settings")
        self.tabs.addTab(self.tab3, "About")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
