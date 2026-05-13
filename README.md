# Email Sender for Elections

> **Easy-to-use automated email sender for election notifications and ballot distribution**

This tool helps you send professional emails to students for election notifications and voting updates. No coding experience needed!

---

## What Does This Tool Do?

This program can send four types of emails:

1. **Notification Email** (`blast`) - Sent BEFORE voting day to inform students
2. **Ballot Link Email** (`ballot_links`) - Sent ON voting day with the actual voting link (one Google Form for everyone)
3. **Precinct Email** (`precinct`) - Shares the physical voting precinct details
4. **Reminder Email** (`reminder`) - Sent 2 days before election day with the alternative email deadline

---

## What You'll Need

Before you start, make sure you have:

- ✅ A computer with Windows
- ✅ Python installed (version 3.7 or higher)
- ✅ A Gmail account for sending emails
- ✅ A list of student emails in a CSV file (Excel can create this)

---

## Quick Start Guide

### Step 1: Install Python

1. Check if Python is already installed:
   - Open **Command Prompt** (search for "cmd" in Windows)
   - Type: `python --version` and press Enter
   - If you see a version number (like `Python 3.12.0`), you're good! Skip to Step 2.

2. If not installed, download Python:
   - Visit: https://www.python.org/downloads/
   - Click the big yellow button "Download Python"
   - Run the installer
---

### Step 2: Install Required Package

1. Open **Command Prompt** (type "cmd" in Windows search)
2. Type this command and press Enter:
   ```
   pip install python-dotenv
   ```
