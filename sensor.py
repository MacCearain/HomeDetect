'''
  sensor module defintion

  Contains definitions of various analog and digital sensors
'''


# pylint: disable=line-too-long


DIGITALHIGH = 1
DIGITALLOW = 0


class BasicSensor(object):
    '''
      Define a Basic Sensor Class to be used via inheritence
    '''

    def __init__(self, sensorName, sensorType, sensorKind='Generic'):
        '''
          Initialize the Basic Sensor Class
        '''
        self.sensor_name = sensorName
        self.sensor_type = sensorType   # Analog vs Digital
        # Temperature, Pressure, Switch, Button, Motion, Door, etc...
        self.sensor_kind = sensorKind
        self.monitor_group = {}         # An Empty Dictionary of Monitors from monitor import

    def define_monitor(self, name, monitor_object):
        '''
          Add / define a monitor to the Basic Sensor Object
        '''
        self.monitor_group[name] = monitor_object


class DigitalSensor(BasicSensor):
    '''
      Define a Digital Sensor -- Can be HIGH or LOW
    '''

    def __init__(self, sensorName, inputPin, units="High/Low", description="This digital sensor can detect High or Low voltage.", defaultHighStr="HIGH", defaultLowStr="LOW", sensorKind='Switch'):
        '''
          Initialization of the Digial Sensor Class
        '''
        BasicSensor.__init__(self, sensorName, "Digital", sensorKind)
        self.description = description
        self.units = units
        self.input_pin = inputPin
        self.default_high_str = defaultHighStr
        self.default_low_str = defaultLowStr
        self._digital_value = 0

    def set_digital_value(self, newValue_HIGHLOW):
        '''
          Set a new value on the Digital Sensor -- either HIGH or LOW (1 or 0)
        '''
        if (newValue_HIGHLOW == DIGITALHIGH) or (newValue_HIGHLOW == DIGITALLOW):
            self._digital_value = newValue_HIGHLOW
            # the below for loop needs to be reviewed...  I don't recall coding a check function that took an argument... weird
            for current_monitor in self.monitor_group:
                self.monitor_group[current_monitor].check(self.current_position())

        else:
            print("ERROR -- Only 1 or 0 can be assigned to a Digital Sensor Value.  You attempted: " + str(newValue_HIGHLOW))

    def current_position(self):
        '''
          current_position returns a string that represents the state of the digital input
        '''
        if self._digital_value == DIGITALHIGH:
            return self.default_high_str
        else:
            return self.default_low_str

    def current_value(self):
        '''
          current_value returns either DIGITALHIGH or DIGITALLOW (1 or 0)
        '''
        return self._digital_value


class ToggleSwitch(DigitalSensor):
    '''
      Defines the ToggleSwitch Class (Inherits from Digital Sensor)
    '''
    def __init__(self, PIN, name='Toggle', description='ON / OFF Toggle Switch'):
        '''
          Initializes an instace of a Toggle Switch Object
        '''
        DigitalSensor.__init__(self, name, PIN, 'ON / OFF',
                               description, 'ON', 'OFF', 'Toggle')


class DoorSwitch(DigitalSensor):
    '''
      Defines a Door Switch Class (inhertis from Digital Sensor)
      Door Switches can be used to show that a door is either OPEN or CLOSED
      You may use multiple inputs to determine this...
      This implementation does not support a door that is half open  -- neither fully opened nor fully closed
    '''
    def __init__(self, PIN, name='Door', description='OPEN / CLOSED Magnetic Door Sensor'):
        '''
          Initializes an instance of a Door Switch Object
        '''
        DigitalSensor.__init__(
            self, name, PIN, 'OPEN / CLOSED', description, 'CLOSED', 'OPEN', 'Door')


class MotionSensor(DigitalSensor):
    '''
      Defines a Motion Sensor Class (inherits from Digital Sensor)
      Motion Sensors either detect MOTION or STILL
    '''
    def __init__(self, PIN, name='PIR', description='PIR Motion Detector'):
        '''
          Initializes an instance of a Motion Sensor Object
        '''
        DigitalSensor.__init__(
            self, name, PIN, 'MOTION / NO MOTION', description, 'MOTION', 'STILL', 'Motion')


