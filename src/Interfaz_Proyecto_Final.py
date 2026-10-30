from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(785, 594)

        # Central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Background image
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 801, 561))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("background.jpg"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("background_label")

        # Camera preview container
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(200, 60, 401, 281))
        self.groupBox.setStyleSheet("")
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("camera_group")

        # Camera preview
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 20, 381, 251))
        self.label.setText("")
        self.label.setScaledContents(True)
        self.label.setObjectName("camera_label")

        # Manual capture button
        self.Captura = QtWidgets.QPushButton(self.centralwidget)
        self.Captura.setGeometry(QtCore.QRect(330, 360, 121, 51))
        self.Captura.setAutoFillBackground(False)
        self.Captura.setStyleSheet(
            "background-color: rgb(170, 0, 255);"
        )
        self.Captura.setObjectName("capture_button")

        # Widget stacking order
        self.label_2.raise_()
        self.groupBox.raise_()
        self.Captura.raise_()

        MainWindow.setCentralWidget(self.centralwidget)

        # Menu bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 785, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # Status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Interface text
        self.retranslateUi(MainWindow)

        # Connect capture button to the main application method
        self.Captura.clicked.connect(
            MainWindow.realizar_captura
        )

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle(
            translate(
                "MainWindow",
                "Raspberry Pi Security Camera"
            )
        )

        self.groupBox.setTitle(
            translate(
                "MainWindow",
                "Camera"
            )
        )

        self.Captura.setText(
            translate(
                "MainWindow",
                "Capture"
            )
        )