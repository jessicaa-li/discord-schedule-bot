"""
Object template for schedules. Currently
pretty basic and lacking in details (especially
in how participants will be stored).
"""
import datetime

class Meeting:
    def __init__(self, name, time = datetime.time(0,0,0), date = datetime.date(2000, 1, 1), participants = [], desc = "", autoRemind = False):
        self.name = name
        self.time = time
        self.date = date
        self.participants = participants
        self.desc = desc
        self.autoRemind = autoRemind
    
    def getName(self):
        return self.name

    def setTime(self, time):
        self.time = time
    
    def getTime(self):
        return self.time
    
    def setDate(self, date):
        self.date = date
    
    def getDate(self):
        return self.date

    def setDesc(self, desc):
        self.desc = desc
    
    def getDesc(self):
        return self.desc

    def setAutoRemind(self, autoRemind):
        self.autoRemind = autoRemind

    def getAutoRemind(self):
        return self.autoRemind

    def addParticipant(self, user):
        self.participants.append(user)
    
    def removeParticipant(self, user):
        self.participants.remove(user)
    
    def getParticipants(self):
        return self.participants