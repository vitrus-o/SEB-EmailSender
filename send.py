import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import time
import argparse
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading

load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
ALTERNATIVE_EMAIL_FORM_LINK = os.getenv('ALTERNATIVE_EMAIL_FORM_LINK', '')
PRECINCT_LOCATION = os.getenv('PRECINCT_LOCATION', 'TBA')
BALLOT_LINK = os.getenv('BALLOT_LINK', '')

BLAST_TEMPLATE_PATH = 'email_blast.html'
BALLOT_LINKS_TEMPLATE_PATH = 'email_ballot_links.html'
SUBJECT_BLAST = 'USSC Special Election & Plebiscite - December 9, 2025'
SUBJECT_BALLOT_LINKS = 'VOTE NOW - USSC Special Election & Plebiscite'

DEFAULT_DELAY_BETWEEN_EMAILS = 3  
MAX_EMAILS_PER_BATCH = 50 

cancel_scheduled_send = False


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

def send_blast_email(recipient_email, student_name, student_id, max_retries=3):
    """
    Sends a customized HTML blast notification email.

    :param recipient_email: The student's whitelisted email address.
    :param student_name: The name of the student.
    :param student_id: The student's ID number.
    """

    html_template = read_file_content(BLAST_TEMPLATE_PATH)
    if not html_template:
        return False
    
    html_content = html_template
    
    replacements = {
        '[STUDENT NAME]': student_name,
        '[STUDENT ID NO.]': student_id,
        '[WHITELISTED EMAIL]': recipient_email,
        '[ALTERNATIVE EMAIL FORM LINK]': ALTERNATIVE_EMAIL_FORM_LINK,
        '[PRECINCT LOCATION]': PRECINCT_LOCATION
    }

    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, value)

    msg = MIMEMultipart('related')
    msg['Subject'] = SUBJECT_BLAST
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Reply-To'] = 'fcbaybayseb@vsu.edu.ph'
    msg['X-Priority'] = '3'
    msg['X-Mailer'] = 'VSU Election System'
    msg['Organization'] = 'Visayas State University - Faculty of Computing'
    msg['List-Unsubscribe'] = '<mailto:fcbaybayseb@vsu.edu.ph?subject=Unsubscribe>'

    msg.attach(MIMEText(html_content, 'html'))

    for attempt in range(max_retries):
        try:
            print(f"Attempting to send ballot email to {recipient_email} (Attempt {attempt + 1}/{max_retries})...")
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

            print(f"Success: Ballot email sent to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ Error: Authentication failed. Please check your SENDER_EMAIL and SENDER_PASSWORD.")
            break 

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt) 
            else:
                print(f"Failed to send email to {recipient_email} after {max_retries} attempts.")
                break
    
    return False


def send_ballot_links_email(recipient_email, student_name, student_id, max_retries=3):
    """
    Sends a customized HTML email with ballot link.

    :param recipient_email: The student's whitelisted email address.
    :param student_name: The name of the student.
    :param student_id: The student's ID number.
    """

    html_template = read_file_content(BALLOT_LINKS_TEMPLATE_PATH)
    if not html_template:
        return False
    
    html_content = html_template
    
    replacements = {
        '[STUDENT NAME]': student_name,
        '[STUDENT ID NO.]': student_id,
        '[WHITELISTED EMAIL]': recipient_email,
        '[SPECIAL ELECTION LINK]': BALLOT_LINK,
        '[PRECINCT LOCATION]': PRECINCT_LOCATION
    }

    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, value)

    msg = MIMEMultipart('related')
    msg['Subject'] = SUBJECT_BALLOT_LINKS
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Reply-To'] = 'fcbaybayseb@vsu.edu.ph'
    msg['X-Priority'] = '1'
    msg['X-Mailer'] = 'VSU Election System'
    msg['Organization'] = 'Visayas State University - Faculty of Computing'
    msg['List-Unsubscribe'] = '<mailto:fcbaybayseb@vsu.edu.ph?subject=Unsubscribe>'

    msg.attach(MIMEText(html_content, 'html'))

    for attempt in range(max_retries):
        try:
            print(f"Attempting to send ballot links email to {recipient_email} (Attempt {attempt + 1}/{max_retries})...")
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

            print(f"Success: Ballot links email sent to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ Error: Authentication failed. Please check your SENDER_EMAIL and SENDER_PASSWORD.")
            break 

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt) 
            else:
                print(f"Failed to send email to {recipient_email} after {max_retries} attempts.")
                break
    
    return False


def countdown_timer(delay_seconds):
    """
    Displays a countdown timer and checks for cancellation.
    Returns True if cancelled, False if timer completed.
    """
    global cancel_scheduled_send
    
    print(f"\nEmail will be sent in {delay_seconds} seconds...")
    print("Press Ctrl+C to cancel the scheduled send.\n")
    
    try:
        for remaining in range(delay_seconds, 0, -1):
            if cancel_scheduled_send:
                return True
            
            mins, secs = divmod(remaining, 60)
            timer = f'{mins:02d}:{secs:02d}'
            print(f'\rTime remaining: {timer}', end='', flush=True)
            time.sleep(1)
        
        print('\n')
        return False
    
    except KeyboardInterrupt:
        print("\n\n❌ Send cancelled by user!")
        return True


