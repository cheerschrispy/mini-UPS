import smtplib, ssl
def sendEmail(emailAddr):
    port = 465  # For SSL
    password = 'gwfhxmx123'
    smtp_server = "smtp.gmail.com"
    sender_email = "crispylizeyu@gmail.com"  # Enter your address
    receiver_email = emailAddr # Enter receiver address
    message = """\
    Subject: Package Information Updated

    Your Package is Delivered.
    Please Collect In Time"""

    # Create a secure SSL context
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("crispylizeyu@gmail.com", password)
            # TODO: Send email here
            server.sendmail(sender_email, receiver_email, message)
            print("sent email")
    except:
        print("fail to send email: ",receiver_email)

if __name__ == '__main__':
    sendEmail("crispylizeyu@gmail.com")
    