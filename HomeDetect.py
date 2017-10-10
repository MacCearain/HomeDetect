'''
  HomeDetect -- Opens a Serial port expecting a Xbee Radio that is configured as a
  controller that reads all broadcasts from other Xbee's in the Network
  It then puts the actual reading into the configurations that are expected
  for each of the radios on the network
  The Radios are positioned roughly in a one room per radio arrangement.
  Some have Temperature Sensors attached, Some have Water Detectors, Some have Motion
  Detectors and the Garage door has a position sensor (UP or DOWN)
'''

# pylint: disable=line-too-long


import serial
import datetime
import time
import configparser

import McMail


import radio
import sensor
import monitor

import Person


# These are part of the Xbee Radio Object -- Future Refactor
STARTFRAMEBYTE = 0x7e
DATAFRAMEBYTE = 0x92
ONEBIT = 0b1

ON = 1
OFF = 0



#-----------------------------------------------------------------------
# Let's Setup some People using the Person import
# This data needs to be externalized from the program into a JSON file or CSV file or SQLite table -- Future Refactor

Paul = Person.Person('Paul', 'McC', 'M', '(555) 555-1212', 'address@gmail.com', '5555551212@vtext.com', 'Yes', 'Yes')
Mike = Person.Person('Mike', 'McC', 'E', '(555) 555-1212', 'address@gmail.com', '5555551212@vtext.com', 'No', 'No')
Gail = Person.Person('Gail', 'McC', 'A', '(555) 999-9999', 'address@gmail.com', '5555551212@vtext.com', 'No', 'No')
Emmy = Person.Person('Emmy', 'McC', 'M', '(555) 555-1212', 'address@gmail.com', ' ', 'Yes', 'No')

People = {'Paul':Paul, 'Mike': Mike, 'Gail': Gail, 'Emmy': Emmy}


#---------------------------------------------------------------------
# Let's Setup the ability to Send Email and Send the Power Back On Emails
# This should be refactored into a clear setup function - Future Refactor

subject = 'LakePi - Alert - The Monitor was started'
body = '\n\n\n\nThe Lake House has Power.\n\nMesssage Sent at: ' + str(datetime.datetime.now())

with McMail.McMail() as mailServer:
    for CurrentPerson in People:
        for CurrentNotify in People[CurrentPerson].notification_subscriptions:
            #print('Lets Notify %s at %s with Power UP Email' % (CurrentPerson, People[CurrentPerson].notification_subscriptions[CurrentNotify]))
            mailServer.sendMessage(People[CurrentPerson].notification_subscriptions[CurrentNotify], subject, body)


#-----------------------------------------------------------
#  Let's Setup the Rooms, Radios, Sensors, Monitors, and a Rooms Dictionary

# dPINs (digital PINs) and aPINS (analog PINs) should be refactored into a Xbee Radio Class = Future Refactor
dPINs = ['d00', 'd01', 'd02', 'd03', 'd04', 'd05', 'd06', 'd07', 'd10', 'd11', 'd12']
aPINs = ['a0', 'a1', 'a2', 'a3']


# The list of Expected Radios and which sensors are attached to them should be externalized into
# a JSON file, CSV file, or SQLite Table - Future Refactor
# Maybe Locations should be collections of Rooms...
basementRadioSerialNumber = '0013A20040B97414'
Basement = radio.Radio('Basement', basementRadioSerialNumber)

Basement.define_sensor('a1', sensor.TMP36('a1'))
Basement.sensor_group['a1'].define_monitor('HighTemp', monitor.HighTemperatureMonitor('HighTemp', 85.0))
Basement.sensor_group['a1'].define_monitor('LowTemp', monitor.LowTemperatureMonitor('LowTemp', 60.0))

Basement.define_sensor('d02', sensor.WaterSensor('d02'))
Basement.sensor_group['d02'].define_monitor('Water', monitor.WaterWetMonitor('Water'))

Basement.define_sensor('d10', sensor.MotionSensor('d10'))
Basement.sensor_group['d10'].define_monitor('Motion', monitor.MotionMonitor('Motion'))

bedroomRadioSerialNumber = '0013A20040C04D95'
Bedroom = radio.Radio('Bedroom', bedroomRadioSerialNumber)

