import time

ON=1
OFF=0

DIGITALHIGH=1
DIGITALLOW=0


#-----------------------------------------------------------------------------------------------------------------------------------------------------
#  Monitor Definitions...
#
class BasicMonitor:

     def __init__(self, Name, Description, Type, Kind, Subject='Unknown', Body='Unknown'):
          self.Name = Name
          self.Description = Description
          self.Type = Type                    # ie Door, Water, Temperature
          self.Kind = Kind                    # A little different than the Radio/Sensor Definitions
          self.__Raised = False               # Private -- True for Raised, False for Not Raised
          self.__Notified = False             # Private -- False for Pending Notification, True after Notification Sent out
          self.__LatchTime = int(time.time()) # The last time in Epoch Seconds that the monitor latched
          self.LatchDuration = 300            # The number of seconds between resets
          self.Subject = Subject              # Used to store the Subject Line of an Email
          self.Body = Body                    # Used to store the Body of the Email

     def RaiseFlag(self):
          if (self.__Raised == False):
              self.__Raised = True
              self.__Notifed = False
              self.__LatchTime = int(time.time())

     def ClearFlag(self):
          self.__Raised = False
          self.__Notified = False
          self.__LatchTime = int(time.time())

     def SetNotified(self):
          self.__Notified = True

     def Reset(self):
          if ((self.__LatchTime + self.LatchDuration) <  int(time.time())):
              self.__Raised = False
              self.__Notified = False
          

     def CurrentStatus(self):
          TimeTillReset = self.LatchDuration - (int(time.time()) - self.__LatchTime)
          return self.__Raised, self.__Notified, TimeTillReset

     def __str__(self):
          if self.__Raised == True:
              return 'Detected'
          else:
              return 'Not Detected'
          


class BaseTemperatureMonitor(BasicMonitor):

      def __init__(self, Name, Threshold, Type, Kind, Units='degF', Description='Not to be instanced directly -- here for inheritence',Subject='Unknown', Body='Unknown'):
           BasicMonitor.__init__(self, Name, Description, Type, Kind, Subject, Body)
           self.Threshold = Threshold
           self.Units = Units


class TemperatureLowMonitor(BaseTemperatureMonitor):

      def __init__(self, Name, Threshold, Type='Temperature', Kind='BELOW THRESHOLD', Units='degF', Description='Monitor when the Temperature drops below Threshold'):
           BaseTemperatureMonitor.__init__(self, Name, Threshold, Type, Kind, Units, Description, 'Low Temperature Detected', 'Check the furace')

      def Check(self, ActualTemperature):
           if ActualTemperature < self.Threshold:
                self.RaiseFlag()

class TemperatureAtMonitor(BaseTemperatureMonitor):

      def __init__(self, Name, Threshold, Type='Temperature', Kind='AT Threshold', Units='degF', Description='Monitor when the Temperature is at the Threshold'):
           BaseTemperatureMonitor.__init__(self, Name, int(Threshold), Type, Kind, Units, Description, 'Temperature Attained', 'We hit the temp')

      def Check(self, ActualTemperature):
           if int(ActualTemperature) == self.Threshold:
                self.RaiseFlag()

      
                
class TemperatureHighMonitor(BaseTemperatureMonitor):

      def __init__(self, Name, Threshold, Type='Temperature', Kind='ABOVE THRESHOLD', Units='degF', Description='Monitor when the Temperature exceeds the Threshold'):
           BaseTemperatureMonitor.__init__(self, Name, Threshold, Type, Kind, Units, Description, 'Temperature is too high', 'Check the AC')

      def Check(self, ActualTemperature):
           if ActualTemperature > self.Threshold:
                self.RaiseFlag()


class BaseMotionMonitor(BasicMonitor):
      
      def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Unknown', Body='Unknown'):
           BasicMonitor.__init__(self, Name, Description, Type, Kind, Subject, Body)
           self.TriggerValue = TriggerValue

      def Check(self, ActualMotionSensorReading):
           if ActualMotionSensorReading == self.TriggerValue:
                self.RaiseFlag()

class MotionMonitor(BaseMotionMonitor):

      def __init__(self, Name, Type='Motion', Kind='PIR', TriggerValue='MOTION', Description='Monitor when Motion is detected.'):
           BaseMotionMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'MOTION Detected', 'Something was moving.')

class NoMotionMonitor(BaseMotionMonitor):

      def __init__(self, Name, Type='Motion', Kind='PIR', TriggerValue='STILL', Description='Monitor when a lack of motion is detected.'):
           BaseMotionMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'Lack of Motion Detected', 'It stopped moving')           


class BaseDoorMonitor(BasicMonitor):

      def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Unknown', Body='Unknown'):
           BasicMonitor.__init__(self, Name, Description, Type, Kind, Subject, Body)
           self.TriggerValue = TriggerValue

      def Check(self, ActualDoorSensorReading):
           if ActualDoorSensorReading == self.TriggerValue:
                self.RaiseFlag()


