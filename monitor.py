'''
  Monitor Definitions...
'''
import time

# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

class BasicMonitor(object):
    '''
      Defines a Basic Monitor Class...
      Used in Inheritance of the more specific monitors
    '''


    def __init__(self, Name, Description, Type, Kind, Subject='Unknown', Body='Unknown'):
        self.name = Name
        self.description = Description
        self.type = Type                    # ie Door, Water, Temperature
        # A little different than the Radio/Sensor Definitions
        self.kind = Kind
        self.__raised = False               # Private -- True for Raised, False for Not Raised
        # Private -- False for Pending Notification, True after Notification Sent out
        self.__notified = False
        # The last time in Epoch Seconds that the monitor latched
        self.__latch_time = int(time.time())
        self.latch_duration = 300            # The number of seconds between resets
        self.subject = Subject              # Used to store the Subject Line of an Email
        self.body = Body                    # Used to store the Body of the Email

    def raise_flag(self):
        '''
          Raises the monitor flag, resets notified to false and resets the latch time
        '''
        if not self.__raised:
            self.__raised = True
            self.__notified = False
            self.__latch_time = int(time.time())

    def clear_flag(self):
        '''
          Clears the monitor flag, resets notified to false and resets the latch time
        '''
        self.__raised = False
        self.__notified = False
        self.__latch_time = int(time.time())

    def set_notified(self):
        '''
          Sets the notified flag within the Monitor
        '''
        self.__notified = True

    def reset(self):
        '''
          Resets the monitored condition if the timer has expired
        '''
        if (self.__latch_time + self.latch_duration) < int(time.time()):
            self.__raised = False
            self.__notified = False

    def current_status(self):
        '''
          returns the raised flag, the notified flag, and the time until a reset is possible
        '''
        time_till_reset = self.latch_duration - \
            (int(time.time()) - self.__latch_time)
        return self.__raised, self.__notified, time_till_reset

    def __str__(self):
        if self.__raised:
            return 'Detected'
        else:
            return 'Not Detected'


class BaseTemperatureMonitor(BasicMonitor):
    '''
      Defining a Base Temperature Monitor -- again used for inheritence
    '''

    def __init__(self, Name, Threshold, Type, Kind, Units='degF', Description='Not to be instanced directly -- here for inheritence', Subject='Unknown', Body='Unknown'):
        '''
          Initialization of Base Temperature Monitor
        '''
        BasicMonitor.__init__(self, Name, Description,
                              Type, Kind, Subject, Body)
        self.threshold = Threshold
        self.units = Units


class LowTemperatureMonitor(BaseTemperatureMonitor):
    '''
      Defining a Low Temperature Monitor
    '''

    def __init__(self, Name, Threshold, Type='Temperature', Kind='BELOW THRESHOLD', Units='degF', Description='Monitor when the Temperature drops below Threshold'):
        '''
          Initializing a Low Temperature Monitor
        '''
        BaseTemperatureMonitor.__init__(self, Name, Threshold, Type, Kind,
                                        Units, Description, 'Low Temperature Detected', 'Check the furace')

    def check(self, actual_temperature):
        '''
          Check verifies if the actual temperature is below the threshold on the Low Temperature Monitor
          if it is... raise the monitor flag
        '''
        if actual_temperature < self.threshold:
            self.raise_flag()


class AtTemperatureMonitor(BaseTemperatureMonitor):
    '''
      Defining a Monitor that flags with a Temperature is at a specific temperature
    '''

    def __init__(self, Name, Threshold, Type='Temperature', Kind='AT Threshold', Units='degF', Description='Monitor when the Temperature is at the Threshold'):
        '''
          Initializing an At Temperature Monitor
        '''
        BaseTemperatureMonitor.__init__(self, Name, int(
            Threshold), Type, Kind, Units, Description, 'Temperature Attained', 'We hit the temp')

    def check(self, actual_temperature):
        '''
          Check verifies if the actual temperature is equal to the threshold on at At Temperature Monitor
          if it is...  raise the monitor flag
        '''
        if int(actual_temperature) == self.threshold:
            self.raise_flag()


class HighTemperatureMonitor(BaseTemperatureMonitor):
    '''
      Defining a montior that flags with a High Temperature condition
    '''

    def __init__(self, Name, Threshold, Type='Temperature', Kind='ABOVE THRESHOLD', Units='degF', Description='Monitor when the Temperature exceeds the Threshold'):
        '''
          Initializing a High Temperature Monitor
        '''
        BaseTemperatureMonitor.__init__(
            self, Name, Threshold, Type, Kind, Units, Description, 'Temperature is too high', 'Check the AC')

    def check(self, actual_temperature):
        '''
          Check verifies if the actual temperature is greater than the threshold defined on the High Temperature Monitor
          if it is... raise the monitor flag
        '''
        if actual_temperature > self.threshold:
            self.raise_flag()


class BaseMotionMonitor(BasicMonitor):
    '''
      Defining a Base Motion Monitor -- Used for inheritence
    '''

    def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Unknown', Body='Unknown'):
        '''
          Initialization of the Base Motion Monitor
        '''
        BasicMonitor.__init__(self, Name, Description,
                              Type, Kind, Subject, Body)
        self.trigger_value = TriggerValue

    def check(self, actual_motion_sensor_reading):
        '''
          Check verifies if the actual motion sensor reading is equal to the trigger value defined in the base motion detection montior
        '''
        if actual_motion_sensor_reading == self.trigger_value:
            self.raise_flag()



