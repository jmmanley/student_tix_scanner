"""
Quick and dirty tool for scraping NYC classical music student tickets websites
and sending notifications when a new show is available!

Currently supported:
- The Metropolitan Opera (https://www.metopera.org/season/tickets/student-tickets/)
- Carnegie Hall (https://www.carnegiehall.org/Events/Discount-Programs/Student-Tickets)
- New York Philharmonic (https://nyphil.org/rush - also check out Free Fridays that opens on Mondays at noon: https://nyphil.org/concerts-tickets/explore/discounts-and-group-sales/free-fridays)

Jason Manley, jmanley AT rockefeller DOT edu
"""


from bs4 import BeautifulSoup as bs
import urllib.request
from urllib.request import build_opener, HTTPCookieProcessor
import smtplib
from email.message import EmailMessage
import csv
import sys
import time


### UTILITY FUNCTIONS ###

def check_new_and_notify(shows, file, To):
    # read old list
    old_shows = []
    try:
        with open(file, mode='r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')

            for row in reader:
                old_shows.append(row)
    except:
        old_shows = []

    with open(file, mode='a') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for show in shows:
            if show not in old_shows:
                send_notification(show, From=file[:-4], To=To)
                writer.writerow(show)
                # UPDATE: note this will now keep a ROLLING log of all shows since the start of scraping
                # sometimes shows are removed & re-added (particularly by NY Phil) which had resulted in redundant notifications

def send_notification(text, To, From='Me'):
    import smtplib
    from email.message import EmailMessage # easy enough to send a text: e.g. 1234567890@txt.att.net

    message = EmailMessage()
    message.set_charset('utf-8')
    message.set_content(' '.join(text))

    server = smtplib.SMTP('localhost') # You can modify this to send from an SMTP server of your choice

    text = ' '.join(text)

    from urllib.parse import unquote

    server.send_message(message, From, To)
    server.quit()


### SITE-SPECIFIC FUNCTIONS ###

def parse_metopera(To):
    
    opener = build_opener(HTTPCookieProcessor())
    response = opener.open('https://www.metopera.org/season/tickets/student-tickets/')
    html = response.read()
    soup = bs(html, "html.parser")
    divs = soup.findAll("li", {"class": "calendar-list-day"})
    
    def parse_metopera_listing(tag):
        # apologies for this ugly HTML hack to get the data out
        date = tag.contents[1].contents[0].replace(',','')
        time = tag.contents[3].contents[1].contents[1].contents[0].replace(',','')
        opera = tag.contents[3].contents[3].contents[1].contents[1].contents[0].replace(',','')

        return [date, time, opera]
    
    shows = []
    
    for tag in divs:
        shows.append(parse_metopera_listing(tag))
    
    check_new_and_notify(shows, 'MetOpera.csv', To)

    
def parse_carnegie(To):
    
    opener = build_opener(HTTPCookieProcessor())
    response = opener.open('https://www.carnegiehall.org/Events/Discount-Programs/Student-Tickets')
    html = response.read()
    soup = bs(html, "html.parser")
    divs = soup.findAll("div", {"class": "ch-events-list-item"})

    def parse_carnegie_listing(tag):
        # apologies again
        date = tag.contents[1].contents[1].contents[0][:3] + ' ' + divs[0].contents[1].contents[3].contents[0]
        show = tag.contents[3].contents[1].contents[3].contents[3].contents[1].contents[1].contents[1].contents[0]
        subtitle = tag.contents[3].contents[1].contents[3].contents[3].contents[1].contents[3].contents[0].replace('\r','').replace('\n','').replace('  ','')
    
        if len(subtitle)>1:
            show += ' (' + subtitle + ')'
        
        return [date.replace(',',''), show.replace(',','')]
    
    shows = []
    
    for tag in divs:
        shows.append(parse_carnegie_listing(tag))
    
    check_new_and_notify(shows, 'Carnegie.csv', To)


def parse_nyphil(To):
    
    opener = build_opener(HTTPCookieProcessor())
    response = opener.open('https://nyphil.org/rush')
    html = response.read()
    soup = bs(html, "html.parser")
    divs1 = soup.findAll("div", {"class": "date-cont"})
    divs2 = soup.findAll("div", {"class": "cal-date"})
    
    def parse_nyphil_listing(tag1, tag2):
        # apologies again
        datenum = tag1.contents[1].contents[1].contents[0]
        month   = tag1.contents[1].contents[3].contents[0].replace('\r','').replace('\n','').replace(' ','').split(',')[0]
        date    = month[:3] + ' ' + datenum

        show = str(tag2.contents[1].contents[3].contents[5].contents[1].contents[0])
        
        return [date, show]
    
    shows = []
    
    for i in range(len(divs1)):
        shows.append(parse_nyphil_listing(divs1[i], divs2[i]))
        
    check_new_and_notify(shows, 'NyPhil.csv', To)


### COMMAND LINE SCRIPT ###

if __name__ == "__main__":
    args = sys.argv[1:]
    To = args[0]
    
    while True:

        if True:
            if '-met' in args:
                parse_metopera(To)

            if '-carnegie' in args:
                parse_carnegie(To)

            if '-nyphil' in args:
                parse_nyphil(To)
        #except:
        #    print('error')
        
        time.sleep(300) # sorry for hard coding ;)
    