Bedroom.define_sensor('a1', sensor.TMP36('a1'))
Bedroom.sensor_group['a1'].define_monitor('HighTemp', monitor.HighTemperatureMonitor('HighTemp', 90.0))
Bedroom.sensor_group['a1'].define_monitor('LowTemp', monitor.LowTemperatureMonitor('LowTemp', 60.0))

Bedroom.define_sensor('d02', sensor.MotionSensor('d02'))
Bedroom.sensor_group['d02'].define_monitor('Motion', monitor.MotionMonitor('Motion'))

Bedroom.define_sensor('d10', sensor.ToggleSwitch('d10'))


garageRadioSerialNumber = '0013A20099999999'
Garage = radio.Radio('Garage', garageRadioSerialNumber)

Garage.define_sensor('a1', sensor.TMP36('a1'))
Garage.sensor_group['a1'].define_monitor('HighTemp', monitor.HighTemperatureMonitor('HighTemp', 100.0))
Garage.sensor_group['a1'].define_monitor('LowTemp', monitor.LowTemperatureMonitor('LowTemp', -10.0))

Garage.define_sensor('d02', sensor.DoorSwitch('d02'))
Garage.sensor_group['d02'].define_monitor('BigDoor', monitor.DoorOpenMonitor('BigDoor'))

Garage.define_sensor('d10', sensor.MotionSensor('d10'))
Garage.sensor_group['d10'].define_monitor('Motion', monitor.MotionMonitor('Motion'))


Rooms = {'Basement':Basement, 'Bedroom':Bedroom, 'Garage':Garage}
CurrentRoom = Rooms['Basement']


#---------------------------------------------------------------------
# Let's Setup the Serial Port where the Coordinator Xbee is attached
# This should be refactored into an ???? Class and consideration for Linux vs Windows...
# Maybe externalize the port definition into the HomeDetect.cfg file....  - Future Refactor


xbee = serial.Serial(port='/dev/ttyUSB0', baudrate=9600)
#print(xbee.portstr)



#-------------------------------------------------------------------
#  Let's Setup a couple of functions that make it easier to work with
#  HEX Bytes

def GetBit(BitMask, Position):
    return (BitMask >> Position) & ONEBIT

def HexDump(RandomInteger):
    return hex(RandomInteger)[2:].zfill(2).upper()


