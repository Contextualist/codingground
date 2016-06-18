import urllib2
from quip4aha import week, QuipClient4AHA, InvalidOperation

class NewDoc(object):

    def __init__(self):
        NextWednesday = week.RecentWeekDay('next Wednesday')
        self.NextWednesdayN = NextWednesday.strftime("%m%d")
        self.NextWednesdayS = NextWednesday.strftime("%B %-d")
        self.ctx = ""
        self.client = QuipClient4AHA()

    def do(self):
        template = urllib2.urlopen("http://pastebin.com/raw/3cLgvDXe").read()
        # In the template, &#8203; (or &#x200b;) stands for a place-holder for a blank <p>.
        if template == "cancel":
            raise InvalidOperation("The template indicates a cancelation for this week!")
        self.ctx = template.format(NextWednesdayS=self.NextWednesdayS)
        
        try:
            self.client.get_latest_script_ID()
        except InvalidOperation as e:
            if e.code == 409:
                raise e # redundancy error
            #else: pass # script not found
        else:
            raise InvalidOperation("Redundancy Warning: The script has already been created.")
        
        self.client.new_document(content=self.ctx, format="html", title=self.NextWednesdayN, member_ids=[self.client.AHABC_ID])
        return "Done!"

if __name__=="__main__":
    NewDocAction = NewDoc()
    NewDocAction.do()
