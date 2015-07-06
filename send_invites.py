# File: send_invites.py
# Author: Thomas Leung
# Sends invite emails to all owners who have requested an invitation, who
# have not received an invite, and whose rental property is either a single
# family home, townhouse, or condominium.


import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import mandrill
import time
import datetime
from datetime import date


API_KEY = 'IUbgWKOy5DcLF_tFLqM76A'															# Mandrill API key
JSON_KEY = json.load(open('/Users/thomasleung/Downloads/Landed-f6a6a26fd105.json'))			# Google Sheets JSON key
INVITE_TEMPLATE = 'owner-invite'															# Invite email template
EMAIL = 2																					# Email column in table
INVITE_SENT = 4																				# Invite_Sent column in table
INVITE_DATE = 5																				# Invite_Date column in table
SIGNED_UP = 9																				# Signed_Up column in table


# Returns a list of email addresses of owners who have requested an invitation,
# who have not received an invite, and whose rental property is either a single
# family home, townhouse, or condominium.
def get_invite_emails():
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = SignedJwtAssertionCredentials(JSON_KEY['client_email'], JSON_KEY['private_key'], scope)
	gc = gspread.authorize(credentials)							
	wks = gc.open("Landed Owner Table").sheet1					

	invites = []
	row_count = wks.row_count

	for i in range(1, row_count):
		row = i + 1
		if wks.cell(row, INVITE_SENT).value == 'FALSE':
			invite = wks.cell(row, EMAIL).value
			invites.append(invite)
			wks.update_cell(row, INVITE_SENT, 'TRUE')
			d = date.strftime(date.today(), "%B %d %Y")
			wks.update_cell(row, INVITE_DATE, d)
			wks.update_cell(row, SIGNED_UP, 'FALSE')

	return invites


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


# Sends reminder emails to all owners who have requested an invitation, who
# have not received an invite, and whose rental property is either a single
# family home, townhouse, or condominium.
def main():
	invites = get_invite_emails()
	print('invites sent to the following emails: ')
	for email in invites:
		print(email)
		send_email(INVITE_TEMPLATE, [email])
		

if __name__ == '__main__':	
	main()

