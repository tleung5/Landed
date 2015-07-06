# File: scheduler.py
# Author: Thomas Leung
# Scrapes Craigslist for emails and phone numbers, sends invites, and sends
# reminders.  The processes can be scheduled to run at a specific time
# each day.


import subprocess
import time
import datetime
from datetime import date


# Calls Scrapy to scrape Craigslist for emails and phone numbers and saves the
# results in a csv file.
scrapy_output = subprocess.call(['scrapy', 'crawl', 'craigslist', '-o', date.strftime(date.today(), "%B-%d-%Y") + '_Rentals.csv', '-t', 'csv'], cwd = "/Users/thomasleung/Desktop/scraper/")
print(scrapy_output)


# Calls the appropriate process to send invites.
send_invites = subprocess.check_output(['python', 'send_invites.py'])
print(send_invites)


# Calls the appropriate process to send reminders.
send_reminders = subprocess.check_output(['python', 'send_reminders.py'])
print(send_reminders) 