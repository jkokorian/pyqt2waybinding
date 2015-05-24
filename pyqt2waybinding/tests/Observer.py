import unittest
from pyqt2waybinding import Observer, BindingEndpoint
from PyQt4.QtCore import QObject, pyqtSignal


class Model(QObject):
    """
    A simple model class for testing
    """
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self):
        QObject.__init__(self)
        self.__value = 0
        self.__text = ""

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if (self.__value != value):
            self.__value = value
            self.valueChanged.emit(value)


class Test_Observer(unittest.TestCase):
    def test_BindToDecoratorProperty(self):
        o = Observer()
        m = Model()
        o.bindToProperty(m,"value",useGetter=True)
        self.assertTrue(o.bindings.has_key(id(m)))
        
        endpoint = o.bindings[id(m)]
        assert isinstance(endpoint,BindingEndpoint)
        self.assertTrue(endpoint.getter is not None)
        self.assertTrue(endpoint.setter is not None)
        
        endpoint.setter(10)
        self.assertTrue(m.value == 10)

        value = endpoint.getter()
        self.assertTrue(value == 10)
        

if __name__ == '__main__':
    unittest.main()
