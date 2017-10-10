'''
  This module defines both a simple Person and Address Class
'''
# pylint: disable=line-too-long
# pylint: disable=too-many-arguments

class Address:
    '''
      Basic Implementation of a US Address Data Structure as a Class
    '''

    def __init__(self, addressLine1, addressLine2, addressLine3, city, state, zipcode):
        '''
          Initialize an instace of the Address Class
        '''
        self.lines = [addressLine1, addressLine2, addressLine3]
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def __str__(self):
        '''
          The default string representation of an Address Object
        '''
        return "%s\n%s\n%s\n%s, %s %s" % (self.lines[0], self.lines[1], self.lines[2], self.city, self.state, self.zipcode)



class Person:
    '''
      Basic Implementation of a Person...
    '''
    def __init__(self, firstName, lastName, middleName, cellPhone, homeEmailAddress, TXTAddress, wantsEmail, wantsTxtMessage):
        '''
          Initialize an instance of the Person Class
        '''
        self.name = {'First': firstName, 'Middle': middleName, 'Last': lastName}
        self.phones = {'Home': 'Unknown', 'Cell': cellPhone, 'Work': 'Unknown'}
        self.email_addresses = {'Home': homeEmailAddress, 'Work': 'Unknown'}
        self.text_addresses = {'Cell': TXTAddress, 'Home':'Unknown'}
        self.notification_subscriptions = {}
        self.addresses = {'Home': Address('Unknown', 'Unknown', 'Unknown', 'Unknown City', 'Unknown State', '99999-9999')}

        if wantsTxtMessage == 'Yes':
            self.notification_subscriptions['Text'] = self.text_addresses['Cell']

        if wantsEmail == 'Yes':
            self.notification_subscriptions['Email'] = self.email_addresses['Home']


    def full_name(self):
        '''
          full_name returns a string containing the first and last name like: John Doe
        '''
        return "%s %s" % (self.name['First'], self.name['Last'])
