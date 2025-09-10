"""
Flask Email Service Application
==============================

This is the main Flask application that provides REST API endpoints for sending emails
It handles password reset emails and success confirmations.
It has a generic API end point that can be used by other microservices to send custom emails to the users.


Purpose: Email service for user password reset functionality and sending custom emails to the users.

Endpoints:
- POST /api/email/send-password-reset: Send password reset email with secure token
- POST /api/email/send-reset-success: Send password reset success confirmation
- POST /api/email/test: Send test email to verify functionality
- POST /api/email/send-custom-email: Send generic email based on the request; to be used by other services for sending custom email.
- GET /health: Health check endpoint for monitoring

Dependencies:
- Flask: Web framework for REST API
- sending_email.py: Email service module using smtplib
- config.py: Configuration management from environment variables
"""
from flask import Flask, request, jsonify
from sending_email import email_service     # Import our custom email service
import secrets      # For generating cryptographically secure tokens

# Initialize Flask application
app = Flask(__name__)

def generate_reset_token():
    """  Generate secure token for password reset links.
    Uses Python's secrets module to create a URL-safe token.
    Returns:
        str: A 32-byte URL-safe token (about 43 characters long)
         Example:
        token = generate_reset_token()
        # Returns something like: 'Drmhze6EPcv0fN_81Bj-nA'  """
    return secrets.token_urlsafe(32)

@app.route('/api/email/send-password-reset', methods=['POST'])
def send_password_reset():
    """
     Send password reset email to user with secure reset link.
    
    This endpoint is called when a user requests to reset their password.
    It generates a secure token and sends an email with a reset link.
    
    Expected JSON payload:
    {
        "email": "user@torontomu.ca",      # Required: User's email address
        "username": "john_doe",           # Required: User's username
        "user_name": "John Doe"           # Optional: Display name for email
    }
    
    Returns:
        JSON response with status and reset token
        
    Success Response (200):
    {
        "status": "sent",
        "message": "Password reset email sent successfully",
        "token": "generated-secure-token"
    }
    
    Error Response (400/500):
    {
        "error": "Error description"
    }
    
    Integration Notes:
        - The reset token should be stored in your database with expiration time
        - Link user to this token for password reset verification
        - Token expires in 60 minutes (configurable in email template)
    """
    try:
         # Parse JSON data from request
        data = request.json
        email = data.get('email')
        username = data.get('username')
        user_name = data.get('user_name')   # Optional display name
        
        #Validate required fields
        if not email or not username:
            return jsonify({'error': 'email and username are required'}), 400
        
        # Generate secure reset token for this password reset request
        reset_token = generate_reset_token()

        #Imported config here to avoid circular imports
        from config import Config

        # Construct reset URL with token and username parameters
        # frontend should handle this URL to show password reset form
        reset_url = f"{Config.PASSWORD_RESET_URL_BASE}?token={reset_token}&username={username}"
        
         # Send password reset email using email service
        success = email_service.send_password_reset_email(
            to_email=email,
            username=username,
            reset_url=reset_url,
            user_name=user_name
        )
        
        if success:
             # Email sent successfully - return token for backend to store
            return jsonify({
                'status': 'sent',
                'message': 'Password reset email sent successfully',
                'token': reset_token    # backend should store this with expiration
            }), 200
        else:
            # Email service failed to send
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        # Log error for debugging 
        print(f"Error in password reset endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/send-reset-success', methods=['POST'])
def send_reset_success():
    """ Send confirmation email after successful password reset.
    
    This endpoint should be called AFTER a user has successfully reset their password.
    It sends a confirmation email to notify the user that their password was changed.
    
    Expected JSON payload:
    {
        "email": "user@torontomu.ca",      # Required: User's email address
        "username": "john_doe"            # Required: User's username
    }
    
    Returns:
        JSON response indicating success or failure
        
    Success Response (200):
    {
        "status": "sent",
        "message": "Success email sent"
    }
    
    Error Response (400/500):
    {
        "error": "Error description"
    }
    
    Security Note:
        This email serves as a security notification. If the user didn't reset
        their password, they'll be alerted to potential unauthorized access."""
    
    try:
         # Parse JSON data from request
        data = request.json
        email = data.get('email')
        username = data.get('username')
        
        # Validate required fields
        if not email or not username:
            return jsonify({'error': 'email and username are required'}), 400
        
        # Send success confirmation email
        success = email_service.send_password_reset_success_email(email, username)
        
        if success:
            return jsonify({'status': 'sent', 'message': 'Success email sent'}), 200
        else:
            return jsonify({'error': 'Failed to send success email'}), 500
            
    except Exception as e:
        # Log error for debugging
        print(f"Error in success email endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and load balancing.
    
    This endpoint can be used by:
    - Load balancers to check if service is running
    - Monitoring tools to verify service health
    - DevOps for service discovery
    
    Returns:
        JSON response indicating service is healthy
        
    Response (200):
    {
        "status": "healthy",
        "service": "email-service"
    }"""
    return jsonify({'status': 'healthy', 'service': 'email-service'}), 200

@app.route('/api/email/send-custom-email', methods=['POST'])
def send_custom_email():
    """
    Generic email endpoint for other microservices
    
    Request Body:
    {
        "to_email": "user@torontomu.ca",
        "subject": " Subject",
        "html_content": "<h1> HTML content</h1>",
        
    }
    """
    try:
        data = request.json
        to_email = data.get('to_email')
        subject = data.get('subject')
        html_content = data.get('html_content')

        if not all(to_email and subject and html_content):
            return jsonify({'error': 'to_email, subject, and html_content are required'}), 400
        
        success = email_service.send_email(to_email, subject, html_content)

        if success:
            return jsonify({'status': 'sent', 'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/test', methods=['POST'])
def test_email():
    """ Test endpoint to verify email service functionality.
    
    This endpoint is used for:
    - Testing email configuration during setup
    - Verifying SMTP credentials work correctly  
    - Debugging email delivery issues
    - Integration testing
    
    Expected JSON payload:
    {
        "email": "test@example.com"       # Optional: defaults to test@example.com
    }
    
    Returns:
        JSON response indicating test result
        
    Success Response (200):
    {
        "status": "sent",
        "message": "Test email sent"
    }
    
    Error Response (500):
    {
        "error": "Failed to send test email"
    }
    
    Note: This endpoint should be disabled or secured in production environment."""
    try:
         # Parse JSON data from request
        data = request.json
        test_email = data.get('email', 'test@example.com')
        
        # Send test email using basic email function
        success = email_service.send_email(
            to_email=test_email,
            subject="Test Email - Computer Networks Program",
            html_content="<h1>Test Email</h1><p>This is a test email from the email service.</p>",
            text_content="Test Email\n\nThis is a test email from the email service."
        )
        
        if success:
            return jsonify({'status': 'sent', 'message': 'Test email sent'}), 200
        else:
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Application entry point
if __name__ == '__main__':
     # Print startup information for debugging
    print("Starting Email Service with smtplib...")
    print("Available endpoints:")
    print("  POST /api/email/send-password-reset")
    print("  POST /api/email/send-reset-success")
    print("  POST /api/email/test")
    print("  GET  /health")

      # Start Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
      # Enable debug mode for development
      # Accept connections from all interfaces (0.0.0.0)
      # Default port for email service