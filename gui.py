import csv
import os
import shutil
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from dotenv import load_dotenv

import send

ENV_PATH = ".env"
DEFAULT_SMTP_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = "587"
DEFAULT_ORG_NAME = "Student Election Board"
STATUS_TRUE_VALUES = {"yes", "y", "true", "1", "sent", "done"}


class UiLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.lock = threading.Lock()

    def write(self, message):
        if not message:
            return
        with self.lock:
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, message + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")

    def clear(self):
        with self.lock:
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.configure(state="disabled")


class StreamToLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        text = message.strip()
        if text:
            self.logger.write(text)

    def flush(self):
        return


def load_env_values():
    load_dotenv(ENV_PATH, override=True)
    return {
        "SMTP_SERVER": os.getenv("SMTP_SERVER", DEFAULT_SMTP_SERVER),
        "SMTP_PORT": os.getenv("SMTP_PORT", DEFAULT_SMTP_PORT),
        "SENDER_EMAIL": os.getenv("SENDER_EMAIL", ""),
        "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD", ""),
        "ALTERNATIVE_EMAIL_FORM_LINK": os.getenv("ALTERNATIVE_EMAIL_FORM_LINK", ""),
        "BALLOT_LINK": os.getenv("BALLOT_LINK", ""),
        "PRECINCT_LOCATION": os.getenv("PRECINCT_LOCATION", ""),
        "ORG_NAME": os.getenv("ORG_NAME", DEFAULT_ORG_NAME),
        "CONTACT_EMAIL": os.getenv("CONTACT_EMAIL", ""),
    }


def write_env(values):
    lines = []
    for key in [
        "SMTP_SERVER",
        "SMTP_PORT",
        "SENDER_EMAIL",
        "SENDER_PASSWORD",
        "ALTERNATIVE_EMAIL_FORM_LINK",
        "BALLOT_LINK",
        "PRECINCT_LOCATION",
        "ORG_NAME",
        "CONTACT_EMAIL",
    ]:
        val = values.get(key, "")
        lines.append(f"{key}={val}")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def reload_send_config():
    values = load_env_values()
    send.SMTP_SERVER = values["SMTP_SERVER"]
    try:
        send.SMTP_PORT = int(values["SMTP_PORT"])
    except ValueError:
        send.SMTP_PORT = 587
    send.SENDER_EMAIL = values["SENDER_EMAIL"]
    send.SENDER_PASSWORD = values["SENDER_PASSWORD"]
    send.ALTERNATIVE_EMAIL_FORM_LINK = values["ALTERNATIVE_EMAIL_FORM_LINK"]
    send.PRECINCT_LOCATION = values["PRECINCT_LOCATION"]
    send.BALLOT_LINK = values["BALLOT_LINK"]
    send.ORG_NAME = values["ORG_NAME"]
    send.CONTACT_EMAIL = values["CONTACT_EMAIL"]
    return values


def parse_csv(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if not rows:
        raise ValueError("CSV file is empty.")

    first_row = rows[0]
    headers = {k.lower().strip(): k for k in first_row.keys()}

    email_col = None
    name_col = None
    for key in headers:
        if key == "email":
            email_col = headers[key]
        elif key in {"name", "student_name"}:
            name_col = headers[key]

    for key in headers:
        if key.endswith("_emailed"):
            continue
        if not email_col and "email" in key:
            email_col = headers[key]
        elif not name_col and "name" in key:
            name_col = headers[key]
    missing_cols = []
    if not email_col:
        missing_cols.append("email")
    if not name_col:
        missing_cols.append("name")

    if missing_cols:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing_cols)
            + ". Expected: email,name"
        )

    if not fieldnames:
        fieldnames = list(rows[0].keys())

    return rows, fieldnames, email_col, name_col


def status_is_sent(value):
    if value is None:
        return False
    return str(value).strip().lower() in STATUS_TRUE_VALUES


def ensure_status_column(fieldnames, email_type):
    status_col = f"{email_type}_emailed"
    if status_col not in fieldnames:
        fieldnames.append(status_col)
    return status_col


def write_csv_rows(csv_path, fieldnames, rows):
    directory = os.path.dirname(csv_path) or "."
    fd, temp_path = tempfile.mkstemp(prefix="emails_", suffix=".csv", dir=directory)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    shutil.move(temp_path, csv_path)


