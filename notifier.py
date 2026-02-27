""" Email notification module for PBS Job Monitor & Notifier.

This module handles sending email notifications when PBS jobs complete.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from logger import LoggerConfig


# Step 1: Initialize logger for notifier module
logger = LoggerConfig.setup("notifier")


class EmailNotifier:
    """Handles email notifications for PBS job completion.

    This class provides functionality to send emails using SMTP protocol
    to notify users when their PBS jobs complete.
    """

    def __init__(self, smtp_server: str, smtp_port: int,
                 smtp_user: str, smtp_password: str):
        """Initialize the EmailNotifier with SMTP credentials.

        Args:
            smtp_server: The SMTP server address.
            smtp_port: The SMTP port number.
            smtp_user: The SMTP username (email address).
            smtp_password: The SMTP password or app token.
        """
        # Step 1: Store SMTP configuration
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_notification(self, recipient_email: str, job_id: str,
                          job_name: Optional[str] = None,
                          exit_status: Optional[str] = None) -> bool:
        """Send an email notification about job completion.

        Args:
            recipient_email: The recipient's email address.
            job_id: The PBS job ID.
            job_name: Optional job name for the email subject.
            exit_status: Optional exit status for the email body.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        logger.info(f"Preparing email notification for job {job_id} to {recipient_email}")

        # Step 1: Create email message
        message = self._create_message(
            recipient_email, job_id, job_name, exit_status
        )

        # Step 2: Send the email via SMTP
        try:
            result = self._send_email(message, recipient_email)
            logger.info(f"Email notification sent successfully for job {job_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to send email notification for job {job_id}: {e}")
            return False

    def _create_message(self, recipient_email: str, job_id: str,
                        job_name: Optional[str] = None,
                        exit_status: Optional[str] = None) -> MIMEMultipart:
        """Create the email message with subject and body.

        Args:
            recipient_email: The recipient's email address.
            job_id: The PBS job ID.
            job_name: Optional job name for the email subject.
            exit_status: Optional exit status for the email body.

        Returns:
            A MIMEMultipart object containing the email message.
        """
        # Step 1: Create multipart message
        message = MIMEMultipart()
        message["From"] = self.smtp_user
        message["To"] = recipient_email

        # Step 2: Construct email subject
        job_name_str = job_name if job_name else "Unknown"
        subject = f"PBS Job Completed: {job_name_str} (Job ID: {job_id})"
        message["Subject"] = subject

        # Step 3: Construct email body
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"Job ID: {job_id}\n"
        body += f"Job Name: {job_name_str}\n"
        body += f"Completion Time: {timestamp}\n"
        if exit_status is not None:
            body += f"Exit Status: {exit_status}\n"
        body = MIMEText(body, "plain")

        # Step 4: Attach body to message
        message.attach(body)
        return message

    def _send_email(self, message: MIMEMultipart, recipient_email: str) -> bool:
        """Send the email message via SMTP.

        Args:
            message: The MIMEMultipart message to send.
            recipient_email: The recipient's email address.

        Returns:
            True if the email was sent successfully, False otherwise.

        Raises:
            smtplib.SMTPException: If SMTP communication fails.
        """
        # Step 1: Connect to SMTP server
        logger.debug(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            # Step 2: Start TLS if available
            logger.debug("Starting TLS")
            server.starttls()

            # Step 3: Login with credentials
            logger.debug(f"Logging in as {self.smtp_user}")
            server.login(self.smtp_user, self.smtp_password)

            # Step 4: Send the email
            logger.debug(f"Sending email to {recipient_email}")
            server.send_message(message)
            logger.debug("Email sent successfully")

        return True
