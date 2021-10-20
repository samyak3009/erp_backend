import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from mailqueue.models import MailerMessage

for _ in range(10):
    my_email = "noreply@kiet.edu"
    my_name = "Dave Johnston"
    content = """
    Dear John,

    This is an example email from Dave.

    Thanks,
    Dave Johnston!
    """
    msg = MailerMessage()
    msg.subject = "Hello World"
    msg.to_address = "noreply@kiet.edu"

    # For sender names to be displayed correctly on mail clients, simply put your name first
    # and the actual email in angle brackets 
    # The below example results in "Dave Johnston <dave@example.com>"
    msg.from_address = '{} <{}>'.format(my_name, my_email)

    # As this is only an example, we place the text content in both the plaintext version (content) 
    # and HTML version (html_content).
    msg.content = content
    msg.html_content = content
    msg.save()