while True:

    startTime = int(time.time())
    xbee.flushInput()

    #-------------------------------------------------------------------------
    # Let's Loop for a bit to get some data from the Remote Data Transmitters

    while (startTime + 200) > int(time.time()):
        # -----------------------------------------------
        # Let's just get a Byte off the Serial Buffer....
        tmpOrd = ord(xbee.read())
        #print 'Start Time: ' + str(startTime) + str(int(time.time()))

        # -------------------------------------------------------------------
        # If the byte in tmpOrd is equal to a the Start of Frame Indicator...
        #     Then the Last Frame is Finished and we herald a New Frame....
        if tmpOrd == STARTFRAMEBYTE:
            #print "Start of Frame: " + HexDump(tmpOrd)
            #print "  Time Stamp: " + str(datetime.datetime.now())


            # ------------------------------------------
            # Let's get how long this Frame should be...
            msbLengthOrd = ord(xbee.read())
            lsbLengthOrd = ord(xbee.read())

            frameLength = (msbLengthOrd * 256) + lsbLengthOrd
            #print "  Length: " + str(frameLength)
            byteCount = 0

            # -----------------------------------------------
            # Let's get the Frame Type Byte from the Frame...

            frameTypeOrd = ord(xbee.read())
            byteCount += 1
            if frameTypeOrd == DATAFRAMEBYTE:
                #print "  Data Frame (0x92) "


                # ----------------------------------------------------------------
                # Let's get the Serial Number of the Sending Xbee from the Frame...

                snOrd8 = ord(xbee.read())
                snOrd7 = ord(xbee.read())
                snOrd6 = ord(xbee.read())
                snOrd5 = ord(xbee.read())
                snOrd4 = ord(xbee.read())
                snOrd3 = ord(xbee.read())
                snOrd2 = ord(xbee.read())
                snOrd1 = ord(xbee.read())
                byteCount += 8

                serialNumber = HexDump(snOrd8) + HexDump(snOrd7) + HexDump(snOrd6) + HexDump(snOrd5) + HexDump(snOrd4) + HexDump(snOrd3) + HexDump(snOrd2) + HexDump(snOrd1)
                #print "  Sender Serial: " + serialNumber
                if serialNumber == basementRadioSerialNumber:
                    #   print "  Sent from the Basement Radio"
                    CurrentRoom = Rooms['Basement']
                elif serialNumber == bedroomRadioSerialNumber:
                    #   print "  Sent from the Bedroom Radio"
                    CurrentRoom = Rooms['Bedroom']
                elif serialNumber == garageRadioSerialNumber:
                    #   print("  Sent from the Garage Radio")
                    CurrentRoom = Rooms['Garage']
                else:
                    print("  Sent from an UNKNOWN Radio")
                    Rooms[serialNumber] = Room.Radio(serialNumber, serialNumber)
                    CurrentRoom = Rooms[serialNumber]

                # -----------------------------------------------------------------
                # Let's get the Network Address within the content of the Frame...

                sourceNetworkAddressHighOrd = ord(xbee.read())
                sourceNetworkAddressLowOrd = ord(xbee.read())
                byteCount += 2
                sourceNetworkAddress = HexDump(sourceNetworkAddressHighOrd) + HexDump(sourceNetworkAddressLowOrd)
                #print "  Source Network Address: " + sourceNetworkAddress


                # -------------------------------------------------------------------------
                # Let's get the Receive Type of the Packet... Acknowledged or Broadcast....
                receiveOptOrd = ord(xbee.read())
                byteCount += 1


                #if receiveOptOrd == 0x01:
                #    print "  Packet Acknowledged"
                #elif receiveOptOrd == 0x02:
                #    print "  Broadcast Packet"
                #else:
                #    print "  Unknown Receive Option"


                # -------------------------------------------------------------
                # Let's get the number of Sample Sets from the Frame Content...
                #    I think the only valid value at this time is 1
                numberOSampleSets = ord(xbee.read())
                byteCount += 1
                #print "  Number of Sample Sets: " + str(numberOSampleSets)



                # -------------------------------------------------------------------------------------------------------
                #                 # Let's get the Digital Channel Mask that describes which Digital Pins are Enabled on the Sending Xbee...
                digitalChannelMaskHigh = ord(xbee.read())
                digitalChannelMaskLow = ord(xbee.read())
                byteCount += 2
                #print "  Digital IO High Mask: " + bin(digitalChannelMaskHigh)[2:].zfill(8) + " (" + HexDump(digitalChannelMaskHigh) + ")"
                #print "  Digital IO Low  Mask: " + bin(digitalChannelMaskLow)[2:].zfill(8) + " (" + HexDump(digitalChannelMaskLow) + ")"

                d00Enabled = GetBit(digitalChannelMaskLow, 0)
                d01Enabled = GetBit(digitalChannelMaskLow, 1)
                d02Enabled = GetBit(digitalChannelMaskLow, 2)
                d03Enabled = GetBit(digitalChannelMaskLow, 3)
                d04Enabled = GetBit(digitalChannelMaskLow, 4)
                d05Enabled = GetBit(digitalChannelMaskLow, 5)
                d06Enabled = GetBit(digitalChannelMaskLow, 6)
                d07Enabled = GetBit(digitalChannelMaskLow, 7)
                d10Enabled = GetBit(digitalChannelMaskHigh, 2)
                d11Enabled = GetBit(digitalChannelMaskHigh, 3)
                d12Enabled = GetBit(digitalChannelMaskHigh, 4)

                CurrentRoom.digitalPinEnabled['d00'] = d00Enabled
                CurrentRoom.digitalPinEnabled['d01'] = d01Enabled
                CurrentRoom.digitalPinEnabled['d02'] = d02Enabled
                CurrentRoom.digitalPinEnabled['d03'] = d03Enabled
                CurrentRoom.digitalPinEnabled['d04'] = d04Enabled
                CurrentRoom.digitalPinEnabled['d05'] = d05Enabled
                CurrentRoom.digitalPinEnabled['d06'] = d06Enabled
                CurrentRoom.digitalPinEnabled['d07'] = d07Enabled
                CurrentRoom.digitalPinEnabled['d10'] = d10Enabled
                CurrentRoom.digitalPinEnabled['d11'] = d11Enabled
                CurrentRoom.digitalPinEnabled['d12'] = d12Enabled

                # --------------------------------------------------------------------------------------------------
                # Let's get the Analog Channel Mask that describes which Analog Pins are Enabled on the Sending Xbee
                analogChannelMask = ord(xbee.read())
                byteCount += 1
                #print "  Analog  IO      Mask: " + bin(analogChannelMask)[2:].zfill(8) + " (" + hex(analogChannelMask)[2:].zfill(2) + ")"

                a0Enabled = GetBit(analogChannelMask, 0)
                a1Enabled = GetBit(analogChannelMask, 1)
                a2Enabled = GetBit(analogChannelMask, 2)
                a3Enabled = GetBit(analogChannelMask, 3)

                CurrentRoom.analogPinEnabled['a0'] = a0Enabled
                CurrentRoom.analogPinEnabled['a1'] = a1Enabled
                CurrentRoom.analogPinEnabled['a2'] = a2Enabled
                CurrentRoom.analogPinEnabled['a3'] = a3Enabled



                # -----------------------------------------------------------------------------------------------------------
                # If any of the Digital Pins were Enabled for Broadcast -- Let's get the Digital Data the remote Xbee sent...
                if d00Enabled or d01Enabled or d02Enabled or d03Enabled or d04Enabled or d05Enabled or d06Enabled or d07Enabled or d10Enabled or d11Enabled or d12Enabled:
                    digitalChannelInputHigh = ord(xbee.read())
                    digitalChannelInputLow = ord(xbee.read())
                    byteCount += 2

                    d00Data = GetBit(digitalChannelInputLow, 0)
                    d01Data = GetBit(digitalChannelInputLow, 1)
                    d02Data = GetBit(digitalChannelInputLow, 2)
                    d03Data = GetBit(digitalChannelInputLow, 3)
                    d04Data = GetBit(digitalChannelInputLow, 4)
                    d05Data = GetBit(digitalChannelInputLow, 5)
                    d06Data = GetBit(digitalChannelInputLow, 6)
                    d07Data = GetBit(digitalChannelInputLow, 7)
                    d10Data = GetBit(digitalChannelInputHigh, 2)
                    d11Data = GetBit(digitalChannelInputHigh, 3)
                    d12Data = GetBit(digitalChannelInputHigh, 4)
                else:
                    d00Data = 0
                    d01Data = 0
                    d02Data = 0
                    d03Data = 0
                    d04Data = 0
                    d05Data = 0
                    d06Data = 0
                    d07Data = 0
                    d10Data = 0
                    d11Data = 0
                    d12Data = 0

                CurrentRoom.digitalPinValue['d00'] = d00Data
                CurrentRoom.digitalPinValue['d01'] = d01Data
                CurrentRoom.digitalPinValue['d02'] = d02Data
                CurrentRoom.digitalPinValue['d03'] = d03Data
                CurrentRoom.digitalPinValue['d04'] = d04Data
                CurrentRoom.digitalPinValue['d05'] = d05Data
                CurrentRoom.digitalPinValue['d06'] = d06Data
                CurrentRoom.digitalPinValue['d07'] = d07Data
                CurrentRoom.digitalPinValue['d10'] = d10Data
                CurrentRoom.digitalPinValue['d11'] = d11Data
                CurrentRoom.digitalPinValue['d12'] = d12Data

                for CurrentPIN in dPINs:
                    if CurrentPIN in CurrentRoom.sensorGroup:
                        CurrentRoom.sensorGroup[CurrentPIN].setDigitalValue(CurrentRoom.digitalPinValue[CurrentPIN])

                #print "  Digital Pin 00 Enabled / Data: " + str(d00Enabled) + " / " + str(d00Data)
                #print "  Digital Pin 01 Enabled / Data: " + str(d01Enabled) + " / " + str(d01Data)
                #print "  Digital Pin 02 Enabled / Data: " + str(d02Enabled) + " / " + str(d02Data)
                #print "  Digital Pin 03 Enabled / Data: " + str(d03Enabled) + " / " + str(d03Data)
                #print "  Digital Pin 04 Enabled / Data: " + str(d04Enabled) + " / " + str(d04Data)
                #print "  Digital Pin 05 Enabled / Data: " + str(d05Enabled) + " / " + str(d05Data)
                #print "  Digital Pin 06 Enabled / Data: " + str(d06Enabled) + " / " + str(d06Data)
                #print "  Digital Pin 07 Enabled / Data: " + str(d07Enabled) + " / " + str(d07Data)
                #print "  Digital Pin 10 Enabled / Data: " + str(d10Enabled) + " / " + str(d10Data)
                #print "  Digital Pin 11 Enabled / Data: " + str(d11Enabled) + " / " + str(d11Data)
                #print "  Digital Pin 12 Enabled / Data: " + str(d12Enabled) + " / " + str(d12Data)

                # ------------------------------------------------------------------------------
                # If Ananlog 0 was Enabled -- Let's get the Analog Value on Pin 0 from the Frame
                if a0Enabled:
                    aChannelInputHigh = ord(xbee.read())
                    aChannelInputLow = ord(xbee.read())
                    byteCount += 2
                    a0Data = (aChannelInputHigh * 256) + aChannelInputLow
                    a0mV = (a0Data/1023.0) * 1200.0
                else:
                    a0Data = 0
                    a0mV = 0.0

                CurrentRoom.analogPinRaw['a0'] = a0Data
                CurrentRoom.analogPin_mV['a0'] = a0mV

                if 'a0' in CurrentRoom.sensorGroup:
                    CurrentRoom.sensorGroup['a0'].setAnalogValue(a0mV)

                # ------------------------------------------------------------------------------
                # If Ananlog 1 was Enabled -- Let's get the Analog Value on Pin a1 from the Frame
                if a1Enabled:
                    aChannelInputHigh = ord(xbee.read())
                    aChannelInputLow = ord(xbee.read())
                    byteCount += 2
                    a1Data = (aChannelInputHigh * 256) + aChannelInputLow
                    a1mV = (a1Data/1023.0) * 1200.0
                else:
                    a1Data = 0
                    a1mV = 0.0

                CurrentRoom.analogPinRaw['a1'] = a1Data
                CurrentRoom.analogPin_mV['a1'] = a1mV

                if 'a1' in CurrentRoom.sensorGroup:
                    CurrentRoom.sensorGroup['a1'].setAnalogValue(a1mV)
                    #if CurrentRoom.sensorGroup['a1'].sensorKind == 'Temperature':
                        #print "  The Temperature of the  %s (Sensor: %s) is: %.0f degF " % (CurrentRoom.roomName, CurrentRoom.sensorGroup['a1'].sensorName , CurrentRoom.sensorGroup['a1'].TempReading('degF'))
                        #print "mv: %s RAW: %s" % (a1mV, a1Data)
                        #print "My New Temp: %s" % ((a1mV-500.0)/10.0)
                        #print aChannelInputHigh
                        #print aChannelInputLow

                # ------------------------------------------------------------------------------
                # If Ananlog 2 was Enabled -- Let's get the Analog Value on Pin 2 from the Frame
                if a2Enabled:
                    aChannelInputHigh = ord(xbee.read())
                    aChannelInputLow = ord(xbee.read())
                    byteCount += 2
                    a2Data = (aChannelInputHigh * 256) + aChannelInputLow
                    a2mV = (a2Data/1023.0) * 1200.0
                else:
                    a2Data = 0
                    a2mV = 0.0

                CurrentRoom.analogPinRaw['a2'] = a2Data
                CurrentRoom.analogPin_mV['a2'] = a2mV

                if 'a2' in CurrentRoom.sensorGroup:
                    CurrentRoom.sensorGroup['a2'].setAnalogValue(a2mV)

                # ------------------------------------------------------------------------------
                # If Ananlog 3 was Enabled -- Let's get the Analog Value on Pin 3 from the Frame
                if a3Enabled:
                    aChannelInputHigh = ord(xbee.read())
                    aChannelInputLow = ord(xbee.read())
                    byteCount += 2
                    a3Data = (aChannelInputHigh * 256) + aChannelInputLow
                    a3mV = (a3Data/1023.0) * 1200.0
                else:
                    a3Data = 0
                    a3mV = 0.0

                CurrentRoom.analogPinRaw['a3'] = a3Data
                CurrentRoom.analogPin_mV['a3'] = a3mV

                if 'a3' in CurrentRoom.sensorGroup:
                    CurrentRoom.sensorGroup['a3'].setAnalogValue(a3mV)

                #print "  Analog Pin 0 Enabled -- mV: " + str(a0Enabled) + " -- " + str(int(a0mV))
                #print "  Analog Pin 1 Enabled -- mV: " + str(a1Enabled) + " -- " + str(int(a1mV))
                #print "  Analog Pin 2 Enabled -- mV: " + str(a2Enabled) + " -- " + str(int(a2mV))
                #print "  Analog Pin 3 Enabled -- mV: " + str(a3Enabled) + " -- " + str(int(a3mV))

                if (byteCount + 2) == frameLength:
                    #print "  The Remote Radio provided VCC in the Frame."
                    # Let's Assume this is a report of the VCC as an analog Value
                    aChannelInputHigh = ord(xbee.read())
                    aChannelInputLow = ord(xbee.read())
                    byteCount += 2
                    aVCCData = (aChannelInputHigh * 256) + aChannelInputLow
                    aVCCmV = (aVCCData/1023.0) * 1200.0
                elif byteCount == frameLength:
                    aVCCData = 0
                    aVCCmV = 0.0
                else:
                    print(" The byte count is: " + str(byteCount) + " the frame length is: " + str(frameLength))
                    aVCCData = 0
                    aVCCmV = 0.0

                CurrentRoom.VCC = aVCCmV
                CurrentRoom.lastUpdateTime = int(time.time())

                #print "  VCC (mV): " + str(int(aVCCmV))

                # ------------------------------------------
                # Let's get the Checksum Byte from the Frame
                checkSum = ord(xbee.read())
                #print "  Check Sum : " + HexDump(checkSum)

            else:
                print("  Unknown Frame Type: " + HexDump(frameTypeOrd))



    for CurrentRoom in Rooms:
        for CurrentSensor in Rooms[CurrentRoom].sensorGroup:

            if Rooms[CurrentRoom].sensorGroup[CurrentSensor].sensorKind == 'Temperature':
                print("%s %s %s %.0f degF" % (Rooms[CurrentRoom].roomName, Rooms[CurrentRoom].sensorGroup[CurrentSensor].sensorName, Rooms[CurrentRoom].sensorGroup[CurrentSensor].sensorKind, Rooms[CurrentRoom].sensorGroup[CurrentSensor].TempReading('degF')))

            for CurrentMonitor in Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup:
                MonitorFlagged, NotifiedFlag, TimeTillReset = Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].CurrentStatus()

                print('Room: %s Sensor Type: %s Sensor Kind: %s Monitor Name: %s Monitor Status: %s Notified: %s TimeTillReset: %s' % (Rooms[CurrentRoom].roomName, Rooms[CurrentRoom].sensorGroup[CurrentSensor].sensorType, Rooms[CurrentRoom].sensorGroup[CurrentSensor].sensorKind, Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].Name, MonitorFlagged, NotifiedFlag, TimeTillReset))

                if MonitorFlagged and not NotifiedFlag:
                    #Let's Notify Everybody about this Flagged Monitor, but only once
                    CurrentSubject = 'LakePi - Alert - ' + CurrentRoom + ' - ' + Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].Subject
                    CurrentBody = Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].Body

                    with McMail.McMail() as mailServer:
                        for CurrentPerson in People:
                            for CurrentNotify in People[CurrentPerson].NotificationSubscriptions:
                                mailServer.sendMessage(People[CurrentPerson].NotificationSubscriptions[CurrentNotify], CurrentSubject, CurrentBody)

                    Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].SetNotified()

                MonitorFlagged, NotifiedFlag, TimeTillReset = Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].CurrentStatus()
                if MonitorFlagged and NotifiedFlag and (TimeTillReset <= 0):
                    Rooms[CurrentRoom].sensorGroup[CurrentSensor].monitorGroup[CurrentMonitor].Reset()



        if (Rooms[CurrentRoom].lastUpdateTime + 1800) < int(time.time()):
            print("The %s radio is not updating." % CurrentRoom)
            Rooms[CurrentRoom].lastUpdateTime = int(time.time())
            # Let's Notify Everybody about not hearing from the Radio we expected to hear from...

            subject = 'LakePi - Alert - MISSING XBEE Radio'
            body = '\n\n\n\nThe %s Radio is not communicating.\n\nMesssage Sent at %s: ' % (CurrentRoom, str(datetime.datetime.now()))



            with McMail.McMail() as mailServer:
                for CurrentPerson in People:
                    for CurrentNotify in People[CurrentPerson].NotificationSubscriptions:
                        mailServer.sendMessage(People[CurrentPerson].NotificationSubscriptions[CurrentNotify], subject, body)