def process_csv_batch(csv_file, email_type, delay=0, email_delay=DEFAULT_DELAY_BETWEEN_EMAILS):
    """
    Process batch emails from CSV file.
    
    CSV format for all email types:
    email,name,student_id
    
    :param email_delay: Delay in seconds between each email (default: 3 seconds)
    """
    global cancel_scheduled_send
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file not found at {csv_file}")
        return
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"\nBatch Email Preview:")
    print(f"Type: {email_type.upper()}")
    print(f"Total recipients: {len(rows)}")
    print(f"Delay between emails: {email_delay} seconds")
    
    if len(rows) > MAX_EMAILS_PER_BATCH:
        print(f"\n⚠️ WARNING: You are sending to {len(rows)} recipients.")
        print(f"Recommended batch size is {MAX_EMAILS_PER_BATCH} emails to avoid spam filters.")
        print(f"Consider splitting your CSV into smaller batches.\n")
    
    for i, row in enumerate(rows, 1):
        print(f"  {i}. {row['name']} ({row['student_id']}) - {row['email']}")
    
    confirm = input(f"\nDo you want to proceed with sending {len(rows)} emails? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Batch send cancelled.")
        return
    
    if delay > 0:
        if countdown_timer(delay):
            print("❌ Batch send cancelled during countdown.")
            return
    
    success_count = 0
    fail_count = 0
    
    for idx, row in enumerate(rows, 1):
        if cancel_scheduled_send:
            print("\n❌ Batch send cancelled!")
            break
        
        print(f"\n[{idx}/{len(rows)}] Processing: {row['name']} <{row['email']}>")
        
        try:
            if email_type == 'blast':
                result = send_blast_email(
                    recipient_email=row['email'],
                    student_name=row['name'],
                    student_id=row['student_id']
                )
            elif email_type == 'ballot_links':
                result = send_ballot_links_email(
                    recipient_email=row['email'],
                    student_name=row['name'],
                    student_id=row['student_id']
                )
            
            if result:
                success_count += 1
            else:
                fail_count += 1
            
            if idx < len(rows):
                print(f"Waiting {email_delay} seconds before next email...")
                time.sleep(email_delay)
            
        except KeyError as e:
            print(f"❌ Error: Missing required column in CSV: {e}")
            fail_count += 1
        except Exception as e:
            print(f"❌ Error processing row: {e}")
            fail_count += 1
    
    print(f"\n--- Batch Processing Complete ---")
    print(f"✅ Successfully sent: {success_count}")
    print(f"❌ Failed: {fail_count}")


def send_single_with_delay(email_func, delay, **kwargs):
    """
    Sends a single email with a delay and cancellation option.
    """
    global cancel_scheduled_send
    
    print(f"\nEmail Preview:")
    print(f"To: {kwargs.get('recipient_email')}")
    print(f"Name: {kwargs.get('student_name')}")
    print(f"Student ID: {kwargs.get('student_id')}")
    
    confirm = input(f"\nProceed with sending this email? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Send cancelled.")
        return False
    
    if delay > 0:
        if countdown_timer(delay):
            print("❌ Send cancelled during countdown.")
            return False
    
    return email_func(**kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='USSC Email Sender - Special Election and Plebiscite')
    
    parser.add_argument('--mode', choices=['single', 'batch'], default='single',
                        help='Send mode: single email or batch from CSV')
    
    parser.add_argument('--type', choices=['blast', 'ballot_links'], default='blast',
                        help='Type of email to send')
    
    parser.add_argument('--email', help='Recipient email address')
    parser.add_argument('--name', help='Student name')
    parser.add_argument('--id', help='Student ID')
    
    parser.add_argument('--csv', help='Path to CSV file for batch processing')
    
    parser.add_argument('--delay', type=int, default=30,
                        help='Delay in seconds before sending (default: 30)')
    
    parser.add_argument('--email-delay', type=int, default=DEFAULT_DELAY_BETWEEN_EMAILS,
                        help=f'Delay in seconds between each email in batch mode (default: {DEFAULT_DELAY_BETWEEN_EMAILS})')
    
    args = parser.parse_args()
    
    print("--- USSC Email Sender - Special Election and Plebiscite ---\n")
    
    try:
        if args.mode == 'single':
            if not all([args.email, args.name, args.id]):
                print("❌ Error: --email, --name, and --id are required for single mode")
                parser.print_help()
            elif args.type == 'blast':
                send_single_with_delay(
                    send_blast_email,
                    delay=args.delay,
                    recipient_email=args.email,
                    student_name=args.name,
                    student_id=args.id
                )
            elif args.type == 'ballot_links':
                send_single_with_delay(
                    send_ballot_links_email,
                    delay=args.delay,
                    recipient_email=args.email,
                    student_name=args.name,
                    student_id=args.id
                )
        elif args.mode == 'batch':
            if not args.csv:
                print("❌ Error: --csv is required for batch mode")
                parser.print_help()
            else:
                process_csv_batch(
                    csv_file=args.csv,
                    email_type=args.type,
                    delay=args.delay,
                    email_delay=args.email_delay
                )
    
    except KeyboardInterrupt:
        print("\n\n❌ Program interrupted by user.")
        cancel_scheduled_send = True