# File: send_reminders.py
# Author: Thomas Leung
# Sends reminder emails to all owners who have received an invite but have not
# completed the onboarding form within 3 days of the invite.


import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import mandrill
import time
import datetime
from datetime import date


API_KEY = 'IUbgWKOy5DcLF_tFLqM76A'			# Mandrill API key
JSON_KEY = json.load(open('/Users/thomasleung/Downloads/Landed-f6a6a26fd105.json'))		# Google Sheets JSON key
FIRST_REMINDER_TEMPLATE = 'onboarding-first-reminder'		# First reminder email template
SECOND_REMINDER_TEMPLATE = 'onboarding-second-reminder'		# Second reminder email template
FIRST_REMINDER = 3		# Number of days after invite for first reminder
SECOND_REMINDER = 7		# Number of days after invite for second reminder
EMAIL = 2				# Email column in table
INVITE_SENT = 4			# Invite_Sent column in table
INVITE_DATE = 5			# Invite_Date column in table


# Returns a list of email addresses of owners who have not completed the onboarding
# form within days of the invite.
def get_reminder_emails(days):
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = SignedJwtAssertionCredentials(JSON_KEY['client_email'], JSON_KEY['private_key'], scope)
	gc = gspread.authorize(credentials)
	wks = gc.open("Landed Owner Table").sheet1

	reminders = []
	row_count = wks.row_count

	for i in range(1, row_count):
		row = i + 1
		if wks.cell(row, INVITE_SENT).value == 'TRUE':
			invite_sent = datetime.datetime.strptime(wks.cell(row, INVITE_DATE).value, "%m/%d/%Y").date()
			delta = date.today() - invite_sent
			if delta == days:
				reminder = wks.cell(row, EMAIL).value
				reminders.append(reminder)

	return reminders


# Sends an email to the specified email address with the specified subject
# using the specified Mandrill template.
def send_email(template_name, email_to):
    mandrill_client = mandrill.Mandrill(API_KEY)
    
    message = {
        'to': [],
    }
    
    for em in email_to:
        message['to'].append({'email': em})
 
    mandrill_client.messages.send_template(template_name, [], message)


# Sends reminder emails to all owners who have received an invite but have not
# completed the onboarding form.  The reminders are sent 3 days and 7 days
# after the invite if the owner has not yet completed the onboarding form.
def main():
	first_reminder_emails = get_reminder_emails(FIRST_REMINDER)
	print('first reminders sent to the following emails:')
	for email in first_reminder_emails:
		print(email)
		send_email(FIRST_REMINDER_TEMPLATE, [email])
	
	second_reminder_emails = get_reminder_emails(SECOND_REMINDER)
	print('second reminders sent to the following emails:')
	for email in second_reminder_emails:
		print(email)
		send_email(SECOND_REMINDER_TEMPLATE, [email])


if __name__ == '__main__':	
	main()