class WaterSensor(DigitalSensor):
    '''
      Defines a Water Sensor Class (inherits from Digital Sensor)
      Water Sensors either detect WET or DRY
    '''
    def __init__(self, PIN, name='Water', description='Water Detector'):
        '''
          Initializes an instance of a Water Sensor Object
        '''
        DigitalSensor.__init__(self, name, PIN, 'WET / DRY',
                               description, 'DRY', 'WET', 'Water')


class LinearAnalogSensor(BasicSensor):
    '''
      Defines the Linear Analog Sensor Class (inherited from Basic Sensor) and used to derive specific Analog Sensors
      Analog Sensors can read a value within a range of values.  Typically they can be read to the sensitivity
      of the anolog to digital converter.  8-bit, 10-bit, 12-bit, 16-bit, 32-bit, ect...
      This is a linear analog sensor because it assumes a linear scaling of voltages to real world readings
    '''
    def __init__(self, sensorName, scalingFactor, scalingOffSet, units, inputPin, defaultFormat, sensorKind='mV'):
        '''
          Initializes an instance of an Analog Sensor
        '''
        BasicSensor.__init__(self, sensorName, "Analog", sensorKind)
        self.scaling_factor = scalingFactor
        self.scaling_offset = scalingOffSet
        self.units = units
        self.input_pin = inputPin
        self.default_format = defaultFormat
        self.digital_current_value = 0
        self.analog_value_mV = 0
        self._scaled_value = 0.0
        self.calibration_factor = 1.0
        self.calibration_offset = 0.0

    def set_analog_value(self, new_value_mV):
        '''
          set_analog_value takes a new mV reading from the sensor and calculates the new scaled_value
        '''
        self.analog_value_mV = new_value_mV
        self._scaled_value = ((new_value_mV * self.scaling_factor) +
                              self.scaling_offset) * self.calibration_factor + self.calibration_offset

    def scaled_value(self):
        '''
          scaled_value returns the current Scaled Value as a float
        '''
        return self._scaled_value

    def __str__(self):
        '''
          Returns the default string representation based on the formatting provided with the initialization of the object
        '''
        return self.default_format % (self.scaled_value, self.units)


class TMP36(LinearAnalogSensor):
    '''
      Defines a TMP36 Temperature Sensor Class (inherited from a Linear Analog Sensor)
    '''
    def __init__(self, PIN, name='TMP36', description='The TMP36 is a temerature sensor that scales linearly from -40C to 125C.'):
        '''
          Initializes a TMP36 Temperature Sensor object
        '''
        LinearAnalogSensor.__init__(self, name, 0.1, -50.0, 'degC', PIN, '%s %s', 'Temperature')
        self.description = description

    def set_analog_value(self, new_value_mV):
        self.analog_value_mV = new_value_mV
        self._scaled_value = (new_value_mV * self.scaling_factor) + self.scaling_offset
        for current_monitor in self.monitor_group:
            self.monitor_group[current_monitor].Check(self.temp_reading(self.monitor_group[current_monitor].units))

    def temp_reading(self, units='degC'):
        '''
          temp_reading returns the temperature of the TMP36 in the units requested...
        '''
        if units == 'degC':  # Celcius
            return self.scaled_value()
        elif units == 'degF':  # Farenheit
            return (self.scaled_value() * 9.0 / 5.0) + 32.0
        elif units == 'degK':  # Kelvin
            return self.scaled_value() + 273.15
        elif units == 'degR':  # Rankine
            return (self.scaled_value() + 273.15) * 9.0 / 5.0
        elif units == 'degDe':  # Delisle
            return (100.0 - self.scaled_value()) * 3.0 / 2.0
        elif units == 'degN':  # Newton
            return self.scaled_value() * 33.0 / 100.0
        elif units == 'degRe':  # Reaumur
            return self.scaled_value() * 4.0 / 5.0
        elif units == 'degRo':  # Romer
            return (self.scaled_value() * 21.0 / 40.0) + 7.5
        else:
            return self.scaled_value()
