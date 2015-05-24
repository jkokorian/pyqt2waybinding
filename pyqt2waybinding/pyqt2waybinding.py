import PyQt4.QtCore as _q


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

    @staticmethod
    def forProperty(instance,propertyName,useGetter=False):
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
        assert isinstance(propertyName,str)

        if propertyName.startswith("get") or propertyName.startswith("set"):
            #property is a getter function or a setter function, assume a corresponding setter/getter function exists
            getterName = "get" + propertyName[3:]
            setterName = "set" + propertyName[3:]
            if len(propertyName[3:]) > 1:
                signalName = propertyName[3].lower() + propertyName[4:] + "Changed"
            else:
                signalName = propertyName.lower() + "Changed"

            assert hasattr(instance,getterName)
            assert hasattr(instance,setterName)
            assert hasattr(instance,signalName)
            getter = getattr(instance,getterName)
            setter = getattr(instance,setterName)
            signal = getattr(instance,signalName)

        elif hasattr(instance, propertyName) and callable(getattr(instance,propertyName)):
            #property is a getter function without the "get" prefix. Assume a corresponding setter method exists
            getterName = propertyName
            setterName = "set" + propertyName.capitalize()
            signalName = propertyName + "Changed"

            assert hasattr(instance,setterName)
            assert hasattr(instance,signalName)
            getter = getattr(instance,getterName)
            setter = getattr(instance,setterName)
            signal = getattr(instance,signalName)


        elif hasattr(instance, propertyName):
            #property is real property. Assume it is not readonly
            signalName = propertyName + "Changed"
            assert hasattr(instance,signalName)

            getter = lambda: getattr(instance,propertyName)
            setter = lambda value: setattr(instance,propertyName,value)
            signal = getattr(instance,signalName)

        else:
            #property is a virtual property. There should be getPropertyName and setPropertyName methods
            if len(propertyName) > 1:
                getterName = "get" + propertyName[0].upper() + propertyName[1:]
                setterName = "set" + propertyName[0].upper() + propertyName[1:]
                signalName = propertyName + "Changed"
            else:
                getterName = "get" + propertyName.upper()
                setterName = "set" + propertyName.upper()
                signalName = propertyName.lower() + "Changed"

            assert hasattr(instance,getterName)
            assert hasattr(instance,setterName)
            assert hasattr(instance,signalName)

            getter = getattr(instance,getterName)
            setter = getattr(instance,setterName)
            signal = getattr(instance,signalName)

        return BindingEndpoint(instance, setter, signal, getter = getter if useGetter else None)

        

class Observer(_q.QObject):
    """
    Create an instance of this class to connect binding endpoints together and intiate a 2-way binding between them.
    """
    def __init__(self):
        _q.QObject.__init__(self)

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
        endpoint = BindingEndpoint.forProperty(instance,propertyName,useGetter = useGetter)

        self.bindToEndPoint(endpoint)

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




