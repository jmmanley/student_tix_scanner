# :musical_score: NY Classical Student Tickets Notifier 

I found myself periodically checking the websites for student tickets at the Met Opera, Carnegie Hall, and NY Phil -- and knew there had be a better way to find out about these awesome deals!

An hour later, I finished this quick and dirty scraper for the student tickets of the three aforementioned NYC classical music institutions.

No guarantee this will work at all for you! I just leave this script running in an infinite loop on a server so I'm always up to date (not the most elegant solution, sorry in advance).

## Usage
```
python student_tix_scanner.py EMAIL@ADDRESS.ORG -met -nyphil -carnegie
```

Built on Python 3.7 and Beautiful Soup4.
