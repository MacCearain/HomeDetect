'''
  Light Weight Mail Sender
'''
import smtplib
import configparser



class McMail:

    def __init__(self, userName=None, passWord=None, serverName=None, portNumber=None):

        config = configparser.ConfigParser()
        config.read('McMail.cfg')

        if userName is None:
            # Let's attempt to get the userName from the Config File
            self.userName = config['Email']['Username']
        else:
            self.userName = userName

        if passWord is None:
            self.passWord = config['Email']['Password']
        else:
            self.passWord = passWord

        if serverName is None:
            self.serverName = config['Email']['Server']
        else:
            self.serverName = serverName

        if portNumber is None:
            self.portNumber = config['Email']['ServerPort']
        else:
            self.portNumber = portNumber

        self.status = 'Closed'



    def open(self):

        #print('Entering the open function.')


        if self.status == 'Closed':
            self.smtpServer = smtplib.SMTP(self.serverName, self.portNumber)
            self.smtpServer.ehlo()
            self.smtpServer.starttls()
            self.smtpServer.ehlo()

            self.smtpServer.login(self.userName, self.passWord)

            self.status = 'Open'
        else:
            print('The connection to a mail server is already open.')



    def close(self):
        if self.status == 'Open':
            self.smtpServer.quit()
            self.status = 'Closed'
        else:
            print('The connection is already closed.')

    def __enter__(self):
        #print('Entering the __enter__ Function.')
        self.open()
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        self.close()

    def __str__(self):
        return "Mail Handle on Server: {} Port: {}, under user: {} is currently: {}".format(self.serverName, self.portNumber, self.userName, self.status)

    def __repr__(self):
        return "McMail.McMail('{}','{}','{}','{}')".format(self.userName, 'XXXXXXXXXX', self.serverName, self.portNumber)

    def sendMessage(self, toAddr, subjectLine, messageBody):
        header = 'To: ' + toAddr + '\nFrom: ' + self.userName + '\nSubject: ' + subjectLine + '\n\n'
        self.smtpServer.sendmail(self.userName, toAddr, header + messageBody)


if __name__ == '__main__':
    # if we run the McMail.py file directly....

    with McMail() as myMail:
        myMail.sendMessage('McCarronClan@gmail.com', 'A Test Message', 'This is the body of the email.')
