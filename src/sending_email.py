"""
Email Service Implementation using smtplib
==========================================

This module provides email functionality
It handles sending password reset emails and confirmation emails using Gmail's SMTP server.

Features:
- HTML email templates with Jinja2 templating
- Fallback plain text versions for compatibility
- Secure SMTP connection with SSL
- Professional email formatting
- Error handling and logging

Technical Implementation:
- Uses Python's built-in smtplib for SMTP communication
- Uses email.mime modules for proper email formatting  
- Uses Jinja2 for dynamic HTML template rendering """

import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
from config import Config

class EmailService:

# Email service class that handles all email operations.
    
 #   This class encapsulates email functionality including:
  #  - SMTP connection management
   # - Template rendering with Jinja2
    #- Email composition and sending
    #- Error handling and logging
    
    #The service uses Gmail's SMTP server by default but should be modified
    
    def __init__(self):

        """
        Initialize the email service with SMTP configuration and template engine.
        
        Sets up:
        - SMTP server connection parameters from Config
        - Jinja2 template environment for HTML email rendering
        - Template directory path resolution
        """
        # Load SMTP configuration from Config class
        self.smtp_server = Config.MAIL_SERVER
        self.smtp_port = Config.MAIL_PORT
        self.admin_email = Config.ADMIN_EMAIL    # Sender email address
        self.admin_password = Config.ADMIN_PASSWORD # Password of the sender
        
       # Set up Jinja2 template engine for HTML email rendering
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """
        Core email sending method using smtplib.
        
        This method handles the low-level email sending process including:
        - Creating proper MIME multipart messages
        - Adding both HTML and text versions
        - Establishing secure SMTP connection
        - Authentication and message transmission
        
        Args:
            to_email (str): Recipient's email address
            subject (str): Email subject line
            html_content (str): HTML version of email content
            text_content (str, optional): Plain text fallback version
            
        Returns:
            bool: True if email was sent successfully, False otherwise
            
        Technical Details:
            - Uses MIMEMultipart('alternative') for HTML + text versions
            - Establishes SSL connection on port 465
            - Uses SMTP authentication with app password
            - Automatically closes connection after sending
            
        Error Handling:
            - Catches and logs all exceptions during sending
            - Returns False on any failure
            - Prints detailed error messages for debugging
        """
        try:
            # Create MIME multipart message (supports both HTML and text)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.admin_email
            msg['To'] = to_email
            
            # Add plain text version (fallback for email clients that don't support HTML)
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version (primary content with formatting and styling)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email using Gmail's SMTP server with SSL encryption
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.admin_email, self.admin_password)

                # Send the composed message
                server.send_message(msg)
            
            # Log successful send for monitoring and debugging
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:

            # Log detailed error for debugging
            print(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, to_email, username, reset_url, user_name=None):
        """
        Send password reset email using Jinja2 template
        This method is called when a user requests a password reset. It sends
        a professionally formatted email with a secure reset link.
        
        Args:
            to_email (str): User's email address
            username (str): User's username for the account
            reset_url (str): Complete URL with token for password reset
            user_name (str, optional): Display name for personalization
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        Email Content:
            - Professional HTML design with CSS styling
            - Personalized greeting using display name or username
            - Clear call-to-action button for password reset
            - Security information (link expiration, ignore instructions)
            - Branded with Computer Networks Program identity
            
        Template Variables:
            - user_name: Display name for greeting
            - username: Account username 
            - reset_url: Complete reset link with token
            - expiration_minutes: How long the link is valid (60 minutes)
            
        Security Features:
            - Uses secure token in URL (generated by calling application)
            - Includes expiration warning for user awareness
            - Provides instructions if user didn't request res
        """

        # Use display name if provided, otherwise fall back to username
        display_name = user_name or username
        subject = "Password Reset - Computer Networks Program"
        
        # Render HTML email using Jinja2 template
        # Template file: templates/password_reset.html
        template = self.jinja_env.get_template('password_reset.html')
        html_content = template.render(
            user_name=display_name,
            username=username,
            reset_url=reset_url,
            expiration_minutes=60
        )
        
        # Create simple text version for email clients that don't support HTML
        # This ensures the email is accessible to all users
        text_content = f"""
        Hello {display_name},
        
        You requested a password reset for your Computer Networks program account.
        
        Please visit this link to reset your password:
        {reset_url}
        
        This link will expire in 60 minutes for security purposes.
        
        If you didn't request this password reset, you can safely ignore this email.
        
        - Computer Networks Program Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_success_email(self, to_email, username):
        """
        Send confirmation email after successful password reset
         This method is called AFTER a user has successfully changed their password.
        It serves as both confirmation and security notification.
        
        Args:
            to_email (str): User's email address
            username (str): User's username
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        Purpose:
            - Confirm that password was successfully changed
            - Security notification in case of unauthorized access
            - Provide contact information if user didn't make the change
            - Give security recommendations
            
        Template Variables:
            - username: User's account username for personalization
            
        Security Importance:
            This email is crucial for security. If a malicious actor changes
            someone's password, this email alerts the legitimate user.
        """
        subject = "Password Reset Successful - Computer Networks Program"
        
        # Render HTML template
        # Template file: templates/password_reset_success.html
        template = self.jinja_env.get_template('password_reset_success.html')
        html_content = template.render(username=username)
        
        # Create simple text version for compatibility
        text_content = f"""
        Hello {username},
        
        Your password has been successfully reset for the Computer Networks program.
        
        If you did not make this change, please contact support immediately.
        
        - Computer Networks Program Team
        """

        # Send the confirmation email
        return self.send_email(to_email, subject, html_content, text_content)

# Global Email Service Instance
# =============================

# Create a single instance of EmailService that can be imported and used
# throughout the application. This follows the singleton pattern for
# resource management and configuration consistency.
email_service = EmailService()