class MotionMonitor(BaseMotionMonitor):
    '''
      Defining a Motion Monitor that triggers when MOTION is detected
    '''
    def __init__(self, Name, Type='Motion', Kind='PIR', TriggerValue='MOTION', Description='Monitor when Motion is detected.'):
        '''
          Initalizing the Motion Monitor Class
        '''
        BaseMotionMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                   Description, 'MOTION Detected', 'Something was moving.')


class NoMotionMonitor(BaseMotionMonitor):
    '''
      Defining a Motion Monitor that triggers when STILL is detected
    '''
    def __init__(self, Name, Type='Motion', Kind='PIR', TriggerValue='STILL', Description='Monitor when a lack of motion is detected.'):
        '''
          Initializing the No Motion Monitor Class
        '''
        BaseMotionMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                   Description, 'Lack of Motion Detected', 'It stopped moving')


class BaseDoorMonitor(BasicMonitor):
    '''
       Defining a Base Door Monitor -- Used for inheritence
    '''

    def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Unknown', Body='Unknown'):
        '''
           Initializing a Base Door Monitor Class
        '''
        BasicMonitor.__init__(self, Name, Description,
                              Type, Kind, Subject, Body)
        self.trigger_value = TriggerValue

    def check(self, actual_door_sensor_reading):
        '''
          Check verifies if the actual door sensor reading is equal to the trigger value defined in the base door montior
        '''
        if actual_door_sensor_reading == self.trigger_value:
            self.raise_flag()



class DoorOpenMonitor(BaseDoorMonitor):
    '''
      Difining a monitor to trigger when a door is OPEN
    '''

    def __init__(self, Name, Type='Door', Kind='Position', TriggerValue='OPEN', Description='Monitor when the DOOR is OPEN'):
        '''
          Initializing a Door Open Monitor Class
        '''
        BaseDoorMonitor.__init__(
            self, Name, Type, Kind, TriggerValue, Description, 'DOOR OPEN', 'The Door was opened')


class DoorClosedMonitor(BaseDoorMonitor):
    '''
      Difining a monitor to trigger when a door is CLOSED
    '''
    def __init__(self, Name, Type='Door', Kind='Position', TriggerValue='CLOSED', Description='Monitor when the DOOR is CLOSED'):
        '''
          Initializing a Door Closed Monitor Class
        '''
        BaseDoorMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                 Description, 'DOOR CLOSED', 'The Door was Closed')


class BaseWaterMonitor(BasicMonitor):
    '''
      Defining a Base Water Monitor -- Used for inheritence
    '''
    def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Uknonwn', Body='Unknown'):
        '''
          Initializing a Base Water Monitor Class
        '''
        BasicMonitor.__init__(self, Name, Description,
                              Type, Kind, Subject, Body)
        self.trigger_value = TriggerValue

    def check(self, actual_water_sensor_reading):
        '''
          Check verifies if the actual water sensor reading is equal to the trigger value defined in the base water montior
        '''
        if actual_water_sensor_reading == self.trigger_value:
            self.raise_flag()


class WaterWetMonitor(BaseWaterMonitor):
    '''
      Defining a monitor to trigger when the sensor is wet
    '''

    def __init__(self, Name, Type='Water', Kind='Resistive Pad', TriggerValue='WET', Description='Monitor when the SENSOR is WET'):
        '''
          Initializing a Water Monitor looking for WET
        '''
        BaseWaterMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                  Description, 'WATER DETECTED', 'There is Water on the Floor')


class WaterDryMonitor(BaseWaterMonitor):
    '''
      Defining a monitor to trigger when the sensor is dry
    '''

    def __init__(self, Name, Type='Water', Kind='Resistive Pad', TriggerValue='DRY', Description='Monitor when the SENSOR is DRY'):
        '''
          Initializing a Water Monitor looking for DRY
        '''
        BaseWaterMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                  Description, 'No Water Detected', 'There is NO Water')


class BasePowerMonitor(BasicMonitor):
    '''
      Defining a Base Power Monitor -- Used for inheritence
    '''
    def __init__(self, Name, Type, Kind, TriggerValue, Description='Not to be instanced directly -- here for inheritence', Subject='Uknown', Body='Unknown'):
        '''
          Initializing a Base Power Monitor Class
        '''
        BasicMonitor.__init__(self, Name, Description,
                              Type, Kind, Subject, Body)
        self.trigger_value = TriggerValue

    def check(self, actual_power_sensor_reading):
        '''
          Check verifies if the actual power sensor reading is equal to the trigger value defined in the base power montior
        '''
        if actual_power_sensor_reading == self.trigger_value:
            self.raise_flag()


class PowerOutMonitor(BasePowerMonitor):
    '''
      Defining a Monitor to Trigger when the power is OUT...
      a little tricky -- this type of thing only works if the system in on UPS including the Internet Connection
    '''

    def __init__(self, Name, Type='Power', Kind='Pi GPIO', TriggerValue='OUT', Description='Monitor when the Power is Out'):
        '''
          Initializing a Power Outage Monitor Class
        '''
        BasePowerMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                  Description, 'The POWER is OUT', 'The Power is OUT')


class PowerNormalMonitor(BasePowerMonitor):
    '''
      Defining a Monitor to Trigger when the power is NORMAL...
    '''

    def __init__(self, Name, Type='Power', Kind='Pi GPIO', TriggerValue='NORMAL', Description='Monitor when the Power is Normal (ON)'):
        '''
          Initializing a monitor that triggers when the power is NORMAL
        '''
        BasePowerMonitor.__init__(self, Name, Type, Kind, TriggerValue,
                                  Description, 'The POWER is Available', 'The POWER IS ON')
