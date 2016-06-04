from quip4aha import week, QuipClient4AHA, InvalidOperation

class NewDoc(object):

    def __init__(self):
        NextWednesday = week.RecentWeekDay('next Wednesday')
        self.NextWednesdayN = NextWednesday.strftime("%m%d")
        self.NextWednesdayS = NextWednesday.strftime("%B %d")
        if self.NextWednesdayS[-2] == "0":
            self.NextWednesdayS = self.NextWednesdayS[:-2] + self.NextWednesdayS[-1];
        self.ctx = """<p class='line'>Good Morning AHA!<br/>
        It is Wednesday, %s. The weather for today is __. There is a(n) __%% chance of rain. The high temperature today will be __ degrees Celsius, which is __ degrees Fahrenheit.</p>
        <p class='line'>&#8203;</p>
        <p class='line'><b>Now for this week in history:</b></p>
        <p class='line'>&#8203;</p>
        <p class='line'>&#8203;</p>
        <p class='line'><b>In World News:</b></p>
        <p class='line'>&#8203;</p>
        <p class='line'>&#8203;</p>
        <p class='line'><b>Now for the fun facts:</b></p>
        <p class='line'>&#8203;</p>
        <p class='line'>&#8203;</p>
        <p class='line'><b>In AHA News:</b></p>
        <p class='line'>&#8203;</p>
        <p class='line'>&#8203;</p>
        <p class='line'>We will close with this/these verse(s) from</p>
        <p class='line'>&#8203;</p>
        <p class='line'>That is all for today's AHA broadcasting. Thank you for listening, and as always stay classy AHA!</p>
        """ % (self.NextWednesdayS) # &#8203; (or &#x200b;) stands for a place-holder for a blank <p>
        self.client = QuipClient4AHA()

    def do(self):
        try:
            self.client.get_latest_script_ID()
        except InvalidOperation, e:
            print repr(e)
        else:
            raise InvalidOperation("Redundancy Warning: The script has already been created!")
        
        print "Done!"
        return "Done!"

if __name__=="__main__":
    NewDocAction = NewDoc()
    NewDocAction.do()

