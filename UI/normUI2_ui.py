# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'normUI2.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTextBrowser, QVBoxLayout, QWidget)
import resourses_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(552, 589)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"selection-color: rgb(255, 255, 255);")
        MainWindow.setIconSize(QSize(30, 30))
        MainWindow.setDocumentMode(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setBaseSize(QSize(0, 0))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setBold(False)
        font1.setStrikeOut(False)
        font1.setKerning(True)
        self.centralwidget.setFont(font1)
        self.centralwidget.setStyleSheet(u"background-color: rgb(54, 57, 63);")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.app_tab = QTabWidget(self.centralwidget)
        self.app_tab.setObjectName(u"app_tab")
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(12)
        font2.setBold(False)
        font2.setItalic(False)
        self.app_tab.setFont(font2)
        self.app_tab.setMouseTracking(False)
        self.app_tab.setStyleSheet(u"\n"
"QTabBar::tab, \n"
"QTabBar::tab:hover\n"
"{\n"
"border: 1px solid rgba(105, 118, 132, 255);\n"
"selection-color: rgb(255, 255, 255);\n"
"\n"
"color: rgb(98, 114, 164);\n"
"background-color: rgb(47, 49, 54);\n"
"}\n"
"\n"
"")
        self.app_tab.setElideMode(Qt.ElideLeft)
        self.app_tab.setDocumentMode(True)
        self.app_tab.setTabsClosable(False)
        self.app_tab.setMovable(False)
        self.main_tab = QWidget()
        self.main_tab.setObjectName(u"main_tab")
        self.main_tab.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.main_tab.setLayoutDirection(Qt.LeftToRight)
        self.main_tab.setStyleSheet(u"background-color: rgb(54, 57, 63);")
        self.gridLayout_2 = QGridLayout(self.main_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 1, 3, 1, 2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.episodeLine = QLineEdit(self.main_tab)
        self.episodeLine.setObjectName(u"episodeLine")
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(12)
        self.episodeLine.setFont(font3)
        self.episodeLine.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"padding-bottom:7px;")

        self.verticalLayout_3.addWidget(self.episodeLine)


        self.gridLayout_2.addLayout(self.verticalLayout_3, 7, 1, 1, 4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.faqButton = QPushButton(self.main_tab)
        self.faqButton.setObjectName(u"faqButton")
        self.faqButton.setEnabled(True)
        self.faqButton.setFont(font2)
        self.faqButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 12pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/icons/res/ICONS/faq_question_icon_149479.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.faqButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.faqButton)

        self.siteButton = QPushButton(self.main_tab)
        self.siteButton.setObjectName(u"siteButton")
        self.siteButton.setFont(font2)
        self.siteButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 12pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/icons/res/ICONS/web_120072.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.siteButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.siteButton)

        self.hardfolderButton = QPushButton(self.main_tab)
        self.hardfolderButton.setObjectName(u"hardfolderButton")
        self.hardfolderButton.setFont(font2)
        self.hardfolderButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 12pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/icons/res/ICONS/folder_storage_file_icon_193553.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.hardfolderButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.hardfolderButton)


        self.gridLayout_2.addLayout(self.horizontalLayout, 15, 1, 2, 4)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.versionLabel = QLabel(self.main_tab)
        self.versionLabel.setObjectName(u"versionLabel")
        self.versionLabel.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.versionLabel.sizePolicy().hasHeightForWidth())
        self.versionLabel.setSizePolicy(sizePolicy1)
        self.versionLabel.setLayoutDirection(Qt.LeftToRight)
        self.versionLabel.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.versionLabel.setWordWrap(False)

        self.verticalLayout_4.addWidget(self.versionLabel)


        self.gridLayout_2.addLayout(self.verticalLayout_4, 17, 1, 1, 4)

        self.pushButton_rick = QPushButton(self.main_tab)
        self.pushButton_rick.setObjectName(u"pushButton_rick")
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(20)
        font4.setBold(True)
        font4.setStrikeOut(False)
        self.pushButton_rick.setFont(font4)
        self.pushButton_rick.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.gridLayout_2.addWidget(self.pushButton_rick, 0, 1, 2, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.stateLabel = QLabel(self.main_tab)
        self.stateLabel.setObjectName(u"stateLabel")
        self.stateLabel.setFont(font3)
        self.stateLabel.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"\n"
"")
        self.stateLabel.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.stateLabel)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 13, 1, 1, 4)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.progressBar = QProgressBar(self.main_tab)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"	background-color: rgb(98, 114, 164);\n"
