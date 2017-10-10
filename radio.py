'''
  radio module
'''

# pylint: disable=line-too-long

class Radio:
    '''
      Defines the XBee Radio Class - from a physical perspective
      This Class puts the XBee Radio in a Room
      This Class allows for the adding of sensors to the analog and digital pins
      The sub-class of Sensor allows for the adding of monitors to sensors
    '''

    def __init__(self, roomName, radioSN):
        self.room_name = roomName
        self.radio_serial_number = radioSN
        self.dPINs = ['d00', 'd01', 'd02', 'd03', 'd04', 'd05', 'd06', 'd07', 'd10', 'd11', 'd12']
        self.digital_pin_enabled = {'d00': 0, 'd01': 0, 'd02': 0, 'd03': 0, 'd04': 0, 'd05': 0, 'd06': 0, 'd07': 0, 'd10': 0, 'd11': 0, 'd12': 0}
        self.digital_pin_value = {'d00': 0, 'd01': 0, 'd02': 0, 'd03': 0, 'd04': 0, 'd05': 0, 'd06': 0, 'd07': 0, 'd10': 0, 'd11': 0, 'd12': 0}
        self.aPINs = ['a0', 'a1', 'a2', 'a3']
        self.analog_pin_enabled = {'a0': 0, 'a1': 0, 'a2': 0, 'a3': 0}
        self.analog_pin_raw = {'a0': 0, 'a1': 0, 'a2': 0, 'a3': 0}
        self.analog_pin_mV = {'a0': 0.0, 'a1': 0.0, 'a2': 0.0, 'a3': 0.0}
        self.VCC = 0.0
        self.last_update_time = 0
        self.sensor_group = {}

    def define_sensor(self, pin, sensor_object):
        '''
          Add / Define a Sensor to the sensor_group within the Radio Object
        '''
        self.sensor_group[pin] = sensor_object
