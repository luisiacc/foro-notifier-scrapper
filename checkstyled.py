from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
#===============================================================================
# MyCheckBox
#===============================================================================
#className
class MyCheckBox(QCheckBox):
#|-----------------------------------------------------------------------------|
# class Variables
#|-----------------------------------------------------------------------------|
    #no classVariables

#|-----------------------------------------------------------------------------|
# Constructor
#|-----------------------------------------------------------------------------|
    def __init__(self, *args, **kwargs):
            QCheckBox.__init__(self, *args, **kwargs)
            self.setStyleSheet("background-color: rgb(0, 0, 0);\n" +
                      "color: rgb(255, 255, 255);\n")
            #set default check as True
            self.setChecked(True)
            #set default enable as True
            #    if it set to false will always remain on/off
            #    here it is on as setChecked is True
            self.setEnabled(True)
            self._enable = True
#|--------------------------End of Constructor---------------------------------|
#|-----------------------------------------------------------------------------|
#   mousePressEvent
#|-----------------------------------------------------------------------------|
    #overrite
    def mousePressEvent(self, *args, **kwargs):
            #tick on and off set here
            if self.isChecked():
                self.setChecked(False)
            else:
                self.setChecked(True)
            return QCheckBox.mousePressEvent(self, *args, **kwargs)
#|--------------------------End of mousePressEvent-----------------------------|

#|-----------------------------------------------------------------------------|
# paintEvent
#|-----------------------------------------------------------------------------|
    def paintEvent(self,event):

            #just setting some size aspects
            self.setMinimumHeight(40)
            self.setMinimumWidth(100)
            self.setMaximumHeight(50)
            self.setMaximumWidth(150)

            self.resize(self.parent().width(),self.parent().height())
            painter = QPainter()
            painter.begin(self)

            #for the black background
            brush = QBrush(QColor(0,0,0),style=Qt.SolidPattern)
            painter.fillRect(self.rect(),brush)


            #smooth curves
            painter.setRenderHint(QPainter.Antialiasing)

            #for the on off font
            font  = QFont()
            font.setFamily("Courier New")
            font.setPixelSize(28)
            painter.setFont(font)

            #change the look for on/off
            if self.isChecked():
                #blue fill
                brush = QBrush(QColor(50,50,255),style=Qt.SolidPattern)
                painter.setBrush(brush)

                #rounded rectangle as a whole
                painter.drawRoundedRect(0,0,self.width()-2,self.height()-2, \
                                   self.height()/2,self.height()/2)

                #white circle/button instead of the tick mark
                brush = QBrush(QColor(255,255,255),style=Qt.SolidPattern)
                painter.setBrush(brush)
                painter.drawEllipse(self.width()-self.height(),0,self.height(),self.height())

                #on text
                painter.drawText(self.width()/4,self.height()/1.5, "On")

            else:
                #gray fill
                brush = QBrush(QColor(50,50,50),style=Qt.SolidPattern)
                painter.setBrush(brush)

                #rounded rectangle as a whole
                painter.drawRoundedRect(0,0,self.width()-2,self.height()-2, \
                                   self.height()/2,self.height()/2)

                #white circle/button instead of the tick but in different location
                brush = QBrush(QColor(255,255,255),style=Qt.SolidPattern)
                painter.setBrush(brush)
                painter.drawEllipse(0,0,self.height(),self.height())

                #off text
                painter.drawText(self.width()/2,self.height()/1.5, "Off")


#|-----------------------End of paintEvent-------------------------------------|
if __name__ == '__main__':
    app = QApplication(sys.argv)
    wgt = QWidget()
    wgt.setStyleSheet("background-color: rgb(0, 0, 0);\n")
    cb = MyCheckBox()
    cb.setParent(wgt)
    layout = QHBoxLayout()
    layout.addWidget(cb)
    wgt.resize(200,100)
    wgt.show()
    sys.exit(app.exec_())