"	color: rgb(200, 200, 200);\n"
"	border-style: none;\n"
"	border-radius: 20px;\n"
"	text-align: center;\n"
"}\n"
"QProgressBar::chunk{	\n"
"	border-radius: 20px;\n"
"	\n"
"	background-color: qlineargradient(spread:pad, x1:0.006, y1:0.556, x2:1, y2:0.522727, stop:0 rgba(54, 57, 63, 255), stop:1 rgba(54, 57, 63, 255));\n"
"}")
        self.progressBar.setValue(0)

        self.verticalLayout_8.addWidget(self.progressBar)


        self.gridLayout_2.addLayout(self.verticalLayout_8, 10, 1, 1, 4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_6)

        self.logo_check = QCheckBox(self.main_tab)
        self.logo_check.setObjectName(u"logo_check")
        font5 = QFont()
        font5.setFamilies([u"Segoe UI"])
        font5.setPointSize(12)
        font5.setBold(True)
        self.logo_check.setFont(font5)
        self.logo_check.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")
        self.logo_check.setChecked(True)

        self.verticalLayout_12.addWidget(self.logo_check)

        self.nvencCheck = QCheckBox(self.main_tab)
        self.nvencCheck.setObjectName(u"nvencCheck")
        self.nvencCheck.setFont(font5)
        self.nvencCheck.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")
        self.nvencCheck.setChecked(False)

        self.verticalLayout_12.addWidget(self.nvencCheck)

        self.codec = QCheckBox(self.main_tab)
        self.codec.setObjectName(u"codec")
        self.codec.setFont(font5)
        self.codec.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;")

        self.verticalLayout_12.addWidget(self.codec)

        self.hardCheck = QCheckBox(self.main_tab)
        self.hardCheck.setObjectName(u"hardCheck")
        self.hardCheck.setFont(font5)
        self.hardCheck.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")
        self.hardCheck.setChecked(True)

        self.verticalLayout_12.addWidget(self.hardCheck)


        self.horizontalLayout_4.addLayout(self.verticalLayout_12)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_5)

        self.modeLabel = QLabel(self.main_tab)
        self.modeLabel.setObjectName(u"modeLabel")
        self.modeLabel.setFont(font3)
        self.modeLabel.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")
        self.modeLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_11.addWidget(self.modeLabel)

        self.modeBox = QComboBox(self.main_tab)
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.setObjectName(u"modeBox")
        self.modeBox.setEnabled(True)
        self.modeBox.setFont(font3)
        self.modeBox.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"")

        self.verticalLayout_11.addWidget(self.modeBox)


        self.horizontalLayout_4.addLayout(self.verticalLayout_11)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_4)

        self.bitrateLabel = QLabel(self.main_tab)
        self.bitrateLabel.setObjectName(u"bitrateLabel")
        self.bitrateLabel.setFont(font3)
        self.bitrateLabel.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.verticalLayout_10.addWidget(self.bitrateLabel)

        self.bitrateBox = QComboBox(self.main_tab)
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.addItem("")
        self.bitrateBox.setObjectName(u"bitrateBox")
        self.bitrateBox.setEnabled(True)
        self.bitrateBox.setFont(font3)
        self.bitrateBox.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"")

        self.verticalLayout_10.addWidget(self.bitrateBox)


        self.horizontalLayout_4.addLayout(self.verticalLayout_10)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_13)

        self.startButton = QPushButton(self.main_tab)
        self.startButton.setObjectName(u"startButton")
        font6 = QFont()
        font6.setFamilies([u"Segoe UI"])
        font6.setPointSize(20)
        font6.setBold(False)
        font6.setItalic(False)
        self.startButton.setFont(font6)
        self.startButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 20pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")

        self.verticalLayout_9.addWidget(self.startButton)

        self.verticalSpacer_22 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_22)

        self.stopButton = QPushButton(self.main_tab)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setEnabled(False)
        self.stopButton.setFont(font6)
        self.stopButton.setMouseTracking(False)
        self.stopButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 20pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        self.stopButton.setCheckable(False)

        self.verticalLayout_9.addWidget(self.stopButton)

        self.verticalSpacer_18 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_18)


        self.horizontalLayout_4.addLayout(self.verticalLayout_9)


        self.gridLayout_2.addLayout(self.horizontalLayout_4, 3, 1, 1, 4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_7)

        self.soundPath = QLineEdit(self.main_tab)
        self.soundPath.setObjectName(u"soundPath")
        font7 = QFont()
        font7.setFamilies([u"Segoe UI"])
        font7.setPointSize(11)
        self.soundPath.setFont(font7)
        self.soundPath.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"padding-bottom:7px;")
        self.soundPath.setDragEnabled(True)

        self.verticalLayout.addWidget(self.soundPath)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.rawPath = QLineEdit(self.main_tab)
        self.rawPath.setObjectName(u"rawPath")
        self.rawPath.setFont(font7)
        self.rawPath.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"padding-bottom:7px;")
        self.rawPath.setDragEnabled(True)

        self.verticalLayout.addWidget(self.rawPath)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.subPath = QLineEdit(self.main_tab)
        self.subPath.setObjectName(u"subPath")
        self.subPath.setFont(font7)
        self.subPath.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"padding-bottom:7px;")
        self.subPath.setDragEnabled(True)

        self.verticalLayout.addWidget(self.subPath)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.softPath = QLineEdit(self.main_tab)
        self.softPath.setObjectName(u"softPath")
        self.softPath.setFont(font7)
        self.softPath.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"padding-bottom:7px;")
        self.softPath.setDragEnabled(True)

        self.verticalLayout.addWidget(self.softPath)

        self.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_19)


        self.horizontalLayout_5.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_14)

        self.soundButton = QPushButton(self.main_tab)
        self.soundButton.setObjectName(u"soundButton")
        self.soundButton.setMinimumSize(QSize(30, 30))
        font8 = QFont()
        font8.setFamilies([u"Segoe UI"])
        font8.setPointSize(8)
        font8.setBold(False)
        font8.setItalic(False)
        self.soundButton.setFont(font8)
        self.soundButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 8pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/icons/res/ICONS/folder.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.soundButton.setIcon(icon3)

        self.verticalLayout_2.addWidget(self.soundButton)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_9)

        self.rawButton = QPushButton(self.main_tab)
        self.rawButton.setObjectName(u"rawButton")
        self.rawButton.setMinimumSize(QSize(30, 30))
        self.rawButton.setFont(font8)
        self.rawButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 8pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}color: rgb(205, 206, 208);")
        self.rawButton.setIcon(icon3)

        self.verticalLayout_2.addWidget(self.rawButton)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_10)

        self.subButton = QPushButton(self.main_tab)
        self.subButton.setObjectName(u"subButton")
        self.subButton.setMinimumSize(QSize(30, 30))
        self.subButton.setFont(font8)
        self.subButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 8pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        self.subButton.setIcon(icon3)

        self.verticalLayout_2.addWidget(self.subButton)

        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_11)

        self.softButton = QPushButton(self.main_tab)
        self.softButton.setObjectName(u"softButton")
        self.softButton.setMinimumSize(QSize(30, 30))
        self.softButton.setFont(font8)
        self.softButton.setStyleSheet(u"QPushButton{\n"
"border: none;\n"
"padding-top: 5px;\n"
"padding-top: 3px;\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"font: 75 8pt \"Segoe UI\";\n"
"color: rgb(98, 114, 164);\n"
"}\n"
"QPushButton:hover{\n"
"background-color: rgb(62, 65, 72);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-buttom: 3px solid  rgb(37, 40, 44);\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: rgb(44, 47, 52);\n"
"border-left: 1px solid  rgb(37, 40, 44);\n"
"border-right: 1px solid  rgb(37, 40, 44);\n"
"border-top: 3px solid  rgb(37, 40, 44);\n"
"border-buttom: none;\n"
"padding-top: -5px;\n"
"}")
        self.softButton.setIcon(icon3)

        self.verticalLayout_2.addWidget(self.softButton)

        self.verticalSpacer_20 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_20)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)


        self.gridLayout_2.addLayout(self.horizontalLayout_5, 5, 1, 1, 4)

        self.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_16, 11, 1, 1, 4)

        self.verticalSpacer_17 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_17, 14, 1, 1, 4)

        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_15, 9, 1, 1, 4)

        self.verticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_21, 6, 1, 1, 4)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_8, 4, 1, 1, 4)

        self.verticalSpacer_23 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_23, 2, 1, 1, 4)

        self.app_tab.addTab(self.main_tab, "")
        self.folder_tab = QWidget()
        self.folder_tab.setObjectName(u"folder_tab")
        self.folder_tab.setMouseTracking(True)
        self.folder_tab.setLayoutDirection(Qt.LeftToRight)
        self.folder_tab.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(self.folder_tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tempLabel = QLabel(self.folder_tab)
        self.tempLabel.setObjectName(u"tempLabel")
        font9 = QFont()
        font9.setFamilies([u"Segoe UI"])
        font9.setPointSize(20)
        self.tempLabel.setFont(font9)
        self.tempLabel.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"")
        self.tempLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.tempLabel, 0, 0, 1, 1)

        self.app_tab.addTab(self.folder_tab, "")
        self.settings_tab = QWidget()
        self.settings_tab.setObjectName(u"settings_tab")
        self.gridLayout_6 = QGridLayout(self.settings_tab)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label = QLabel(self.settings_tab)
        self.label.setObjectName(u"label")
        font10 = QFont()
        font10.setFamilies([u"Segoe UI"])
        font10.setPointSize(20)
        font10.setBold(False)
        self.label.setFont(font10)
        self.label.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"border-bottom: 2px solid rgba(105, 118, 132, 255);\n"
