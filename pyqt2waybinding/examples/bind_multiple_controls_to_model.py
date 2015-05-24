import PyQt4.QtCore as q
import PyQt4.QtGui as qt

from pyqt2waybinding import Observer


class Model(q.QObject):
    """
    A simple model class for testing
    """
    
    valueChanged = q.pyqtSignal(int)
    someTextChanged = q.pyqtSignal(str)
    
    def __init__(self):
        q.QObject.__init__(self)
        self.__value = 0
        self.__text = ""

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if (self.__value != value):
            self.__value = value
            print "model value changed to %i" % value
            self.valueChanged.emit(value)

    @property
    def someText(self):
        return self.__text

    @someText.setter
    def someText(self,text):
        if (self.__text != text):
            self.__text = text
            print "text changed: %s" % text
            self.someTextChanged.emit(text)


class TestWidget(qt.QWidget):
    """
    A simple GUI for testing
    """
    def __init__(self):
        qt.QWidget.__init__(self,parent=None)
        layout = qt.QVBoxLayout()

        spinbox1 = qt.QSpinBox()
        spinbox2 = qt.QSpinBox()
        textEdit = qt.QTextEdit()
        button = qt.QPushButton()
        slider = qt.QSlider(q.Qt.Horizontal)
        

        self.model = Model()

        valueObserver = Observer()
        self.valueObserver = valueObserver
        valueObserver.bindToProperty(spinbox1, "value")
        valueObserver.bindToProperty(spinbox2, "value")
        valueObserver.bindToProperty(self.model, "value")
        valueObserver.bindToProperty(slider, "value")

        textObserver = Observer()
        self.textObserver = textObserver
        textObserver.bindToProperty(self.model, "someText")
        textObserver.bind(textEdit, textEdit.setPlainText, textEdit.textChanged, getter = textEdit.toPlainText)

        button.clicked.connect(lambda: setattr(self.model,"value",10))

        layout.addWidget(spinbox1)
        layout.addWidget(spinbox2)
        layout.addWidget(textEdit)
        layout.addWidget(button)
        layout.addWidget(slider)

        self.setLayout(layout)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = qt.QApplication([])

    w = TestWidget()
    w.show()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(q, 'PYQT_VERSION'):
        qt.QApplication.instance().exec_()