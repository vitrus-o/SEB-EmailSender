# FOC-SEB Email Sender

Automated email sender for Faculty of Computing - Student Election Board (FC-SEB) online voting applications.

## Features

- Send approval emails for online voting
- Send rejection emails with reapplication link
- Single email or batch processing from CSV
- Scheduled sending with countdown timer
- Cancellation support (Ctrl+C)
- Email preview and confirmation before sending
- Automatic retry on failure

## Prerequisites

- Python 3.7 or higher
- Gmail account with App Password enabled

## Installation

1. **Clone or download this repository**

2. **Install required packages:**
   ```bash
   pip install python-dotenv
   ```

3. **Create a `.env` file** in the same directory with your credentials:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_sender_email_here
   SENDER_PASSWORD=your_app_password_here
   REAPPLICATION_LINK=your_google_forms_link
   ```

   > **Important:** Use a Gmail App Password, not your regular password. 
   > [Learn how to create an App Password](https://support.google.com/accounts/answer/185833)

4. **Add `.env` to `.gitignore`** (if using Git):
   ```
   .env
   ```

## File Structure

```
FC-SEBEmailSender/
├── send.py              # Main script
├── email_approval_template.html  # Approval email template
├── email_rejection_template.html # Rejection email template
├── .env                          # Credentials (DO NOT COMMIT)
├── approval.csv                  # Sample approval list
├── rejection.csv                 # Sample rejection list
└── README.md                     # This file
```

## CSV File Format

### For Approval Emails (`approval.csv`)
```csv
email,name,student_id
```

**Required columns:** `email`, `name`, `student_id`

### For Rejection Emails (`rejection.csv`)
```csv
email,name,student_id,rejection_reason
```

**Required columns:** `email`, `name`, `student_id`, `rejection_reason`

## Usage

### Basic Command Structure
```bash
python send_approval.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Send mode: `single` or `batch` | `single` |
| `--type` | Email type: `approval` or `reapply` | `approval` |
| `--email` | Recipient email address (single mode) | - |
| `--name` | Student name (single mode) | - |
| `--id` | Student ID (single mode) | - |
| `--csv` | Path to CSV file (batch mode) | - |
| `--date` | Election date | `Wednesday, November 26, 2025` |
| `--start` | Voting start time | `8:00 AM` |
| `--end` | Voting end time | `5:00 PM` |
| `--reason` | Rejection reason (single rejection) | - |
| `--reapply-link` | Reapplication link | From `.env` file |
| `--delay` | Delay before sending (seconds) | `30` |

### Examples

#### 1. Send Single Approval Email
```bash
python send_approval.py --mode single --type approval --email "jdlc67@gmail.com" --name "JUAN DE LA CRUZ" --id "67-1-01"
```

#### 2. Send Single Rejection Email
```bash
python send_approval.py --mode single --type rejection --email "student@gmail.com" --name "JOHN DOE" --id "23-1-12345" --reason "Invalid email domain - must use @jdlc.com"
```

#### 3. Batch Send Approval Emails
```bash
python send_approval.py --mode batch --type approval --csv approval.csv
```

#### 4. Batch Send Rejection Emails
```bash
python send_approval.py --mode batch --type rejection --csv rejection.csv
```

#### 5. Custom Election Details
```bash
python send_approval.py --mode batch --type approval --csv approval.csv --date "December 1, 2025" --start "9:00 AM" --end "6:00 PM"
```

#### 6. Send Immediately (No Delay)
```bash
python send_approval.py --mode batch --csv approval.csv --delay 0
```

#### 7. Send with 60 Second Delay
```bash
python send_approval.py --mode batch --csv approval.csv --delay 60
```

## Workflow

1. **Prepare your CSV file** with student information
2. **Run the command** with appropriate parameters
3. **Review the preview** of recipients and details
4. **Type `yes`** to confirm sending
5. **Wait for countdown** (default 30 seconds)
6. **Press Ctrl+C** anytime during countdown to cancel
7. **Emails are sent** one by one with status updates

## Cancellation

You can cancel the scheduled send at any time by:
- Pressing **Ctrl+C** during the countdown
- Typing **no** when prompted for confirmation

## Gmail App Password Setup

1. Go to your Google Account settings
2. Select **Security** > **2-Step Verification** (enable if not already)
3. Go to **App passwords**
4. Create account and name it appropriately
5. Copy the generated 16-character password
6. Use this password in your `.env` file

## Limits

- **Gmail Free:** 500 emails/day
- **Gmail Workspace:** 2,000 emails/day
- Script includes 1-second delay between emails to avoid rate limiting

## Support

For issues or questions, contact:
- **Email:** facultyofcomputingseb@gmail.com

## License

This project is for internal use by FC-SEB for managing online voting applications.

---
