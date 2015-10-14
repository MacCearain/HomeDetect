class Address:
      def __init__(self,addressLine1, addressLine2, addressLine3, city, state, zipcode):
          self.lines = [addressLine1, addressLine2, addressLine3]
          self.city = city
          self.state = state
          self.zipcode = zipcode

      def __str__(self):
          return "%s\n%s\n%s\n%s, %s %s" % (self.lines[0], self.lines[1], self.lines[2], self.city, self.state, self.zipcode)
  


class Person:
      def __init__(self, firstName, lastName, middleName,  cellPhone, homeEmailAddress, TXTAddress, wantsEmail, wantsTxtMessage):
           self.Name = {'First':firstName, 'Middle':middleName, 'Last':lastName}
           self.Phones = {'Home': 'Unknown', 'Cell': cellPhone, 'Work': 'Unknown'}
           self.EmailAddresses = {'Home': homeEmailAddress, 'Work': 'Unknown'}
           self.TextAddresses = { 'Cell': TXTAddress, 'Home':'Unknown'}
           self.NotificationSubscriptions = {} 
           self.Addresses = {'Home': Address('Unknown', 'Unknown', 'Unknown', 'Unknown City', 'Unknown State', '99999-9999')}
           
           if wantsTxtMessage == 'Yes':
               self.NotificationSubscriptions['Text'] = self.TextAddresses['Cell']

           if wantsEmail == 'Yes':
               self.NotificationSubscriptions['Email'] = self.EmailAddresses['Home']
           

      def FullName(self):
           return "%s %s" % (self.FirstName, self.LastName)

       

