import unittest
from pyqt2waybinding import BindingEndpoint
from PyQt4.QtCore import QObject, pyqtSignal


class RealPropertyModel(QObject):
    """
    A simple model class for testing
    """
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self):
        QObject.__init__(self)
        self.__value = 0

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if (self.__value != value):
            self.__value = value
            self.valueChanged.emit(value)

   


class GetterSetterPairModel(QObject):
    valueChanged = pyqtSignal(int)
    
    def __init__(self):
        QObject.__init__(self)
        self.__value = 0

    def value(self):
        return self.__value
    
    def setValue(self, value):
        if (self.__value != value):
            self.__value = value
            self.valueChanged.emit(value)


class VirtualPropertyModel(QObject):
    valueChanged = pyqtSignal(int)
    
    def __init__(self):
        QObject.__init__(self)
        self.__value = 0

    def getValue(self):
        return self.__value
    
    def setValue(self, value):
        if (self.__value != value):
            self.__value = value
            self.valueChanged.emit(value)

class Test_Observer(unittest.TestCase):
    def test_forProperty_realProperty(self):
        m = RealPropertyModel()
        endpoint = BindingEndpoint.forProperty(m,"value",useGetter=True)
        
        assert isinstance(endpoint,BindingEndpoint)
        self.assertTrue(endpoint.getter is not None)
        self.assertTrue(endpoint.setter is not None)
        
        endpoint.setter(10)
        self.assertTrue(m.value == 10)

        value = endpoint.getter()
        self.assertTrue(value == 10)
     
    def test_forProperty_getterSetterPairGet(self):
        m = VirtualPropertyModel()
        endpoint = BindingEndpoint.forProperty(m,"getValue",useGetter=True)
        
        assert isinstance(endpoint,BindingEndpoint)
        self.assertTrue(endpoint.getter is not None)
        self.assertTrue(endpoint.setter is not None)
        self.assertTrue(endpoint.getter.__name__ == "getValue")
        self.assertTrue(endpoint.setter.__name__ == "setValue")
        
        endpoint.setter(10)
        self.assertTrue(m.getValue() == 10)

        value = endpoint.getter()
        self.assertTrue(value == 10)
    
    def test_forProperty_getterSetterPairSet(self):
        m = VirtualPropertyModel()
        endpoint = BindingEndpoint.forProperty(m,"setValue",useGetter=True)
        
        assert isinstance(endpoint,BindingEndpoint)
        self.assertTrue(endpoint.getter is not None)
        self.assertTrue(endpoint.setter is not None)
        self.assertTrue(endpoint.getter.__name__ == "getValue")
        self.assertTrue(endpoint.setter.__name__ == "setValue")
        
        endpoint.setter(10)
        self.assertTrue(m.getValue() == 10)

        value = endpoint.getter()
        self.assertTrue(value == 10)

    def test_forProperty_getterSetterPairWithoutExplicitGet(self):
        m = GetterSetterPairModel()
        endpoint = BindingEndpoint.forProperty(m,"value",useGetter=True)
        
        assert isinstance(endpoint,BindingEndpoint)
        self.assertTrue(endpoint.getter is not None)
        self.assertTrue(endpoint.setter is not None)
        self.assertTrue(endpoint.getter.__name__ == "value")
        self.assertTrue(endpoint.setter.__name__ == "setValue")
        
        endpoint.setter(10)
        self.assertTrue(m.value() == 10)

        value = endpoint.getter()
        self.assertTrue(value == 10)

    def test_forProperty_virtualProperty(self):
        m = VirtualPropertyModel()
        endpoint = BindingEndpoint.forProperty(m,"value",useGetter=True)
        
        assert isinstance(endpoint,BindingEndpoint)
        self.assertTrue(endpoint.getter is not None)
        self.assertTrue(endpoint.setter is not None)
        self.assertTrue(endpoint.getter.__name__ == "getValue")
        self.assertTrue(endpoint.setter.__name__ == "setValue")
        
        endpoint.setter(10)
        self.assertTrue(m.getValue() == 10)

        value = endpoint.getter()
        self.assertTrue(value == 10)

if __name__ == '__main__':
    unittest.main()
