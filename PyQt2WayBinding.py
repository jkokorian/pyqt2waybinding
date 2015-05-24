import PyQt4.QtCore as q
import PyQt4.QtGui as qt

class BindingEndpoint(object):
    """
    Data object that contains the triplet of: getter, setter and change notification signal, 
    as well as the object instance and it's memory id to which the binding triplet belongs.
    
    Parameters:
        instance -- the object instance to which the getter, setter and changedSignal belong
        setter -- the value setter method
        valueChangedSignal -- the pyqtSignal that is emitted with the value changes
        getter -- the value getter method (default None)
                  If None, the signal argument(s) are passed to the setter method
    """
    def __init__(self,instance,setter,valueChangedSignal,getter=None):
        self.instanceId = id(instance)
        self.instance = instance
        self.getter = getter
        self.setter = setter
        self.valueChangedSignal = valueChangedSignal

        

class Observer(q.QObject):
    """
    Create an instance of this class to connect binding endpoints together and intiate a 2-way binding between them.
    """
    def __init__(self):
        q.QObject.__init__(self)

        self.bindings = {}
        self.ignoreEvents = False

    def bind(self,instance,setter,valueChangedSignal,getter = None):
        """
        Creates an endpoint and call bindToEndpoint(endpoint). This is a convenience method.

        Parameters:
            instance -- the object instance to which the getter, setter and changedSignal belong
            setter -- the value setter method
            valueChangedSignal -- the pyqtSignal that is emitted with the value changes
            getter -- the value getter method (default None)
                      If None, the signal argument(s) are passed to the setter method
        """

        endpoint = BindingEndpoint(instance,setter,valueChangedSignal,getter=getter)
        self.bindToEndPoint(endpoint)

    def bindToEndPoint(self,bindingEndpoint):
        """
        2-way binds the target endpoint to all other registered endpoints.
        """
        self.bindings[bindingEndpoint.instanceId] = bindingEndpoint
        bindingEndpoint.valueChangedSignal.connect(self._updateEndpoints)
        

    def bindToProperty(self,instance,propertyName,useGetter=False):
        """
        2-way binds to an instance property.

        Parameters:
        - instance -- the object instance
        - propertyName -- the name of the property to bind to
        - useGetter: when True, calls the getter method to obtain the value. When False, the signal argument is used as input for the target setter. (default False)

        Notes:
        2-way binds to an instance property according to one of the following naming conventions:

        @property, propertyName.setter and pyqtSignal
        - getter: propertyName
        - setter: propertyName
        - changedSignal: propertyNameChanged

        getter, setter and pyqtSignal (this is used when binding to standard QWidgets like QSpinBox)
        - getter: propertyName()
        - setter: setPropertyName()
        - changedSignal: propertyNameChanged
        """

        getterAttribute = getattr(instance,propertyName)
        if callable(getterAttribute):
            #the propertyName turns out to be a method (like value()), assume the corresponding setter is called setValue()
            getter = getterAttribute
            if len(propertyName) == 1:
                setter = getattr(instance,"set" + propertyName[0].upper())
            elif propertyName.startswith("get"):
                setter = getattr(instance,"set" + propertyName[3:])
            else:
                setter = getattr(instance,"set" + propertyName[0].upper() + propertyName[1:])
        else:
            getter = lambda: getterAttribute()
            setter = lambda value: setattr(instance,propertyName,value)

        valueChangedSignal = getattr(instance,propertyName + "Changed")

        self.bind(instance, setter, valueChangedSignal, getter = getter if useGetter else None)

    def _updateEndpoints(self,*args,**kwargs):
        """
        Updates all endpoints except the one from which this slot was called.

        Note: this method is probably not complete threadsafe. Maybe a lock is needed when setter self.ignoreEvents
        """

        sender = self.sender()
        if not self.ignoreEvents:
            self.ignoreEvents = True

            for binding in self.bindings.values():
                if binding.instanceId == id(sender):
                    continue
                
                if args: 
                    binding.setter(*args,**kwargs)
                else:
                    binding.setter(self.bindings[id(sender)].getter())

            self.ignoreEvents = False



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