3. Wait for it to finish (you'll see "Successfully installed...")

![Project Screenshot](https://drive.google.com/uc?export=view&id=1IMMuX3DMiwh_VMt_Qw6QQGfJe35vLZgA)

---

### Optional: Use the Visual Setup (No Command Line Needed)

If you want a point-and-click screen for non-technical users, run the GUI:

1. Open **Command Prompt**
2. Go to your SEB folder
3. Run:
   ```
   python gui.py
   ```

In the GUI, fill in the .env fields, click **Save .env**, then choose **Batch** or **Single** and click **Send**.

---

### Optional: Use the Windows EXE (No Python Needed)

If you have the single-file exe, run:
```
dist\sebEmailSender.exe
```

Place your `.env` and CSV file in the same folder as the exe.

---

### Step 3: Set Up Gmail App Password

**Why?** Gmail requires a special password for programs to send emails (not your regular password).

1. Go to your Gmail account settings
2. Enable **2-Step Verification** first (if not already enabled)
   - Visit: https://myaccount.google.com/security
   - Click "2-Step Verification" and follow the steps

![Project Screenshot](https://drive.google.com/uc?export=view&id=19dQO6Ohk_-jxBe2626wvnxcGoRY7Ci6C)

3. Create an **App Password**:
   - Visit: https://myaccount.google.com/apppasswords
   - Or search for "App passwords" in your Google Account settings
   - Assign name for app password, can be anything
   - Click "Create"
   - **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

![Project Screenshot](https://drive.google.com/uc?export=view&id=1h43EE2NqnMXJsH49i-FHbFg2G7HRa9UQ)

⚠️ **IMPORTANT**: Save this password! You'll need it in the next step.

---

### Step 4: Create Your Configuration File

1. Open **Notepad** (search for "Notepad" in Windows)
2. Copy and paste this text (replace the example values with your real information):

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop
ALTERNATIVE_EMAIL_FORM_LINK=https://forms.gle/YourGoogleFormLink
BALLOT_LINK=https://forms.gle/YourBallotFormLink
PRECINCT_LOCATION=Room 123, Main Building, VSU Campus
ORG_NAME=Student Election Board
CONTACT_EMAIL=your_contact_email@vsu.edu.ph
```

3. **Replace these values:**
   - `your_email@gmail.com` → Your Gmail address
   - `abcdefghijklmnop` → The 16-character App Password from Step 3 (remove spaces)
   - `https://forms.gle/YourGoogleFormLink` → Your Google Form link for alternative email requests
   - `https://forms.gle/YourBallotFormLink` → Your Google Form ballot link (same for all students)
   - `Room 123, Main Building, VSU Campus` → The actual voting precinct location
   - `ORG_NAME` → The organization name shown in the email footer
   - `CONTACT_EMAIL` → The contact email shown in the email footer

4. Save the file:
   - Click **File** → **Save As**
   - Navigate to your SEB folder (where `send.py` is located)
   - For "File name", type: `.env` (yes, with the dot at the start!)
   - For "Save as type", select: **All Files**
   - Click **Save**

![Project Screenshot](https://drive.google.com/uc?export=view&id=1rkLL1sCP9td0TOxuizsa7jwGPBUnBqFg)

---

### Step 5: Prepare Your Student List (CSV File)

#### For Notification Emails (Before Voting Day)

Create a file called `students.csv` with these columns:

```
email,name
juan.delacruz@vsu.edu.ph,Juan Dela Cruz
maria.santos@vsu.edu.ph,Maria Santos
```

![Project Screenshot](https://drive.google.com/uc?export=view&id=1P6wsM6jTXvygUVjigHg6ji1MDXRb137C)


**How to create this in Excel:**
1. Open Excel
2. Create two columns: `email`, `name`
3. Fill in your student data
4. Click **File** → **Save As**
5. Choose **CSV (Comma delimited) (*.csv)** as the file type
6. Save it in your SEB folder as `students.csv`

---

#### For Ballot Link Emails (On Voting Day)

Use the **SAME** CSV file as notifications! The ballot link comes from your `.env` file, not the CSV.

```
email,name
juan.delacruz@vsu.edu.ph,Juan Dela Cruz
maria.santos@vsu.edu.ph,Maria Santos
```

**Note**: All students will receive the same Google Form ballot link that you configured in `BALLOT_LINK` in your `.env` file.

---

## 📬 How to Send Emails

### Sending Notification Emails (Before Voting Day)

1. Open **Command Prompt**
2. Navigate to any SEB folder:
   ```
   cd C:\Users\YourName\...\SEB
   ```
   (Replace with your actual folder location)

3. Type this command:
   ```
   python send.py --mode batch --type blast --csv students.csv
   ```

4. You'll see a preview of all emails. Type `yes` to confirm.

5. Wait 30 seconds (you can press `Ctrl+C` to cancel if needed)

6. Emails will be sent! 

![Project Screenshot](https://drive.google.com/uc?export=view&id=1A0e8h2NeWWfMa7VyEdO22S915rCg5SlO)
---

### Sending Ballot Links (On Voting Day)

1. Open **Command Prompt**
2. Navigate to your SEB folder:
   ```
   cd C:\Users\YourName\...\SEB
   ```
   (Replace with your actual folder location)

3. Type this command:
   ```
   python send.py --mode batch --type ballot_links --csv students.csv
   ```

4. Confirm and wait for emails to be sent! 

**Note**: Make sure `BALLOT_LINK` is set correctly in your `.env` file before sending!

---

### Sending Precinct Details

```
python send.py --mode batch --type precinct --csv students.csv
```

---

### Sending Reminder (2 Days Before)

```
python send.py --mode batch --type reminder --csv students.csv
```

---

## 🔧 Advanced Options

### Send to Just One Student (Test)

```
python send.py --mode single --type blast --email student@vsu.edu.ph --name "Juan Dela Cruz"
```

### Send Ballot Link to One Student

```
python send.py --mode single --type ballot_links --email student@vsu.edu.ph --name "Juan Dela Cruz"
```

### Send Precinct Details to One Student

```
python send.py --mode single --type precinct --email student@vsu.edu.ph --name "Juan Dela Cruz"
```

### Send Reminder to One Student

```
python send.py --mode single --type reminder --email student@vsu.edu.ph --name "Juan Dela Cruz"
```

### Send Immediately (No 30-Second Wait)

```
python send.py --mode batch --type blast --csv students.csv --delay 0
```

### Wait Longer Before Sending (60 seconds)

```
python send.py --mode batch --type blast --csv students.csv --delay 60
```

### Adjust Delay Between Emails (Anti-Spam)

```
python send.py --mode batch --type blast --csv students.csv --email-delay 45
```

**Note**: Default is 30 seconds between emails. Increase to 45-60 seconds if emails are going to spam.

---

## Preventing Spam Folder Issues

If your emails are being marked as spam, try these solutions:

### **1. Send a Test Email to Yourself First**
- Always send to your own email before sending to students
- If it goes to spam, mark it as "Not Spam"
- This helps train Gmail's filters

### **2. Increase Delay Between Emails**
```bash
# Use 45 seconds between emails instead of 30
python send.py --mode batch --type blast --csv students.csv --email-delay 5

# For very cautious sending, use 60 seconds
python send.py --mode batch --type blast --csv students.csv --email-delay 60
```

### **3. Send in Smaller Batches**
- Don't send more than 50 emails at once
- Split your CSV into smaller files
- Wait 30-60 minutes between batches

### **5. Ask Recipients to Whitelist**
Tell students to:
1. Check their spam folder
2. Mark the email as "Not Spam"
3. Add your `CONTACT_EMAIL` to their contacts

### **6. Check Your Email Content**
- Avoid ALL CAPS in subject lines
- Don't use too many exclamation marks!!!
- Keep a good text-to-image ratio
- Include a physical address (already in footer)

### **7. Verify Your Sender Reputation**
- Use only one Gmail account for sending
- Don't switch between different accounts
- Keep your account in good standing (no violations)

---

##  Common Problems & Solutions

### Problem: "python: command not found"
**Solution**: Python is not installed or not added to PATH. Go back to Step 1.

---

### Problem: "Authentication failed"
**Solution**: 
1. Check your App Password in the `.env` file
2. Make sure there are no spaces in the password
3. Make sure you're using an App Password, not your regular Gmail password


---

### Problem: "CSV file not found"
**Solution**: 
1. Make sure your CSV file is in the same folder as `send.py`
2. Check the file name matches exactly (including `.csv` extension)
3. Use the full path if needed: `--csv "C:\Users\YourName\Desktop\SEB\students.csv"`

---

### Problem: Email not sending
**Solution**:
1. Check your internet connection
2. Make sure your Gmail account is active
3. Check if you've hit Gmail's daily sending limit (500 emails for free accounts)
4. Try sending to yourself first as a test

---

### Problem: Emails going to spam folder
**Solution**:
1. Increase delay between emails: `--email-delay 5` or `--email-delay 10`
2. Send smaller batches (max 50 emails at a time)
3. Send a test to yourself first and mark as "Not Spam"
4. Ask recipients to check spam and whitelist the sender
5. See the "Preventing Spam Folder Issues" section above for more tips

---

### Problem: "Missing required column in CSV"
**Solution**: 
1. Open your CSV file in Excel
2. Make sure the first row has the exact column names (no extra spaces):
   - For notifications: `email,name`
   - For ballot links: `email,name`

**[IMAGE PLACEHOLDER: Screenshot highlighting the correct CSV header row format]**

---

### Resume After Errors or App Closure

When sending in batch, the program adds a status column to your CSV and skips
rows that are already marked as sent. If the app stops, you can rerun the same
batch and it continues where it left off.

---

##  Email Sending Limits

- **Gmail Free Account**: 500 emails per day
- **Gmail Workspace**: 2,000 emails per day

The program automatically waits 1 second between each email to avoid problems.

---

##  What the Emails Look Like

### Notification Email (Gray Header)
- Informs students their email is whitelisted
- Tells them when voting day is (e.g., May 15, 2026, 8:00 AM - 10:00 PM)
- Explains they'll receive the ballot link on voting day
- Shows alternative voting options:
  - Button to apply for different email (deadline: Dec 8, 5PM)
  - In-person precinct information (8:00 AM - 5:00 PM)

**[IMAGE PLACEHOLDER: Screenshot of the notification email as it appears in Gmail]**

---

### Ballot Link Email (Gray Header)
- Contains the actual voting link
- "VOTE" button
- Reminds students voting closes at the configured time
- Shows in-person voting option if they can't access online

**[IMAGE PLACEHOLDER: Screenshot of the ballot link email as it appears in Gmail]**

---

##  Need Help?

If you're stuck:

1. **Read the error message carefully** - it usually tells you what's wrong
2. **Check the Common Problems section** above
3. **Contact the technical team** at your `CONTACT_EMAIL`

---

## ✅ Quick Checklist Before Sending

- [ ] Python is installed (`python --version` shows a version number)
- [ ] `python-dotenv` package is installed (`pip show python-dotenv` shows package info)
- [ ] `.env` file is created with correct Gmail credentials
- [ ] Gmail App Password is set up and working
- [ ] CSV file is prepared with correct format and column names
- [ ] Alternative email form link is added to `.env` file
- [ ] Precinct location is correct in `.env` file
- [ ] **Test email sent successfully to yourself first!**

---

## 🔒 Security Notes

- **NEVER share your `.env` file** - it contains your Gmail password!
- **NEVER commit `.env` to GitHub** - the file is already excluded via `.gitignore`
- The App Password only works for this program, not for logging into your Gmail account
- You can delete App Passwords anytime from your Google Account settings

---

##  File Structure

Your SEB folder should look like this:

```
SEB/
├── send.py                     (The main program - don't edit!)
├── gui.py                      (Visual setup and sending)
├── email_blast.html            (Notification email template)
├── email_ballot_links.html     (Ballot link email template)
├── email_precinct.html         (Precinct email template)
├── email_reminder.html         (Reminder email template)
├── .env                        (Your secret credentials - NEVER share!)
├── .env.example                (Example template - safe to share)
├── students.csv                (Your student list)
├── dist\sebEmailSender.exe     (Single-file Windows executable)
└── README.md                   (This guide you're reading)
```

---

##  Made for Student Election Boards

This tool was created to make election email management easier and more professional.

**For official concerns**: use your configured `CONTACT_EMAIL`

---

## 📝 Quick Command Reference

```bash
# Send notification emails to all students (with default 30-second delay between emails)
python send.py --mode batch --type blast --csv students.csv

# Send ballot links on voting day (uses same CSV, ballot link from .env)
python send.py --mode batch --type ballot_links --csv students.csv

# Send physical precinct details
python send.py --mode batch --type precinct --csv students.csv

# Send reminder email (2 days before election)
python send.py --mode batch --type reminder --csv students.csv

# Test with one email first
python send.py --mode single --type blast --email test@vsu.edu.ph --name "Test User" --id 2021-00000

# Send immediately without countdown (still has 30-second delay between emails)
python send.py --mode batch --type blast --csv students.csv --delay 0

# Increase delay between emails to prevent spam (5 seconds)
python send.py --mode batch --type blast --csv students.csv --email-delay 5

# Send with longer delays for maximum anti-spam protection (60 seconds between emails)
python send.py --mode batch --type blast --csv students.csv --email-delay 60
```

---

**Good luck with your election! 🗳️**
