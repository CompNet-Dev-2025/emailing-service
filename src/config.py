"""Configuration Management for Email Service
==========================================

This module handles all configuration settings for the email service application.
It loads sensitive information from environment variables for security.

Security Features:
- Sensitive data (passwords, API keys) stored in environment variables
- No hardcoded credentials in source code
- Easy configuration management across different environments

Setup Instructions:
1. Create a .env file in your project root with:
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=465
   ADMIN_EMAIL=your-email@gmail.com
   ADMIN_PASSWORD=your-16-digit-app-password
   PASSWORD_RESET_URL_BASE=https://yourapp.com/reset  (Need to be changed)

2. For Gmail, use an App Password (not your regular password):
   - Enable 2-Factor Authentication
   - Generate App Password in Google Account settings
   - Use the 16-character app password
   **Gmail was used for test purposes. 
   """


import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This must be called before accessing environment variables

load_dotenv()

class Config:

    """
    Configuration class that centralizes all application settings.
    
    This class loads configuration from environment variables, providing
    defaults where appropriate and keeping sensitive information secure.
    
    Environment Variables Required:
        ADMIN_EMAIL: Gmail address for sending emails (TMU email in future)
        ADMIN_PASSWORD: Gmail App Password (16 characters)
        
    Environment Variables Optional:
        MAIL_SERVER: SMTP server (defaults to Gmail for now)
        MAIL_PORT: SMTP port (defaults to 465 for SSL)
        PASSWORD_RESET_URL_BASE: Base URL for password reset links
    """
   
   # SMTP Server Configuration (Gmail)
   # Need to be changed in future
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')

# SMTP Port Configuration
    # Port 465: SSL/TLS which is recommended for Gmail
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))  
    
    # Email credentials
     # Sender email address - MUST be set in environment variables
     #For gmai: yourmail@gmail.com
     #For future: compnetadmin@torontomu.ca

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

    # Email password - MUST be set in environment variables
    # For Gmail: Use App Password (16-character code), not regular password  
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')  
    
    # Application URLs
    # Base URL for password reset links
    # This should point to the frontend's password reset page
    # The final URL will be: {BASE_URL}?token={token}&username={username}
    PASSWORD_RESET_URL_BASE = os.environ.get('PASSWORD_RESET_URL_BASE', 'https://yourapp.com/reset')  #Need to be changed