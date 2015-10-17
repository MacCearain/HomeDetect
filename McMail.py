import smtplib


#-----------------------
# Email Constants
EMAILUSERNAME = 'address@gmail.com'
EMAILPASSWORD = 'xxxxxxxx'
EMAILSERVER = 'smtp.gmail.com'
EMAILSERVERPORT = 587



class McMail:
   
    def __init__ (self, userName=EMAILUSERNAME, passWord=EMAILPASSWORD, serverName=EMAILSERVER, portNumber=EMAILSERVERPORT):
       self.userName = userName
       self.passWord = passWord
       self.serverName = serverName
       self.portNumber = portNumber

       self.smtpServer = smtplib.SMTP(serverName,portNumber)

       self.smtpServer.ehlo()
       self.smtpServer.starttls()
       self.smtpServer.ehlo()

       self.smtpServer.login(self.userName, self.passWord)

   
    def quit(self):
       self.smtpServer.quit()

    def sendMessage(self, toAddr, subjectLine, messageBody):
       header = 'To: ' + toAddr + '\nFrom: ' + self.userName + '\nSubject: ' + subjectLine + '\n\n' 
       self.smtpServer.sendmail(self.userName, toAddr, header + messageBody)



       