class DoorOpenMonitor(BaseDoorMonitor):

      def __init__(self, Name, Type='Door', Kind='Position', TriggerValue='OPEN', Description='Monitor when the DOOR is OPEN'):
           BaseDoorMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'DOOR OPEN', 'The Door was opened')


class DoorClosedMonitor(BaseDoorMonitor):

      def __init__(self, Name, Type='Door', Kind='Position', TriggerValue='CLOSED', Description='Monitor when the DOOR is CLOSED'):
           BaseDoorMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'DOOR CLOSED', 'The Door was Closed')


class BaseWaterMonitor(BasicMonitor):

      def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Uknonwn', Body='Unknown'):
           BasicMonitor.__init__(self, Name, Description, Type, Kind, Subject, Body)
           self.TriggerValue = TriggerValue

      def Check(self, ActualWaterSensorReading):
           if ActualWaterSensorReading == self.TriggerValue:
                self.RaiseFlag()


class WaterWetMonitor(BaseWaterMonitor):

      def __init__(self, Name, Type='Water', Kind='Resistive Pad', TriggerValue='WET', Description='Monitor when the SENSOR is WET'):
           BaseWaterMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'WATER DETECTED', 'There is Water on the Floor')


class WaterDryMonitor(BaseWaterMonitor):

      def __init__(self, Name, Type='Water', Kind='Resistive Pad', TriggerValue='DRY', Description='Monitor when the SENSOR is DRY'):
           BaseWaterMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'No Water Detected', 'There is NO Water')


class BasePowerMonitor(BasicMonitor):

      def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Uknown', Body='Unknown'):
           BasicMonitor.__init__(self, Name, Description, Type, Kind, Subject, Body)
           self.TriggerValue = TriggerValue

      def Check(self, ActualPowerSensorReading):
           if ActualPowerSensorReading == self.TriggerValue:
                self.RaiseFlag()


class PowerOutMonitor(BasePowerMonitor):

      def __init__(self, Name, Type='Power', Kind='Pi GPIO', TriggerValue='OUT', Description='Monitor when the Power is Out'):
           BasePowerMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'The POWER is OUT', 'The Power is OUT')


class PowerNormalMonitor(BasePowerMonitor):

      def __init__(self, Name, Type='Power', Kind='Pi GPIO', TriggerValue='NORMAL', Description='Monitor when the Power is Normal (ON)'):
           BasePowerMonitor.__init__(self, Name, Type, Kind, TriggerValue, Description, 'The POWER is Available', 'The POWER IS ON')



#  Soo....  After defining all of these Monitor Classes...  The only ones I forsee using in my current project are:
#  
#    TemperatureLowMonitor -- To Detect Broken Windows (in the winter) or a busted Heater in the House
#    TemperatureHighMonitor -- To Detect when the Air Conditioner in the House is busted...
#    DoorOpenMonitor -- To Detect when the Garage Door is Open when the system is ARMED
#    WaterWetMonitor -- To Detect when water is detected on the Basement Floor...
#    MotionMonitor -- To Detect when there is MOTION in a Room while the system is ARMED
#    PowerOutMonitor -- To Detect when Power at the House is NOT Available...

      

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Sensor Definitions
#

class BasicSensor:


    def __init__(self, sensorName, sensorType, sensorKind='Generic'):
          self.sensorName = sensorName
          self.sensorType = sensorType   # Analog vs Digital
          self.sensorKind = sensorKind   # Temperature, Pressure, Switch, Button, Motion, Door, etc...
          self.monitorGroup = {}         # An Empty Dictionary of Monitors from Above

    def defineMonitor(self, Name, MonitorObject):
          self.monitorGroup[Name] = MonitorObject


class DigitalSensor(BasicSensor):


    def __init__(self, sensorName, inputPin, units="High/Low", description = "This digital sensor can detect High or Low voltage.", defaultHighStr="HIGH", defaultLowStr="LOW", sensorKind='Switch'):
          BasicSensor.__init__(self, sensorName, "Digital", sensorKind)
          self.description = description
          self.units = units
          self.inputPin = inputPin
          self.defaultHighStr = defaultHighStr
          self.defaultLowStr = defaultLowStr
          self._digitalValue = 0

    def setDigitalValue(self, newValue_HIGHLOW):
          if ((newValue_HIGHLOW == DIGITALHIGH) or (newValue_HIGHLOW == DIGITALLOW)):
                self._digitalValue = newValue_HIGHLOW
                for CurrentMonitor in self.monitorGroup:
                    self.monitorGroup[CurrentMonitor].Check(self.CurrentPosition())

          else:
                print "ERROR -- Only 1 or 0 can be assigned to a Digital Sensor Value.  You attempted: " + str(newValue_HIGHLOW)

    def CurrentPosition(self):
          if self._digitalValue == DIGITALHIGH:
                return self.defaultHighStr
          else:
                return self.defaultLowStr

    def CurrentValue(self):
          return self._digitalValue
          

