import smtplib
from email.message import EmailMessage

ADMIN_MAIL = ""
STUDENT_MAIL = ""
PASSCODE_MAIL= "" #ovcfymyouzevkgtz

msg = EmailMessage()
msg['Subject'] = "Test Email"
msg['From'] = ADMIN_MAIL
msg['To'] = STUDENT_MAIL
msg.set_content("This is a test message from Python.")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(ADMIN_MAIL,PASSCODE_MAIL ) #ovcfymyouzevkgtz
    server.send_message(msg)

print("Test email sent.")
