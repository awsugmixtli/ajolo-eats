import logging, os
from postmarker.core import PostmarkClient

# Load env
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
POSTMARK_TOKEN = os.environ.get('POSTMARK_API_TOKEN')

# Logger setup
logger = logging.getLogger("__name__")
logger.setLevel(LOG_LEVEL)

# Postmark setup
postmark = PostmarkClient(server_token=POSTMARK_TOKEN)

def send_email(receiver, subject, body, sender, postmark=postmark):
  """
  Send an email using Postmark service.
  Parameters:
    receiver: <list> with the recipients (TO) of the email.
    subject: <string> with the subject of the email.
    body: <string> with the body of the email.
    postmark: <PostmarkClient> with the client instantiation of Postmark.
    sender: <string> with the sender (FROM) of the email.
  """
  postmark.emails.send(
    From = sender,
    To = receiver,
    Subject = subject,
    HtmlBody = body,
  )

def lambda_handler(event, context):
  """
  Lambda handler function
  Parameters:
    event: <Dict> with the Lambda function event data.
    context: Lambda runtime context.
  Returns:
    <Dict> with status message.
  """
  id = event["order_id"]
  sender = event["from_email"]
  receiver = event["client_email"]
  name = event["client_name"]
  time = event["expected_delivery"]
  subject = "¡Tu pedido #{} va en camino!".format(id)
  body = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{}</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f8f8; padding: 20px; border-radius: 5px;">
            <h1 style="color: #2b2b2b; margin-bottom: 20px;">¡Pedido en camino!</h1>
            <p>Estimado {},</p>
            
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Detalles del Pedido:</h3>
                <p>Nos complace informarte que tu pedido está en camino, debes recibirlo a las {}</p>
            </div>
            
            <p style="color: #666;">Este es un mensaje automático, por favor no respondas a este correo.</p>
        </div>
    </body>
    </html>
  """.format(subject, name, time)
  
  send_email(receiver, subject, body, sender)