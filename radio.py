'''
  radio module
'''

# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=trailing-whitespace


import time
import serial
import sensor


ONEBIT = 0b1

#-------------------------------------------------------------------
#  Let's Setup a couple of functions that make it easier to work with
#  HEX Bytes

def get_bit(bit_mask, position):
    '''
      Utility Function that extracts a bit from a byte
      Should probably check on length of the bit_mask and the number of positions we are shifting the position... possible future refactor
    '''
    return (bit_mask >> position) & ONEBIT

def hex_dump(random_integer):
    '''
      hex_dump returns the hex representation of a number
    '''
    return hex(random_integer)[2:].zfill(2).upper()



class XBeeOnUSB(object):
    '''
      XBee On USB models the interaction with the Xbee radio that is acting as the translator of ZigBee Messages to
      computer logic via a USB serial port
    '''

    # Setup Context Manager on the Serial Port...  Open / Close
    # Support a Configuration File
    # Maybe send the inbound raw data to a log @ debug level
    # Potentially deliver complete messages instead of raw bytes
    # It's ok to XBee/ZigBee specific this object is about getting Zigbee Packets off the USB port

    # These are part of the Xbee Radio Object -- Future Refactor

    STARTFRAMEBYTE = 0x7e
    DATAFRAMEBYTE = 0x92


    #---------------------------------------------------------------------
    # Let's Setup the Serial Port where the Coordinator Xbee is attached
    # This should be refactored into an ???? Class and consideration for Linux vs Windows...
    # Maybe externalize the port definition into the radio.cfg file....  - Future Refactor


    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        '''
          Initializes the XbeeOnUSB Class
        '''

        self.port = port
        self.baud_rate = baudrate
        self.usb = serial.Serial()                   # This will be handle to the serial port
        self._start_frame = 0x7e                      # Just used as a constant
        self.frame_length = 0                         # Indicates the length of the ZigBee Protocol Data Frame
        self._byte_count = 0                          # Indicates how many bytes have been read
        self.actual_frame_type = 0x92                 # Will be the frame type we read in the packet
        self.expected_frame_type = 0x92               # We are always hoping for the 0x92 data frame type in this program
        self.serial_number = '0013A20040B97414'      # The serial number of the XBEE that sent the message
        self.network_address = '0000'                # The network address
        self.receive_type = 'Broadcast'              # Receive Type is either 'Acknowledge' or 'Broadcast'
        self.sample_set_count = 1                    # The number of sample sets in the packet -- Limited to 1 currently
        self.digital_channel_mask = {'d00': 0, 'd01': 0, 'd02': 0, 'd03': 0, 'd04': 0, 'd05': 0, 'd06': 0, 'd07': 0, 'd10': 0, 'd11': 0, 'd12': 0}
                                                     # Indicates the digital inputs that are enabled on the sending radio
        self.analog_channel_mask = {'a0': 0, 'a1': 0, 'a2': 0, 'a3': 0}
                                                     # Indicates the analog inputs that are enabled on the sending radio
        self.digital_data = {'d00': 0, 'd01': 0, 'd02': 0, 'd03': 0, 'd04': 0, 'd05': 0, 'd06': 0, 'd07': 0, 'd10': 0, 'd11': 0, 'd12': 0}
                                                     # The actual digital data on the digital pins
        self.analog_data = {'a0': 0, 'a1': 0, 'a2': 0, 'a3': 0, 'vcc': 0}
                                                     # The actual analog data from the packet
        self.analog_mV = {'a0': 0.0, 'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'vcc': 0.0}
                                                     # The mV readings on the analog inputs from the remote radio
        self.check_sum = 0x00                        # A Check sum -- to be calculated later                      

    def open(self):
        '''
          open() attempts to open the serial port based on the current configuration settings of port and baud rate
        '''
        self.usb.port = self.port
        self.usb.baudrate = self.baud_rate
        self.usb.open()

    def close(self):
        '''
          close() attempts to close the serial port
        '''
        self.usb.close()

    def __enter__(self):
        '''
          __enter__ implements context manager features for the class
        '''
        self.open()
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        '''
          __exit__ implements context manager features for the class
        '''
        self.close()

    def __str__(self):
        return 'Some Text tbd'

    def __repr__(self):
        return 'radio.XBeeOnUSB()'

    def _dict(self):
        '''
          Returns a Dictionary that summarizes the last frame read 
        '''
        return_val = {}
        return_val['frame_length'] = self.frame_length
        return_val['frame_type'] = self.actual_frame_type
        return_val['serial_number'] = self.serial_number
        return_val['network_address'] = self.network_address
        return_val['receive_type'] = self.receive_type
        return_val['digital_channel_mask'] = self.digital_channel_mask
        return_val['analog_channel_mask'] = self.analog_channel_mask
        return_val['digital_data'] = self.digital_data
        return_val['analog_data'] = self.analog_data
        return_val['analog_mV'] = self.analog_mV
        return return_val

        

    def _read_start_byte(self):
        '''
          Let's read bytes until either 5 seconds has passed or we get a start byte
        '''
        start_time = int(time.time())
        if self.usb.is_open:
            self.usb.reset_input_buffer()
            start_ord = ord(self.usb.read())
            while (start_time + 5) > int(time.time()) and start_ord != self._start_frame:
                start_ord = ord(self.usb.read())
            if start_ord == self._start_frame:
                self._byte_count = 0
                return
        else:
            print('You need to open the serial port before we can read from it.')


    def _read_frame_length(self):
        '''
          Let's read the two bytes that indicate the frame length
        '''
        msb_length_ord = ord(self.usb.read())
        lsb_length_ord = ord(self.usb.read())
        self.frame_length = (msb_length_ord * 256) + lsb_length_ord
        #    print "  Length: " + str(frameLength)
        self._byte_count = 0

    def _read_frame_type(self):
        '''
          Let's get the Frame Type Byte from the Frame...
        '''
        self.actual_frame_type = ord(self.usb.read())
        self._byte_count += 1

    def _read_serial_number(self):
        '''
          Let's get the Serial Number of the Sending Xbee from the Frame...
        '''
        sn_ord8 = ord(self.usb.read())
        sn_ord7 = ord(self.usb.read())
        sn_ord6 = ord(self.usb.read())
        sn_ord5 = ord(self.usb.read())
        sn_ord4 = ord(self.usb.read())
        sn_ord3 = ord(self.usb.read())
        sn_ord2 = ord(self.usb.read())
        sn_ord1 = ord(self.usb.read())
        self._byte_count += 8

        self.serial_number = hex_dump(sn_ord8) + hex_dump(sn_ord7) + hex_dump(sn_ord6) + hex_dump(sn_ord5) + hex_dump(sn_ord4) + hex_dump(sn_ord3) + hex_dump(sn_ord2) + hex_dump(sn_ord1)
        #print("  Sender Radio Serial Number: " + self.serial_number)

    def _read_network_address(self):
        '''
          Let's get the Network Address within the packet
        '''
        network_address_high_ord = ord(self.usb.read())
        network_address_low_ord = ord(self.usb.read())
        self._byte_count += 2
        self.network_address = hex_dump(network_address_high_ord) + hex_dump(network_address_low_ord)
        #print("  Source Network Address: " + self.network_address)

    def _read_receive_type(self):
        '''
          Let's get the Receive Type of the Packet.
            0x01 = Acknoledge
            0x02 = Broadcast
            0x?? = Unknown

        '''
        receive_type_ord = ord(self.usb.read())
        self._byte_count += 1


        if receive_type_ord == 0x01:
            self.receive_type = 'Acknowledge'
            #print("  Packet Acknowledged")
        elif receive_type_ord == 0x02:
            self.receive_type = 'Broadcast'
            #print("  Broadcast Packet")
        else:
            self.receive_type = 'Unknown'
            #print("  Unknown Receive Option")

    def _read_sample_set_count(self):
        '''
          Let's get the number of Sample Sets from the Frame Content...
             I think the only valide value at this time is 1
        '''
        self.sample_set_count = ord(self.usb.read())
        self._byte_count += 1
        #print("  Number of Sample Sets: " + str(self.sample_set_count))

    def _read_digital_channel_mask(self):
        '''
          Let's get the Digital Channel Mask that describes which Digital Pins are Enabled on the Sending Xbee
        '''
        digital_channel_mask_high = ord(self.usb.read())
        digital_channel_mask_low = ord(self.usb.read())
        self._byte_count += 2
        #print("  Digital IO High Mask: " + bin(digitalChannelMaskHigh)[2:].zfill(8) + " (" + HexDump(digitalChannelMaskHigh) + ")")
        #print("  Digital IO Low  Mask: " + bin(digitalChannelMaskLow)[2:].zfill(8) + " (" + HexDump(digitalChannelMaskLow) + ")")

        self.digital_channel_mask['d00'] = get_bit(digital_channel_mask_low, 0)
        self.digital_channel_mask['d01'] = get_bit(digital_channel_mask_low, 1)
        self.digital_channel_mask['d02'] = get_bit(digital_channel_mask_low, 2)
        self.digital_channel_mask['d03'] = get_bit(digital_channel_mask_low, 3)
        self.digital_channel_mask['d04'] = get_bit(digital_channel_mask_low, 4)
        self.digital_channel_mask['d05'] = get_bit(digital_channel_mask_low, 5)
        self.digital_channel_mask['d06'] = get_bit(digital_channel_mask_low, 6)
        self.digital_channel_mask['d07'] = get_bit(digital_channel_mask_low, 7)
        self.digital_channel_mask['d10'] = get_bit(digital_channel_mask_high, 2)
        self.digital_channel_mask['d11'] = get_bit(digital_channel_mask_high, 3)
        self.digital_channel_mask['d12'] = get_bit(digital_channel_mask_high, 4)

    def _read_analog_channel_mask(self):
        '''
          Let's get the Analog Channel Mask that describes which Analog Pins are Enabled on the Sending Xbee
        '''
        analog_channel_mask = ord(self.usb.read())
        self._byte_count += 1
        #print("  Analog  IO      Mask: " + bin(analogChannelMask)[2:].zfill(8) + " (" + hex(analogChannelMask)[2:].zfill(2) + ")")

        self.analog_channel_mask['a0'] = get_bit(analog_channel_mask, 0)
        self.analog_channel_mask['a1'] = get_bit(analog_channel_mask, 1)
        self.analog_channel_mask['a2'] = get_bit(analog_channel_mask, 2)
        self.analog_channel_mask['a3'] = get_bit(analog_channel_mask, 3)

    def _read_digital_data(self):
        '''
          If any of the Digital Pins were Enabled -- Let's get the Digital Data the remote Xbee sent...
        '''
        if any(self.digital_channel_mask['d00'],
               self.digital_channel_mask['d01'],
               self.digital_channel_mask['d02'],
               self.digital_channel_mask['d03'],
               self.digital_channel_mask['d04'],
               self.digital_channel_mask['d05'],
               self.digital_channel_mask['d06'],
               self.digital_channel_mask['d07'],
               self.digital_channel_mask['d10'],
               self.digital_channel_mask['d11'],
               self.digital_channel_mask['d12']):

            digital_channel_input_high = ord(self.usb.read())
            digital_channel_input_low = ord(self.usb.read())
            self._byte_count += 2
        
            self.digital_data['d00'] = get_bit(digital_channel_input_low, 0)
            self.digital_data['d01'] = get_bit(digital_channel_input_low, 1)
            self.digital_data['d02'] = get_bit(digital_channel_input_low, 2)
            self.digital_data['d03'] = get_bit(digital_channel_input_low, 3)
            self.digital_data['d04'] = get_bit(digital_channel_input_low, 4)
            self.digital_data['d05'] = get_bit(digital_channel_input_low, 5)
            self.digital_data['d06'] = get_bit(digital_channel_input_low, 6)
            self.digital_data['d07'] = get_bit(digital_channel_input_low, 7)
            self.digital_data['d10'] = get_bit(digital_channel_input_high, 2)
            self.digital_data['d11'] = get_bit(digital_channel_input_high, 3)
            self.digital_data['d12'] = get_bit(digital_channel_input_high, 4)
        else:
            self.digital_data['d00'] = 0
            self.digital_data['d01'] = 0
            self.digital_data['d02'] = 0
            self.digital_data['d03'] = 0
            self.digital_data['d04'] = 0
            self.digital_data['d05'] = 0
            self.digital_data['d06'] = 0
            self.digital_data['d07'] = 0
            self.digital_data['d10'] = 0
            self.digital_data['d11'] = 0
            self.digital_data['d12'] = 0


    def _read_analog_data(self, pin):
        '''
          Let's read an analog data value and convert it to mV as well
          Used on Analog pins that are enabled and on VCC if enabled on the sending radio
        '''
        analog_high_input = ord(self.usb.read())
        analog_low_input = ord(self.usb.read())
        self._byte_count += 2
        
        self.analog_data[pin] = (analog_high_input * 256) + analog_low_input
        self.analog_mV[pin] = (self.analog_data[pin]/1023.0) * 1200.0
        

    
    def _read_analog_channels(self):
        '''
          Let's cycle over the analog pins, if the pin is enabled (in the analog channel mask)
          then let's read the data on the pin
        '''
        for pin in self.analog_channel_mask:
            if self.analog_channel_mask[pin]:
                self._read_analog_data(pin)
            else:
                self.analog_data[pin] = 0
                self.analog_mV[pin] = 0.0
        
        # 15 -- Let's determine if the Radio Sent VCC
        pin = 'vcc'
        if (self._byte_count + 2) == self.frame_length:
            #print "  The Remote Radio provided VCC in the Frame."
            # Let's Assume this is a report of the VCC as an analog Value
            self._read_analog_data(pin)
        elif self._byte_count == self.frame_length:
            self.analog_data[pin] = 0
            self.analog_mV[pin] = 0.0
        else:
            #print(" The byte count is: " + str(byteCount) + " the frame length is: " + str(frameLength))
            self.analog_data[pin] = 0
            self.analog_mV[pin] = 0.0

    def _read_check_sum(self):
        '''
          Let's read the checksum byte from the frame
        '''
        self.check_sum = ord(self.usb.read())
        #print "  Check Sum : " + HexDump(checkSum)


    def read_frame(self):
        '''
          This returns a dictionary that has the essence of the raw radio message received

          Typically a radio message will formatted as follows:

            Byte  Example  Description
             0    0x7e     Start Byte -- Indicates the beginning of a data frame
             1    0x00     Length -- Number of Bytes (CheckSumByte# - 1 - 2)
             2    0x14
             3    0x92     Frame Type - 0x92 indicates this will be a broadcasted data sample
             4    0x00     64-Bit Source Address (aka Serial Number of the Sending Radio)
             5    0x13     Most Significant Byte is Byte 4 and the Least Significant Byte is Byte 11
             6    0xA2
             7    0x00
             8    0x40
             9    0x77
            10    0x9C
            11    0x49
            12    0x36    Source Network Address -- 16 Bit
            13    0x6A    
            14    0x01    Receive Options -- 01 = Packet Acknowledged -- 02 = Broadcast Packet
            15    0x01    Number of Sample Sets (Always set to 1 due to XBEE Limitations)
            16    0x00    Digital Channel Mask - Indicates which Digital Pins are enabled  (See below for a mapping)
            17    0x20
            18    0x01    Analog Channel Mask - Indicates which Analog Pins are enabled (See below for a mapping)
            19    0x00    Digital Sample Data (if any) - Maps the same as the Digital Channel Mask
            20    0x14    
            21    0x04    Analog Sample Data (if any)
            22    0x25    There will be two bytes here for every pin set for ADC
            23    0xF5    Checksum(0xFF - the 8 bit sum of the bytes from byte 3 to this byte)

            Digital Channel Mask
            First Byte
             0     1     2     3     4     5     6     7
            n/a   n/a   D12   D11   D10   n/a   n/a   n/a
            Second Byte
             0     1     2     3     4     5     6     7
             D7    D6    D5    D4    D3    D2    D1    D0

            Analog Channel Mask
            First Byte
             0     1     2     3     4     5     6     7
            n/a   n/a   n/a   n/a    A3    A2    A1    A0
            
        '''

        
        
        # 1 -- Let's read until we get a STARTFRAMEBYTE or 5 seconds has elapsed
        self._read_start_byte()
        # 2 -- Next lets get how long the frame should be...
        self._read_frame_length()
        # 3 -- Next lets get the dataframe type -- we are hoping for 0x92 data frames
        self._read_frame_type()
        # 4 -- Next lets get the serial number of the sending XBEE
        self._read_serial_number()
        # 5 -- Let's get the network Address
        self._read_network_address()
        # 6 -- Lets get the Receive Type of the Packet... Acknowledged or Broadbast
        self._read_receive_type()
        # 7 -- Let's get the number of sample sets 
        self._read_sample_set_count()
        # 8 -- Let's get the Digital Channel Mask
        self._read_digital_channel_mask()
        # 9 -- Let's get the Analog Channel Mask
        self._read_analog_channel_mask()
        # 10 -- Let's get the actual digital data on the Digital Pins if any are enabled.
        self._read_digital_data()
        # 11 -- Analog Pin 0 Data, if it was enabled...
        self._read_analog_channels()
        # 12 -- Read the Checksum Byte
        self._read_check_sum()

        return self._dict()