class EmailSenderGui:
    def __init__(self, root):
        self.root = root
        self.root.title("SEB Email Sender")
        self.cancel_event = threading.Event()

        self.build_ui()
        self.load_env_into_fields()

    def build_ui(self):
        self.root.geometry("980x680")
        self.root.minsize(920, 620)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        config_frame = ttk.LabelFrame(main_frame, text="Configuration (.env)", padding=10)
        config_frame.pack(fill=tk.X)

        self.smtp_server_var = tk.StringVar(value=DEFAULT_SMTP_SERVER)
        self.smtp_port_var = tk.StringVar(value=DEFAULT_SMTP_PORT)
        self.sender_email_var = tk.StringVar()
        self.sender_password_var = tk.StringVar()
        self.alt_email_link_var = tk.StringVar()
        self.ballot_link_var = tk.StringVar()
        self.precinct_location_var = tk.StringVar()
        self.org_name_var = tk.StringVar(value=DEFAULT_ORG_NAME)
        self.contact_email_var = tk.StringVar()

        self._row_entry(config_frame, 0, "Sender Email", self.sender_email_var)
        self._row_entry(config_frame, 1, "Sender App Password", self.sender_password_var, show="*")
        self._row_entry(config_frame, 2, "Alternative Email Form Link (optional)", self.alt_email_link_var)
        self._row_entry(config_frame, 3, "Ballot Link", self.ballot_link_var)
        self._row_entry(config_frame, 4, "Precinct Location (optional)", self.precinct_location_var)
        self._row_entry(config_frame, 5, "Organization Name", self.org_name_var)
        self._row_entry(config_frame, 6, "Contact Email", self.contact_email_var)

        button_row = ttk.Frame(config_frame)
        button_row.grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Button(button_row, text="Load .env", command=self.load_env_into_fields).pack(side=tk.LEFT)
        ttk.Button(button_row, text="Save .env", command=self.save_env_from_fields).pack(side=tk.LEFT, padx=6)

        send_frame = ttk.LabelFrame(main_frame, text="Send Emails", padding=10)
        send_frame.pack(fill=tk.X, pady=10)

        self.mode_var = tk.StringVar(value="batch")
        self.type_var = tk.StringVar(value="blast")
        self.delay_var = tk.StringVar(value="30")
        self.email_delay_var = tk.StringVar(value=str(send.DEFAULT_DELAY_BETWEEN_EMAILS))

        mode_row = ttk.Frame(send_frame)
        mode_row.pack(fill=tk.X)
        ttk.Label(mode_row, text="Mode").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_row, text="Batch", variable=self.mode_var, value="batch", command=self.update_mode).pack(
            side=tk.LEFT, padx=8
        )
        ttk.Radiobutton(mode_row, text="Single", variable=self.mode_var, value="single", command=self.update_mode).pack(
            side=tk.LEFT
        )

        type_row = ttk.Frame(send_frame)
        type_row.pack(fill=tk.X, pady=6)
        ttk.Label(type_row, text="Email Type").pack(side=tk.LEFT)
        ttk.Radiobutton(type_row, text="Notification (blast)", variable=self.type_var, value="blast").pack(
            side=tk.LEFT, padx=8
        )
        ttk.Radiobutton(type_row, text="Ballot Link", variable=self.type_var, value="ballot_links").pack(
            side=tk.LEFT, padx=8
        )
        ttk.Radiobutton(type_row, text="Precinct", variable=self.type_var, value="precinct").pack(
            side=tk.LEFT, padx=8
        )
        ttk.Radiobutton(type_row, text="Reminder", variable=self.type_var, value="reminder").pack(
            side=tk.LEFT
        )

        file_row = ttk.Frame(send_frame)
        file_row.pack(fill=tk.X, pady=6)
        self.csv_path_var = tk.StringVar()
        ttk.Label(file_row, text="CSV File").pack(side=tk.LEFT)
        self.csv_entry = ttk.Entry(file_row, textvariable=self.csv_path_var, width=62)
        self.csv_entry.pack(side=tk.LEFT, padx=8)
        self.browse_button = ttk.Button(file_row, text="Browse", command=self.browse_csv)
        self.browse_button.pack(side=tk.LEFT)

        single_row = ttk.Frame(send_frame)
        single_row.pack(fill=tk.X, pady=6)
        self.single_email_var = tk.StringVar()
        self.single_name_var = tk.StringVar()
        ttk.Label(single_row, text="Single Email").pack(side=tk.LEFT)
        self.single_email_entry = ttk.Entry(single_row, textvariable=self.single_email_var, width=28)
        self.single_email_entry.pack(side=tk.LEFT, padx=6)
        ttk.Label(single_row, text="Name").pack(side=tk.LEFT)
        self.single_name_entry = ttk.Entry(single_row, textvariable=self.single_name_var, width=22)
        self.single_name_entry.pack(side=tk.LEFT, padx=6)

        timing_row = ttk.Frame(send_frame)
        timing_row.pack(fill=tk.X, pady=6)
        ttk.Label(timing_row, text="Delay Before Send (sec)").pack(side=tk.LEFT)
        ttk.Entry(timing_row, textvariable=self.delay_var, width=8).pack(side=tk.LEFT, padx=6)
        ttk.Label(timing_row, text="Delay Between Emails (sec)").pack(side=tk.LEFT, padx=12)
        ttk.Entry(timing_row, textvariable=self.email_delay_var, width=8).pack(side=tk.LEFT)

        action_row = ttk.Frame(send_frame)
        action_row.pack(fill=tk.X, pady=8)
        ttk.Button(action_row, text="Send", command=self.send_emails).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Cancel", command=self.cancel_send).pack(side=tk.LEFT, padx=6)

        log_frame = ttk.LabelFrame(main_frame, text="Status Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=14, state="disabled", wrap="word")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.logger = UiLogger(self.log_text)

        self.update_mode()

    def _row_entry(self, parent, row, label, var, show=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(parent, textvariable=var, width=60, show=show)
        entry.grid(row=row, column=1, sticky="w", pady=2, padx=6)

    def update_mode(self):
        mode = self.mode_var.get()
        batch_state = "normal" if mode == "batch" else "disabled"
        single_state = "normal" if mode == "single" else "disabled"

        self.csv_entry.configure(state=batch_state)
        self.browse_button.configure(state=batch_state)

        self.single_email_entry.configure(state=single_state)
        self.single_name_entry.configure(state=single_state)

    def browse_csv(self):
        path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV Files", "*.csv")],
        )
        if path:
            self.csv_path_var.set(path)

    def load_env_into_fields(self):
        values = load_env_values()
        self.sender_email_var.set(values["SENDER_EMAIL"])
        self.sender_password_var.set(values["SENDER_PASSWORD"])
        self.alt_email_link_var.set(values["ALTERNATIVE_EMAIL_FORM_LINK"])
        self.ballot_link_var.set(values["BALLOT_LINK"])
        self.precinct_location_var.set(values["PRECINCT_LOCATION"])
        self.org_name_var.set(values["ORG_NAME"])
        self.contact_email_var.set(values["CONTACT_EMAIL"])
        self.logger.write("Loaded values from .env")

    def save_env_from_fields(self):
        values = {
            "SMTP_SERVER": DEFAULT_SMTP_SERVER,
            "SMTP_PORT": DEFAULT_SMTP_PORT,
            "SENDER_EMAIL": self.sender_email_var.get().strip(),
            "SENDER_PASSWORD": self.sender_password_var.get().strip(),
            "ALTERNATIVE_EMAIL_FORM_LINK": self.alt_email_link_var.get().strip(),
            "BALLOT_LINK": self.ballot_link_var.get().strip(),
            "PRECINCT_LOCATION": self.precinct_location_var.get().strip(),
            "ORG_NAME": self.org_name_var.get().strip() or DEFAULT_ORG_NAME,
            "CONTACT_EMAIL": self.contact_email_var.get().strip(),
        }

        if not values["CONTACT_EMAIL"]:
            values["CONTACT_EMAIL"] = values["SENDER_EMAIL"]

        if not values["SENDER_EMAIL"] or not values["SENDER_PASSWORD"]:
            messagebox.showwarning("Missing Required", "Sender email and app password are required.")
            return

        write_env(values)
        reload_send_config()
        self.logger.write("Saved .env and reloaded configuration.")

    def cancel_send(self):
        self.cancel_event.set()
        self.logger.write("Cancel requested. Waiting for current email to finish...")

    def send_emails(self):
        self.cancel_event.clear()
        mode = self.mode_var.get()
        email_type = self.type_var.get()

        try:
            delay = int(self.delay_var.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Delay must be a number.")
            return

        try:
            email_delay = int(self.email_delay_var.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Delay between emails must be a number.")
            return

        values = reload_send_config()
        missing = []
        if not values["SMTP_SERVER"]:
            missing.append("SMTP Server")
        if not values["SMTP_PORT"]:
            missing.append("SMTP Port")
        if not values["SENDER_EMAIL"]:
            missing.append("Sender Email")
        if not values["SENDER_PASSWORD"]:
            missing.append("Sender App Password")
        if email_type == "ballot_links" and not values["BALLOT_LINK"]:
            missing.append("Ballot Link")

        if missing:
            messagebox.showerror(
                "Missing Configuration",
                "Please fill in these fields in the Configuration section and click Save .env:\n"
                + "\n".join(missing),
            )
            return

        if mode == "batch":
            csv_path = self.csv_path_var.get().strip()
            if not csv_path:
                messagebox.showerror("Missing CSV", "Please choose a CSV file.")
                return
            thread = threading.Thread(
                target=self.run_batch,
                args=(csv_path, email_type, delay, email_delay),
                daemon=True,
            )
        else:
            email = self.single_email_var.get().strip()
            name = self.single_name_var.get().strip()
            if not all([email, name]):
                messagebox.showerror("Missing Info", "Please fill in email and name.")
                return

            thread = threading.Thread(
                target=self.run_single,
                args=(email_type, email, name, delay),
                daemon=True,
            )

        thread.start()

    def run_single(self, email_type, email, name, delay):
        self.logger.write("Preparing single email...")
        if not self.wait_with_cancel(delay, "Sending will start in"):
            return

        if email_type == "blast":
            result = send.send_blast_email(email, name)
        elif email_type == "ballot_links":
            result = send.send_ballot_links_email(email, name)
        elif email_type == "precinct":
            result = send.send_precinct_email(email, name)
        else:
            result = send.send_reminder_email(email, name)

        if result:
            self.logger.write("Single email sent successfully.")
        else:
            self.logger.write("Single email failed. Check configuration and try again.")

    def run_batch(self, csv_path, email_type, delay, email_delay):
        self.logger.write("Loading CSV...")
        try:
            rows, fieldnames, email_col, name_col = parse_csv(csv_path)
        except Exception as exc:
            self.logger.write(f"Error: {exc}")
            return

        status_col = ensure_status_column(fieldnames, email_type)
        pending_rows = [row for row in rows if not status_is_sent(row.get(status_col))]
        already_sent = len(rows) - len(pending_rows)
        self.logger.write(f"Batch size: {len(rows)}")
        self.logger.write(f"Already emailed: {already_sent}")
        self.logger.write(f"Pending: {len(pending_rows)}")
        if not pending_rows:
            self.logger.write("No pending recipients. Nothing to send.")
            return

        write_csv_rows(csv_path, fieldnames, rows)
        if not self.wait_with_cancel(delay, "Batch will start in"):
            return

        success_count = 0
        fail_count = 0

        for idx, row in enumerate(pending_rows, 1):
            if self.cancel_event.is_set():
                self.logger.write("Batch cancelled by user.")
                break

            recipient = row.get(email_col, "").strip()
            name = row.get(name_col, "").strip()
            self.logger.write(f"[{idx}/{len(rows)}] Sending to {name} <{recipient}>...")

            if email_type == "blast":
                result = send.send_blast_email(recipient, name)
            elif email_type == "ballot_links":
                result = send.send_ballot_links_email(recipient, name)
            elif email_type == "precinct":
                result = send.send_precinct_email(recipient, name)
            else:
                result = send.send_reminder_email(recipient, name)

            if result:
                success_count += 1
                row[status_col] = "yes"
            else:
                fail_count += 1
                row[status_col] = "failed"

            write_csv_rows(csv_path, fieldnames, rows)

            if idx < len(pending_rows):
                if not self.wait_with_cancel(email_delay, "Waiting before next email"):
                    break

        self.logger.write("Batch complete.")
        self.logger.write(f"Success: {success_count}")
        self.logger.write(f"Failed: {fail_count}")

    def wait_with_cancel(self, seconds, label):
        if seconds <= 0:
            return True
        for remaining in range(seconds, 0, -1):
            if self.cancel_event.is_set():
                self.logger.write("Cancelled by user.")
                return False
            self.logger.write(f"{label} {remaining} sec")
            time.sleep(1)
        return True


def main():
    root = tk.Tk()
    app = EmailSenderGui(root)
    sys.stdout = StreamToLogger(app.logger)
    sys.stderr = StreamToLogger(app.logger)
    root.mainloop()


if __name__ == "__main__":
    main()