class ToggleSwitch(DigitalSensor):


    def __init__(self, PIN, name='Toggle', description='ON / OFF Toggle Switch'):
          DigitalSensor.__init__(self, name, PIN, 'ON / OFF', description, 'ON', 'OFF',  'Toggle')


class DoorSwitch(DigitalSensor):


    def __init__(self, PIN, name='Door', description='OPEN / CLOSED Magnetic Door Sensor'):
          DigitalSensor.__init__(self, name, PIN, 'OPEN / CLOSED', description, 'CLOSED', 'OPEN', 'Door')


class MotionSensor(DigitalSensor):


    def __init__(self, PIN, name='PIR', description='PIR Motion Detector'):
          DigitalSensor.__init__(self, name, PIN, 'MOTION / NO MOTION', description, 'MOTION', 'STILL', 'Motion')


class WaterSensor(DigitalSensor):


    def __init__(self, PIN, name='Water', description='Water Detector'):
          DigitalSensor.__init__(self, name, PIN, 'WET / DRY', description, 'DRY', 'WET', 'Water')


class AnalogSensor(BasicSensor):


    def __init__(self, sensorName, scalingFactor, scalingOffSet, units, inputPin, defaultFormat, sensorKind='mV'):
          BasicSensor.__init__(self, sensorName, "Analog", sensorKind)          
          self.scalingFactor = scalingFactor
          self.scalingOffSet = scalingOffSet
          self.units = units
          self.inputPin = inputPin
          self.defaultFormat = defaultFormat
          self.digitalCurrentValue = 0
          self.analogValue_mV = 0
          self._ScaledValue = 0.0
          self.calibrationFactor = 1.0
          self.calibrationOffset = 0.0

    def setAnalogValue(self, newValue_mV):
          self.analogValue_mV = newValue_mV
          self._ScaledValue = ((newValue_mV * self.scalingFactor) + self.scalingOffSet) * self.calibrationFactor + self.calibrationOffset


    def scaledValue(self):
          return  self._ScaledValue

    def __str__(self):
          return self.defaultFormat % (self._ScaledValue,  self.units) 


class TMP36(AnalogSensor):


    def __init__(self, PIN, name='TMP36', description='The TMP36 is a temerature sensor that scales linearly from -40C to 125C.'):
          AnalogSensor.__init__(self, name, 0.1, -50.0, 'degC', PIN, '%s %s', 'Temperature')
          self.description = description

    def setAnalogValue(self, newValue_mV):
          self.analogValue_mV = newValue_mV
          self._ScaledValue = (newValue_mV * self.scalingFactor) + self.scalingOffSet
          for CurrentMonitor in self.monitorGroup:
             self.monitorGroup[CurrentMonitor].Check(self.TempReading(self.monitorGroup[CurrentMonitor].Units))              


    def TempReading(self, units='degC'):
          if units == 'degC':   #Celcius
             return self.scaledValue()
          elif units == 'degF': #Farenheit
             return ((self.scaledValue() * 9.0 / 5.0) + 32.0)
          elif units == 'degK': #Kelvin
             return (self.scaledValue() + 273.15)
          elif units == 'degR': #Rankine
             return ((self.scaledValue() + 273.15) * 9.0 / 5.0)
          elif units == 'degDe': #Delisle
             return (100.0 - self.scaledValue()) * 3.0 / 2.0
          elif units == 'degN': #Newton
             return (self.scaledValue() * 33.0 / 100.0)
          elif units == 'degRe': #Reaumur
             return (self.scaledValue() * 4.0 / 5.0)
          elif units == 'degRo': #Romer
             return ((self.scaledValue() * 21.0 / 40.0) + 7.5)
          else:
             return self.scaledValue()


class Radio:


    def __init__(self, roomName, radioSN):
         self.roomName = roomName
         self.radioSN = radioSN
         self.dPINs = ['d00', 'd01', 'd02', 'd03', 'd04', 'd05', 'd06', 'd07', 'd10', 'd11', 'd12']
         self.digitalPinEnabled = {'d00':0,'d01':0,'d02':0,'d03':0,'d04':0,'d05':0,'d06':0,'d07':0,'d10':0,'d11':0,'d12':0}
         self.digitalPinValue = {'d00':0,'d01':0,'d02':0,'d03':0,'d04':0,'d05':0,'d06':0,'d07':0,'d10':0,'d11':0,'d12':0}
         self.aPINs = ['a0', 'a1', 'a2', 'a3']
         self.analogPinEnabled = {'a0':0,'a1':0,'a2':0,'a3':0}
         self.analogPinRaw = {'a0':0,'a1':0,'a2':0,'a3':0}
         self.analogPin_mV = {'a0':0.0,'a1':0.0,'a2':0.0,'a3':0.0}
         self.VCC = 0.0
         self.lastUpdateTime = 0
         self.sensorGroup = {}

    def defineSensor(self, Pin, sensorObject):
        self.sensorGroup[Pin] = sensorObject



