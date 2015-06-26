import csv
import mandrill
import re
import time
	

API_KEY = 'IUbgWKOy5DcLF_tFLqM76A'				# Mandrill API key
DELAY = 120										# delay between emails in seconds
TEMPLATES = ['leadgen1', 'leadgen2', 'leadgen3', 'leadgen4', 'leadgen5', 'leadgen6']		# Mandrill template names
EMAIL_SUBJECT = "Interested Stanford Grad Students re: "									# Email subject


# Sends an email to the specified email address with the specified subject
# using the specified Mandrill template.
def send_email(template_name, email_to, subject):
    mandrill_client = mandrill.Mandrill(API_KEY)
    
    message = {
    	'subject': subject,
        'to': [],
    }

    for em in email_to:
        message['to'].append({'email': em})
        print(message)
 
    mandrill_client.messages.send_template(template_name, [], message)


# Given a filename of a csv file containing data scrapped from Craigslist,
# returns a list of all the email addresses in the csv file.  Email
# addresses that belong to property managers are excluded.
def readFile(filename):
	with open(filename, 'rU') as f:
		reader = csv.reader(f)

		emails = []
		linecounter = 0
		for line in reader:
			if linecounter == 0:
				linecounter += 1
			else:
				linecounter += 1
				exp = re.compile("(?i)Management|Realty|Apartment|Broker|Agent|Real Estate")
				manager = exp.search(line[0])
				if manager is None:
					email = line[4]
					subject = line[1]
					emails.append((email, subject))
		
	return emails
		

# Sends lead generation email to all the email addresses in the file.  DELAY
# is the number of seconds between each email send.  The template cycles
# between the templates in TEMPLATES.
def send_emails(filename):
	emails = readFile(filename)
	count = 0
	for email in emails:
		send_email(TEMPLATES[count % len(TEMPLATES)], [email[0]], EMAIL_SUBJECT + email[1])
		time.sleep(DELAY)
		count += 1

send_emails('test.csv')


