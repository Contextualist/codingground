'''
Include a customized Quip client and some utilities.

NOTICE:  To update the broadcast structure, you need to update
         1) KEYWORD, 2) B_WEIGHT, 3) PN_PER_B;
         To update the host list, you need to update
         1) HOST.
'''

from time import time
from datetime import datetime, timedelta, tzinfo
from quip import QuipClient

class QuipClient4AHA(QuipClient):
    """A customized Quip client using Harry's token and dedicated for AHA Broadcast."""
    AHABC_ID = "PCeAOAQx6sO"
    DESKTOP_ID = "LHEAOAhm7YS" # Harry's private desktop.
    
    KEYWORD = ("Good Morning AHA",
               "Now for this week in history",
               "In World News",
               "Now for the fun facts",
               "In AHA News")
    B_WEIGHT = (1.00, 1.30, 1.50, 1.20, 1.00)
    HOST = ["Edward", "Katherine", "Sissy", "Harry"]
    PN_PER_B = (1, 1, 2, 1, 2)
    
    def __init__(self):
        QuipClient.__init__(self, 
            access_token="Wk9EQU1BcDZFS04=|1483091850|CF037JVoITJPnAET8aHWnZwEZACvrIm7jtkRIQCaX3g=")
            # Harry's access token.
    
    def get_folder_AHABC(self):
        return self.get_folder(id=self.AHABC_ID)
    
    def get_latest_script_ID(self):
        AHABC = self.get_folder_AHABC()
        nxtwed = week.RecentWeekDay('next Wednesday')
        title = nxtwed.strftime('%m%d')
        #lstfri = [int(time.mktime(
        #    time.strptime('%s 16:10:00' % (week.RecentWeekday('last Friday')), "%Y-%m-%d %H:%M:%S")))]
        docID = []
        for td in AHABC['children']:
            if (('thread_id' in td) and (self.get_thread(td['thread_id'])['thread']['title']==title)):
                docID.append(td['thread_id'])
        if docID == []:
            raise InvalidOperation("Script not found: There's no legitimate host script for next week's broadcast.")
        if len(docID) > 1:
            raise InvalidOperation("Redundancy Error: More than one scripts for the next broadcast are found!", 409)
        return docID[0]

class Week(object):

    class CST(tzinfo):
        utcoffset = lambda self, dt: timedelta(hours=8)
        dst = lambda self, dt: timedelta(0)
    _cst_today = lambda self: datetime.fromtimestamp(time(), self.CST()).date()
    
    def DaysTo(self, TheDay, IgnoreToday=False):
        """Return the days to a specific day of last/next week.
        e.g. (assume today is May 24, Wed. IgnoreToday=False):
            DaysTo('last Friday') # -5
            DaysTo('next Wednesday') # 0
        """
        argu = TheDay.split(' ')
        rel = {'last':-1, 'next':1}[argu[0].lower()]
        weekday = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4,
                   'Friday':5, 'Saturday':6, 'Sunday':7}[argu[1]]
        today = self._cst_today().isoweekday()
        if IgnoreToday:
            return weekday - today + (rel*weekday<=rel*today) * rel * 7
        else:
            return weekday - today + (rel*weekday<rel*today) * rel * 7
    
    def RecentWeekDay(self, TheDay, IgnoreToday=False):
        '''Return the date object for a specific day of last/next week.
        e.g. (assume today is May 24, Wed. IgnoreToday=False):
            RecentWeekDay('last Friday') # <date object of 05-19>
            RecentWeekDay('next Wednesday') # <date object of 05-24>
        '''
        return self._cst_today() + timedelta(self.DaysTo(TheDay,IgnoreToday))
    
week = Week()

class InvalidOperation(Exception):
    """Exception for all actions that take place when the conditions are not fulfilled."""
    def __init__(self, message, http_code=None):
        Exception.__init__(self, message)
        self.code = http_code or 202
