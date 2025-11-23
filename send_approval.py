import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import time
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

HTML_TEMPLATE_PATH = 'email_approval_template.html'
SUBJECT_TEMPLATE = 'Online Voting Application Approved - FC Plebiscite'


def read_file_content(filepath):
    """Reads the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None


def send_approval_email(recipient_email, student_name, student_id, election_date, start_time, end_time, max_retries=3):
    """
    Sends a customized HTML approval email.

    :param recipient_email: The student's approved email address.
    :param student_name: The name of the student.
    :param student_id: The student's ID number.
    :param election_date: The date of the election.
    :param start_time: Voting start time.
    :param end_time: Voting end time.
    """

    html_template = read_file_content(HTML_TEMPLATE_PATH)
    if not html_template:
        return
    
    html_content = html_template
    
    replacements = {
        '[STUDENT NAME]': student_name,
        '[STUDENT ID NO.]': student_id,
        '[WHITELISTED EMAIL]': recipient_email,
        '[ELECTION DATE]': election_date,
        '[START TIME]': start_time,
        '[END TIME]': end_time
    }

    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, value)


    msg = MIMEMultipart('related')
    msg['Subject'] = SUBJECT_TEMPLATE
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    msg.attach(MIMEText(html_content, 'html'))

    for attempt in range(max_retries):
        try:
            print(f"Attempting to send email to {recipient_email} (Attempt {attempt + 1}/{max_retries})...")
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls() # Secure the connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

            print(f"✅ Success: Approval email sent to {recipient_email}")
            return 

        except smtplib.SMTPAuthenticationError:
            print("❌ Error: Authentication failed. Please check your SENDER_EMAIL and SENDER_PASSWORD (ensure you are using an App Password for Gmail).")
            break 

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt) 
            else:
                print(f"Failed to send email to {recipient_email} after {max_retries} attempts.")
                break 

if __name__ == '__main__':
    
    print("--- FOC-SEB Email Sender Initialization ---")
    
    example_student = {
        'email': '23-1-01032@vsu.edu.ph',  
        'name': 'VEE EMMANUEL LEYES AÑORA',
        'id': '23-1-01032',
        'date': 'Wednesday, November 26, 2025',
        'start': '8:00 AM',
        'end': '5:00 PM'
    }
    
    send_approval_email(
        recipient_email=example_student['email'],
        student_name=example_student['name'],
        student_id=example_student['id'],
        election_date=example_student['date'],
        start_time=example_student['start'],
        end_time=example_student['end'],
    )