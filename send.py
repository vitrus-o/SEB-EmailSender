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
REAPPLICATION_LINK = os.getenv('REAPPLICATION_LINK')

HTML_TEMPLATE_PATH = 'email_approval_template.html'
REAPPLY_TEMPLATE_PATH = 'email_reapply_template.html'
SUBJECT_TEMPLATE = 'Online Voting Application Approved - FC Plebiscite'
SUBJECT_REAPPLY = 'Online Voting Application - Action Required - FC Plebiscite'

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
        return False
    
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
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

            print(f"Success: Approval email sent to {recipient_email}")
            return True

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
    
    return False


def send_reapply_email(recipient_email, student_name, student_id, reapply_reason, election_date, start_time, end_time, reapplication_link, max_retries=3):
    """
    Sends a customized HTML reapply email with reapplication option.

    :param recipient_email: The student's email address.
    :param student_name: The name of the student.
    :param student_id: The student's ID number.
    :param reapply_reason: The reason for reapply.
    :param election_date: The date of the election.
    :param start_time: Voting start time.
    :param end_time: Voting end time.
    :param reapplication_link: Link to reapply.
    """

    html_template = read_file_content(REAPPLY_TEMPLATE_PATH)
    if not html_template:
        return False
    
    html_content = html_template
    
    replacements = {
        '[STUDENT NAME]': student_name,
        '[STUDENT ID NO.]': student_id,
        '[REAPPLY REASON]': reapply_reason,
        '[ELECTION DATE]': election_date,
        '[START TIME]': start_time,
        '[END TIME]': end_time,
        '[REAPPLICATION LINK]': reapplication_link
    }

    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, value)

    msg = MIMEMultipart('related')
    msg['Subject'] = SUBJECT_REAPPLY
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    msg.attach(MIMEText(html_content, 'html'))

    for attempt in range(max_retries):
        try:
            print(f"Attempting to send reapply email to {recipient_email} (Attempt {attempt + 1}/{max_retries})...")
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

            print(f"Success: reapply email sent to {recipient_email}")
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


def process_csv_batch(csv_file, email_type, election_date, start_time, end_time, reapplication_link=None, delay=0):
    """
    Process batch emails from CSV file.
    
    CSV format for approval:
    email,name,student_id
    
    CSV format for reapply:
    email,name,student_id,reapply_reason
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
    
    for row in rows:
        if cancel_scheduled_send:
            print("\n❌ Batch send cancelled!")
            break
        
        try:
            if email_type == 'approval':
                result = send_approval_email(
                    recipient_email=row['email'],
                    student_name=row['name'],
                    student_id=row['student_id'],
                    election_date=election_date,
                    start_time=start_time,
                    end_time=end_time
                )
            elif email_type == 'reapply':
                if not reapplication_link:
                    print("❌ Error: Reapplication link is required for reapply emails.")
                    break
                
                result = send_reapply_email(
                    recipient_email=row['email'],
                    student_name=row['name'],
                    student_id=row['student_id'],
                    reapply_reason=row.get('reapply_reason', 'Incomplete or invalid application'),
                    election_date=election_date,
                    start_time=start_time,
                    end_time=end_time,
                    reapplication_link=reapplication_link
                )
            
            if result:
                success_count += 1
            else:
                fail_count += 1
            
            time.sleep(1)
            
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
    parser = argparse.ArgumentParser(description='FOC-SEB Email Sender')
    
    parser.add_argument('--mode', choices=['single', 'batch'], default='single',
                        help='Send mode: single email or batch from CSV')
    
    parser.add_argument('--type', choices=['approval', 'reapply'], default='approval',
                        help='Type of email to send')
    
    parser.add_argument('--email', help='Recipient email address')
    parser.add_argument('--name', help='Student name')
    parser.add_argument('--id', help='Student ID')
    
    parser.add_argument('--csv', help='Path to CSV file for batch processing')
    
    parser.add_argument('--date', default='Wednesday, November 26, 2025',
                        help='Election date')
    parser.add_argument('--start', default='8:00 AM',
                        help='Voting start time')
    parser.add_argument('--end', default='5:00 PM',
                        help='Voting end time')
    
    parser.add_argument('--reason', help='Reapply reason (for single reapply emails)')
    parser.add_argument('--reapply-link', default=REAPPLICATION_LINK,
                        help='Reapplication link (for reapply emails)')
    
    parser.add_argument('--delay', type=int, default=30,
                        help='Delay in seconds before sending (default: 30)')
    
    args = parser.parse_args()
    
    print("--- FOC-SEB Email Sender Initialization ---\n")
    
    try:
        if args.mode == 'single':
            if not all([args.email, args.name, args.id]):
                print("❌ Error: --email, --name, and --id are required for single mode")
                parser.print_help()
            elif args.type == 'approval':
                send_single_with_delay(
                    send_approval_email,
                    delay=args.delay,
                    recipient_email=args.email,
                    student_name=args.name,
                    student_id=args.id,
                    election_date=args.date,
                    start_time=args.start,
                    end_time=args.end
                )
            elif args.type == 'reapply':
                if not args.reason:
                    print("❌ Error: --reason is required for reapply emails")
                    parser.print_help()
                else:
                    send_single_with_delay(
                        send_reapply_email,
                        delay=args.delay,
                        recipient_email=args.email,
                        student_name=args.name,
                        student_id=args.id,
                        reapply_reason=args.reason,
                        election_date=args.date,
                        start_time=args.start,
                        end_time=args.end,
                        reapplication_link=args.reapply_link
                    )
        
        elif args.mode == 'batch':
            if not args.csv:
                print("❌ Error: --csv is required for batch mode")
                parser.print_help()
            else:
                process_csv_batch(
                    csv_file=args.csv,
                    email_type=args.type,
                    election_date=args.date,
                    start_time=args.start,
                    end_time=args.end,
                    reapplication_link=args.reapply_link,
                    delay=args.delay
                )
    
    except KeyboardInterrupt:
        print("\n\n❌ Program interrupted by user.")
        cancel_scheduled_send = True