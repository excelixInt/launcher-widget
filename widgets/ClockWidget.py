from core.widgets import *

class ClockWidget(BaseWidget):
    def __init__(self,title = "Clock"):
        super().__init__(title)
        
    def fillBodyContent(self, body):
        QVBoxLayout(body).setContentsMargins(0,0,0,0)
        # clock
        self.clockLabel = QLabel()
        self.clockLabel.setObjectName("clockLabel")
        self.clockLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.clockLabel.setFont(QFont())

        # date
        self.dateLabel = QLabel()
        self.dateLabel.setObjectName("dateLabel")
        self.dateLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.dateLabel.setFont(QFont())

        body.layout().addWidget(self.clockLabel)
        body.layout().addWidget(self.dateLabel)

        # timer update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

    def update_time(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        current_date = QDate.currentDate().toString("dddd, dd MMMM yyyy")

        self.clockLabel.setText(current_time)
        self.dateLabel.setText(current_date)