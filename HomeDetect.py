'''
  HomeDetect -- uses a Radio Class to open a serial port expecting a Xbee Radio that is configured as a
  controller that reads all broadcasts from other Xbee's in the Network
  It then puts the actual reading into the configurations that are expected
  for each of the Rooms on the network
  The Radios are positioned exactly in a one room per radio arrangement.
  This could change in the future == but it's the intial implementation
  Some have Temperature Sensors attached, Some have Water Detectors, Some have Motion
  Detectors and the Garage door has a position sensor (UP or DOWN)
'''

# pylint: disable=line-too-long


import datetime
import time
import configparser

import McMail
import radio
from room import Room
import person



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




# The list of Expected Radios and which sensors are attached to them should be externalized into
# a JSON file, CSV file, or SQLite Table - Future Refactor
# Maybe Locations should be collections of Rooms...
basementRadioSerialNumber = '0013A20040B97414'
Basement = Room('Basement', basementRadioSerialNumber)

Basement.define_sensor('a1', sensor.TMP36('a1'))
Basement.sensor_group['a1'].define_monitor('HighTemp', monitor.HighTemperatureMonitor('HighTemp', 85.0))
Basement.sensor_group['a1'].define_monitor('LowTemp', monitor.LowTemperatureMonitor('LowTemp', 60.0))

Basement.define_sensor('d02', sensor.WaterSensor('d02'))
Basement.sensor_group['d02'].define_monitor('Water', monitor.WaterWetMonitor('Water'))

Basement.define_sensor('d10', sensor.MotionSensor('d10'))
Basement.sensor_group['d10'].define_monitor('Motion', monitor.MotionMonitor('Motion'))

bedroomRadioSerialNumber = '0013A20040C04D95'
Bedroom = Room('Bedroom', bedroomRadioSerialNumber)

Bedroom.define_sensor('a1', sensor.TMP36('a1'))
Bedroom.sensor_group['a1'].define_monitor('HighTemp', monitor.HighTemperatureMonitor('HighTemp', 90.0))
Bedroom.sensor_group['a1'].define_monitor('LowTemp', monitor.LowTemperatureMonitor('LowTemp', 60.0))

Bedroom.define_sensor('d02', sensor.MotionSensor('d02'))
Bedroom.sensor_group['d02'].define_monitor('Motion', monitor.MotionMonitor('Motion'))

Bedroom.define_sensor('d10', sensor.ToggleSwitch('d10'))


garageRadioSerialNumber = '0013A20099999999'
Garage = Room('Garage', garageRadioSerialNumber)

Garage.define_sensor('a1', sensor.TMP36('a1'))
Garage.sensor_group['a1'].define_monitor('HighTemp', monitor.HighTemperatureMonitor('HighTemp', 100.0))
Garage.sensor_group['a1'].define_monitor('LowTemp', monitor.LowTemperatureMonitor('LowTemp', -10.0))

Garage.define_sensor('d02', sensor.DoorSwitch('d02'))
Garage.sensor_group['d02'].define_monitor('BigDoor', monitor.DoorOpenMonitor('BigDoor'))

Garage.define_sensor('d10', sensor.MotionSensor('d10'))
Garage.sensor_group['d10'].define_monitor('Motion', monitor.MotionMonitor('Motion'))


Rooms = {'Basement':Basement, 'Bedroom':Bedroom, 'Garage':Garage}
CurrentRoom = Rooms['Basement']





while True:

    startTime = int(time.time())
    with radio.XBeeOnUSB as xbee:
        message = xbee.read_frame()
        #print("  Sender Serial: " + message['serial_number'])
        if message['serial_number'] == basementRadioSerialNumber:
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

        for pin in CurrentRoom.digital_pin_enabled:
            CurrentRoom.digital_pin_enabled[pin] = message['digital_channel_mask'][pin]
            CurrentRoom.digital_pin_value[pin] = message['digitial_data'][pin]
            if pin in CurrentRoom.sensor_group:
                CurrentRoom.sensor_group[pin].set_digital_value(message['digital_data'][pin])
        
        for pin in CurrentRoom.analog_pin_enabled:
            CurrentRoom.analog_pin_enabled[pin] = message['analog_channel_mask'][pin]
            CurrentRoom.analog_pin_raw[pin] = message['analog_data'][pin]
            CurrentRoom.analog_pin_mV = message['analog_mV'][pin]
            if pin in CurrentRoom.sensor_group:
                CurrentRoom.sensor_group[pin].set_analog_value(message['analog_mV'][pin])


        
        
        CurrentRoom.VCC = message['analog_mV']['vcc']
        CurrentRoom.last_update_time = int(time.time())

        #print "  VCC (mV): " + str(int(aVCCmV))

          
        print("  Unknown Frame Type: " + HexDump(frameTypeOrd))



    for CurrentRoom in Rooms:
        for CurrentSensor in Rooms[CurrentRoom].sensor_group:

            if Rooms[CurrentRoom].sensor_group[CurrentSensor].sensor_kind == 'Temperature':
                print("%s %s %s %.0f degF" % (Rooms[CurrentRoom].room_name, Rooms[CurrentRoom].sensor_group[CurrentSensor].sensor_name, Rooms[CurrentRoom].sensor_group[CurrentSensor].sensor_kind, Rooms[CurrentRoom].sensor_group[CurrentSensor].temp_reading('degF')))

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
                    for CurrentNotify in People[CurrentPerson].notification_subscriptions:
                        mailServer.sendMessage(People[CurrentPerson].NotificationSubscriptions[CurrentNotify], subject, body)