"")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.label, 0, 0, 1, 1)

        self.app_tab.addTab(self.settings_tab, "")
        self.whatsnew_tab = QWidget()
        self.whatsnew_tab.setObjectName(u"whatsnew_tab")
        self.gridLayout_4 = QGridLayout(self.whatsnew_tab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.textBrowser = QTextBrowser(self.whatsnew_tab)
        self.textBrowser.setObjectName(u"textBrowser")
        font11 = QFont()
        font11.setFamilies([u"Segoe UI"])
        self.textBrowser.setFont(font11)
        self.textBrowser.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.gridLayout_4.addWidget(self.textBrowser, 0, 0, 1, 1)

        self.app_tab.addTab(self.whatsnew_tab, "")
        self.dev_tab = QWidget()
        self.dev_tab.setObjectName(u"dev_tab")
        self.gridLayout_5 = QGridLayout(self.dev_tab)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_5, 0, 1, 1, 1)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.enableDevMode = QCheckBox(self.dev_tab)
        self.enableDevMode.setObjectName(u"enableDevMode")
        self.enableDevMode.setFont(font3)
        self.enableDevMode.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.verticalLayout_5.addWidget(self.enableDevMode)

        self.folderAutodecting = QCheckBox(self.dev_tab)
        self.folderAutodecting.setObjectName(u"folderAutodecting")
        self.folderAutodecting.setEnabled(False)
        self.folderAutodecting.setFont(font3)
        self.folderAutodecting.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.verticalLayout_5.addWidget(self.folderAutodecting)

        self.videoBitrateAutodetectibg = QCheckBox(self.dev_tab)
        self.videoBitrateAutodetectibg.setObjectName(u"videoBitrateAutodetectibg")
        self.videoBitrateAutodetectibg.setEnabled(False)
        self.videoBitrateAutodetectibg.setFont(font3)
        self.videoBitrateAutodetectibg.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.verticalLayout_5.addWidget(self.videoBitrateAutodetectibg)

        self.enableLogging = QCheckBox(self.dev_tab)
        self.enableLogging.setObjectName(u"enableLogging")
        self.enableLogging.setEnabled(False)
        self.enableLogging.setFont(font3)
        self.enableLogging.setStyleSheet(u"color: rgb(98, 114, 164);\n"
"background-color: rgb(0, 0, 0, 0);\n"
"border:none;\n"
"")

        self.verticalLayout_5.addWidget(self.enableLogging)


        self.gridLayout_5.addLayout(self.verticalLayout_5, 0, 0, 1, 1)

        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_12, 2, 0, 1, 1)

        self.app_tab.addTab(self.dev_tab, "")

        self.gridLayout_3.addWidget(self.app_tab, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.app_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AniBaza converter", None))
        self.episodeLine.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0440\u0435\u043b\u0438\u0437\u0430 ([AniBaza] Kaguya-sama Love is War TV [02])", None))
#if QT_CONFIG(whatsthis)
        self.faqButton.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" text-decoration: underline;\">\u0410 \u0448\u043e \u043a\u0430\u043a \u0434\u0435\u043b\u0430\u0442\u044c? FAQ</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.faqButton.setText(QCoreApplication.translate("MainWindow", u" \u0418\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u044f \u0442\u0443\u0442 ", None))
#if QT_CONFIG(whatsthis)
        self.siteButton.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>\u0430\u044b\u0430\u044b\u0432\u0430</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.siteButton.setText(QCoreApplication.translate("MainWindow", u" \u041d\u0430 \u0441\u0430\u0439\u0442 ", None))
#if QT_CONFIG(whatsthis)
        self.hardfolderButton.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>\u0430\u044b\u0430\u044b\u0432\u0430</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.hardfolderButton.setText(QCoreApplication.translate("MainWindow", u" \u041f\u0430\u043f\u043a\u0430 Hardsub ", None))
        self.versionLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Version 2.0 (Einsein) by Miki-san</span></p></body></html>", None))
#if QT_CONFIG(whatsthis)
        self.pushButton_rick.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>asdasdasd</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pushButton_rick.setText(QCoreApplication.translate("MainWindow", u"AniBaza converter <- click here :3", None))
        self.stateLabel.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u043e\u043b\u043d\u044f\u0439 \u043f\u043e\u043b\u044f!", None))
        self.logo_check.setText(QCoreApplication.translate("MainWindow", u"\u041b\u043e\u0433\u043e", None))
        self.nvencCheck.setText(QCoreApplication.translate("MainWindow", u"Nvenc", None))
        self.codec.setText(QCoreApplication.translate("MainWindow", u"HEVC", None))
        self.hardCheck.setText(QCoreApplication.translate("MainWindow", u"Sub", None))
        self.modeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">\u0427\u0442\u043e \u0441\u043e\u0431\u0438\u0440\u0430\u0435\u043c:</span></p></body></html>", None))
        self.modeBox.setItemText(0, QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0444\u0442 \u0438 \u0445\u0430\u0440\u0434", None))
        self.modeBox.setItemText(1, QCoreApplication.translate("MainWindow", u"\u0422\u043e\u043b\u044c\u043a\u043e \u0441\u043e\u0444\u0442", None))
        self.modeBox.setItemText(2, QCoreApplication.translate("MainWindow", u"\u0422\u043e\u043b\u044c\u043a\u043e \u0445\u0430\u0440\u0434", None))
        self.modeBox.setItemText(3, QCoreApplication.translate("MainWindow", u"\u0414\u043b\u044f \u0445\u0430\u0440\u0434\u0441\u0430\u0431\u0431\u0435\u0440\u043e\u0432", None))

        self.bitrateLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600; font-style:italic;\">\u0411\u0438\u0442\u0440\u0435\u0439\u0442</span>, kbps:</p></body></html>", None))
        self.bitrateBox.setItemText(0, QCoreApplication.translate("MainWindow", u"1000", None))
        self.bitrateBox.setItemText(1, QCoreApplication.translate("MainWindow", u"1500", None))
        self.bitrateBox.setItemText(2, QCoreApplication.translate("MainWindow", u"2000", None))
        self.bitrateBox.setItemText(3, QCoreApplication.translate("MainWindow", u"2500", None))
        self.bitrateBox.setItemText(4, QCoreApplication.translate("MainWindow", u"3000", None))
        self.bitrateBox.setItemText(5, QCoreApplication.translate("MainWindow", u"3500", None))
        self.bitrateBox.setItemText(6, QCoreApplication.translate("MainWindow", u"4000", None))
        self.bitrateBox.setItemText(7, QCoreApplication.translate("MainWindow", u"4500", None))
        self.bitrateBox.setItemText(8, QCoreApplication.translate("MainWindow", u"5000", None))
        self.bitrateBox.setItemText(9, QCoreApplication.translate("MainWindow", u"5500", None))
        self.bitrateBox.setItemText(10, QCoreApplication.translate("MainWindow", u"6000", None))
        self.bitrateBox.setItemText(11, QCoreApplication.translate("MainWindow", u"6500", None))
        self.bitrateBox.setItemText(12, QCoreApplication.translate("MainWindow", u"7000", None))
        self.bitrateBox.setItemText(13, QCoreApplication.translate("MainWindow", u"7500", None))
        self.bitrateBox.setItemText(14, QCoreApplication.translate("MainWindow", u"8000", None))
        self.bitrateBox.setItemText(15, QCoreApplication.translate("MainWindow", u"9000", None))
        self.bitrateBox.setItemText(16, QCoreApplication.translate("MainWindow", u"10000", None))
        self.bitrateBox.setItemText(17, QCoreApplication.translate("MainWindow", u"11000", None))
        self.bitrateBox.setItemText(18, QCoreApplication.translate("MainWindow", u"12000", None))

        self.startButton.setText(QCoreApplication.translate("MainWindow", u"  \u041d\u0410\u0427\u0410\u0422\u042c  ", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u" \u0421\u0422\u041e\u041f ", None))
        self.soundPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0440\u043e\u0436\u043a\u0430 \u0437\u0432\u0443\u043a\u0430", None))
        self.rawPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0420\u0430\u0432\u043a\u0430", None))
        self.subPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u0439\u043b \u0441\u0443\u0431\u0442\u0438\u0442\u0440\u043e\u0432", None))
        self.softPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u0443\u0442\u044c \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f \u0441\u043e\u0444\u0442\u0441\u0430\u0431\u0430", None))
        self.soundButton.setText("")
        self.rawButton.setText("")
        self.subButton.setText("")
        self.softButton.setText("")
        self.app_tab.setTabText(self.app_tab.indexOf(self.main_tab), QCoreApplication.translate("MainWindow", u"\u041e\u0434\u0438\u043d \u0444\u0430\u0439\u043b", None))
        self.tempLabel.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0423\u0414\u0415\u0422 \u0417\u0410\u0412\u0422\u0420\u0410", None))
        self.app_tab.setTabText(self.app_tab.indexOf(self.folder_tab), QCoreApplication.translate("MainWindow", u"\u041f\u0430\u043f\u043a\u0430", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0423\u0414\u0415\u0422 \u0417\u0410\u0412\u0422\u0420\u0410", None))
        self.app_tab.setTabText(self.app_tab.indexOf(self.settings_tab), QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.textBrowser.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:14pt; font-weight:600;\">\u0412\u0435\u0440\u0441\u0438\u044f 2.0 (Einstein): </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; font-weight:600; text-decoration: underline;\">\u0413\u043b\u043e\u0431\u0430\u043b\u044c\u043d\u0430\u044f \u043f\u0435\u0440\u0435\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u0434\u0432\u0438\u0436\u043a\u0430 \u043f\u0440\u043e\u0433"
                        "\u0440\u0430\u043c\u043c\u044b.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; font-weight:600;\">\u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f:</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">1) \u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d \u0431\u0430\u0433 \u043f\u0440\u0438\u0432\u043e\u0434\u044f\u0449\u0438\u0439 \u043a \u043a\u0440\u0438\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u043e\u0448\u0438\u0431\u043a\u0435 \u0435\u0441\u043b\u0438 \u0432 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0438 \u0441\u0443\u0431\u0442\u0438\u0442\u0440\u043e\u0432 \u0431\u044b\u043b\u0438 \u043a\u0432\u0430\u0434\u0440\u0430\u0442\u043d\u044b\u0435 \u0441\u043a\u043e\u0431\u043a\u0438"
                        ".</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">2) \u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d \u0431\u0430\u0433 \u0441 \u043d\u0435\u0440\u0430\u0431\u043e\u0442\u0430\u044e\u0449\u0435\u0439 \u043a\u043d\u043e\u043f\u043a\u043e\u0439 sub \u0434\u043b\u044f \u0440\u0435\u043d\u0434\u0435\u0440\u0430 \u0431\u0435\u0437 \u0441\u0443\u0431\u0442\u0438\u0442\u0440\u043e\u0432.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">3) \u041f\u0440\u0438 \u0432\u044b\u0431\u043e\u0440\u0435 \u043c\u0435\u0441\u0442\u0430 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f \u0441\u043e\u0444\u0442\u0441\u0430\u0431\u0430 \u0435\u0441\u043b\u0438 \u043f\u0430\u043f\u043a\u0430 \u0443\u0434\u043e\u0432"
                        "\u043b\u0435\u0442\u0432\u043e\u0440\u044f\u0435\u0442 \u0441\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u043e\u043c\u0443 \u0448\u0430\u0431\u043b\u043e\u043d\u0443 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0439 \u043f\u0430\u043f\u043e\u043a \u0442\u043e\u0440\u0440\u0435\u043d\u0442\u043e\u0432, \u0442\u043e \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0431\u0443\u0434\u0435\u0442 \u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043e \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u0435\u0440\u0438\u0438, \u0433\u0434\u0435 \u043d\u0443\u0436\u043d\u043e \u0431\u0443\u0434\u0435\u0442 \u0442\u043e\u043b\u044c\u043a\u043e \u043d\u0430\u043f\u0438\u0441\u0430\u0442\u044c \u043d\u043e\u043c\u0435\u0440.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">4) \u041c\u0435\u043b\u043a\u0438\u0435"
                        " \u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; font-weight:600;\">\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u043e:</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">1) \u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u0432\u043a\u043b\u0430\u0434\u043a\u0430 &quot;\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438&quot; \u0434\u043b\u044f \u0431\u0443\u0434\u0443\u0449\u0435\u0439 \u043a\u0430\u0441\u0442\u043e\u043c\u0438\u0437\u0430\u0446\u0438\u0438 \u0440\u0430\u0431\u043e\u0442\u044b \u0441 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u043e\u0439.</span"
                        "></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">2) \u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u0432\u043a\u043b\u0430\u0434\u043a\u0430 &quot;\u0414\u043b\u044f \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\u0430&quot; \u0434\u043b\u044f \u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u043d\u043e\u0432\u044b\u0445 \u044d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u044b\u0445 \u0444\u0443\u043d\u043a\u0446\u0438\u0439, \u0430 \u0442\u0430\u043a\u0436\u0435 \u0434\u043b\u044f \u0430\u043a\u0442\u0438\u0432\u0430\u0446\u0438\u0438 \u0441\u043f\u0435\u0446\u0438\u0444\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u0440\u0435\u0436\u0438\u043c\u043e\u0432 \u0440\u0430\u0431\u043e\u0442\u044b.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; m"
                        "argin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">3) \u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u0433\u0430\u043b\u043e\u0447\u043a\u0430 &quot;\u041b\u043e\u0433\u043e&quot; \u0434\u043b\u044f \u0442\u043e\u0433\u043e \u0447\u0442\u043e\u0431\u044b \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043b\u043e\u0433\u043e \u0410\u043d\u0438\u0431\u0430\u0437\u044b \u043f\u0440\u0438 \u0440\u0435\u043d\u0434\u0435\u0440\u0435.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">4) \u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u0433\u0430\u043b\u043e\u0447\u043a\u0430 &quot;HEVC&quot; \u0434\u043b\u044f \u0440\u0435\u043d\u0434\u0435\u0440\u0430 \u0445\u0430\u0440\u0434\u0441\u0430\u0431\u0430 \u0432 \u043a\u043e\u0434\u0435\u043a\u0435 h265 (\u043e\u043d \u0436\u0435 HEVC).<"
                        "/span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">5) \u041f\u0440\u0438 \u043f\u0435\u0440\u0432\u043e\u043c \u0437\u0430\u043f\u0443\u0441\u043a\u0435 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u0431\u0443\u0434\u0435\u0442 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0441\u043a\u0430\u0447\u0430\u043d \u0438 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d ffmpeg, \u0430 \u0442\u0430\u043a\u0436\u0435 \u0448\u0440\u0438\u0444\u0442\u044b \u0434\u043b\u044f \u0440\u0430\u0431\u043e\u0442\u044b \u0441 \u041b\u043e\u0433\u043e.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-"
                        "left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:14pt; font-weight:600;\">\u0412\u0435\u0440\u0441\u0438\u044f 1.3 (Fresco): </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; text-decoration: underline;\">\u0412\u0435\u0440\u0441\u0438\u044e \u0441\u0447\u0438\u0442\u0430\u0442\u044c \u0442\u0443\u043f\u0438\u043a\u043e\u0432\u043e\u0439 \u0438 \u043d\u0435\u0440\u0430\u0431\u043e\u0447\u0435\u0439!</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-si"
                        "ze:14pt; font-weight:600;\">\u0412\u0435\u0440\u0441\u0438\u044f 1.2 (Euclid): </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">\u0427\u0430\u0441\u0442\u0438\u0447\u043d\u0430\u044f \u043f\u0435\u0440\u0435\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u0434\u0432\u0438\u0436\u043a\u0430 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u0438 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043c\u0435\u043b\u043a\u0438\u0445 \u0431\u0430\u0433\u043e\u0432.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2"
                        "'; font-size:14pt; font-weight:600;\">\u0412\u0435\u0440\u0441\u0438\u044f 1.1 (Newton): </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; font-weight:600;\">\u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f:</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">1) \u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430 \u043f\u0440\u043e\u0431\u043b\u0435\u043c\u0430 \u0441 \u0434\u043e\u0441\u0442\u0443\u043f\u043e\u043c \u043a \u043f\u0440\u0430\u0432\u0430\u043c \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u0430. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span styl"
                        "e=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">2) \u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d \u0431\u0430\u0433 \u0441 \u0432\u044b\u043b\u0435\u0442\u043e\u043c \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u043f\u0440\u0438 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u0438 \u043f\u0430\u043f\u043a\u0438 HARDSUB.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt; font-weight:600;\">\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u043e:</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">1) \u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u0432\u043a\u043b\u0430\u0434\u043a\u0430 &quot;\u0427\u0442\u043e \u043d\u043e\u0432\u043e\u0433\u043e?&quot; \u0434\u043b\u044f \u043e"
                        "\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u0432\u0441\u0435\u0445 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439 \u0432 \u0442\u0435\u043a\u0443\u0449\u0435\u0439 \u0432\u0435\u0440\u0441\u0438\u0438.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">2) \u041f\u0440\u0438 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u0438 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u043e\u0433\u043e ffmpeg, \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u043f\u0435\u0440\u0435\u043d\u043e\u0441\u0438\u0442 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u044b\u0435 \u0434\u043b\u044f \u0440\u0430\u0431\u043e\u0442\u044b \u0444\u0430\u0439\u043b\u044b \u0432 \u0441\u0438\u0441\u0442\u0435\u043c\u043d\u0443\u044e \u043f\u0430\u043f\u043a\u0443 \u0438 \u043f\u0440\u043e\u043f\u0438\u0441"
                        "\u044b\u0432\u0430\u0435\u0442 \u043f\u0443\u0442\u044c \u0432 \u043f\u0435\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0445 \u0441\u0440\u0435\u0434\u044b \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0430.</span></p></body></html>", None))
        self.app_tab.setTabText(self.app_tab.indexOf(self.whatsnew_tab), QCoreApplication.translate("MainWindow", u"\u0427\u0442\u043e \u043d\u043e\u0432\u043e\u0433\u043e?", None))
        self.enableDevMode.setText(QCoreApplication.translate("MainWindow", u"\u0412\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u0440\u0435\u0436\u0438\u043c \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\u0430", None))
        self.folderAutodecting.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0432\u0442\u043e\u0434\u0435\u0442\u0435\u043a\u0442\u0438\u043d\u0433 \u043f\u0430\u043f\u043e\u043a (\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u043e\u0435)", None))
        self.videoBitrateAutodetectibg.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0432\u0442\u043e\u0434\u0435\u0442\u0435\u043a\u0442\u0438\u043d\u0433 \u0431\u0438\u0442\u0440\u0435\u0439\u0442\u0430 \u0432\u0438\u0434\u0435\u043e \u0434\u043b\u044f \u0445\u0430\u0440\u0434\u0441\u0430\u0431\u0430 (\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u043e\u0435)", None))
        self.enableLogging.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0442\u044c \u043b\u043e\u0433 \u0444\u0430\u0439\u043b\u044b (\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u043e\u0435)", None))
        self.app_tab.setTabText(self.app_tab.indexOf(self.dev_tab), QCoreApplication.translate("MainWindow", u"\u0414\u043b\u044f \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\u0430", None))
    # retranslateUi

