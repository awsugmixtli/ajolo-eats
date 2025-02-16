from time import strftime
import boto3, json, logging, os, random, re
from datetime import datetime, timedelta
from dateutil import tz
from postmarker.core import PostmarkClient

# Load env
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
POSTMARK_TOKEN = os.environ.get('POSTMARK_API_TOKEN')
TIMEZONE = os.environ.get('TZ', 'America/Mexico_City')
EMAIL_FROM = "AjoloEats <{}>".format(os.environ.get('EMAIL_FROM'))
RESTAURANT_EMAIL = os.environ.get('RESTAURANT_EMAIL')
DELIVERY_EMAIL = os.environ.get('DELIVERY_EMAIL')

# Logger setup
logger = logging.getLogger("__name__")
logger.setLevel(LOG_LEVEL)
## Local testing setup
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
logger.addHandler(ch)

# Timezone setup
runtime_tz = tz.gettz(TIMEZONE)
mex_tz = tz.gettz('America/Mexico_City')

# Constants
time_format = "%I:%M %p"
restaurant_address = "Periférico Blvrd Manuel Ávila Camacho 261, Polanco"
restaurant_name = "El Ajolote Frito"
delivery_name = "Juan"

# Postmark setup
postmark = PostmarkClient(server_token=POSTMARK_TOKEN)

def send_email(receiver, subject, body, postmark=postmark, sender=EMAIL_FROM):
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

def notify_restaurant(restaurant_email, order_id, order, amount, expected_pickup, restaurant = restaurant_name):
  subject = "Nuevo Pedido - {}".format(order_id)
  email_body = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{}</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f8f8; padding: 20px; border-radius: 5px;">
            <h1 style="color: #2b2b2b; margin-bottom: 20px;">¡Nuevo Pedido Recibido!</h1>
            <p>Estimado {},</p>
            <p>Has recibido un nuevo pedido con el número #{}.</p>
            
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Detalles del Pedido:</h3>
                <p><strong>Items:</strong></p>
                {}
                <p><strong>Total:</strong> ${}</p>
            </div>

            <p>Por favor, confirma la recepción de este pedido en tu panel de control.</p>
            <p>La orden debería estar lista a las: {}</p>
            
            <p style="color: #666;">Este es un mensaje automático, por favor no respondas a este correo.</p>
        </div>
    </body>
    </html>
  """.format(subject, restaurant, order_id, order, amount, expected_pickup)
  send_email(restaurant_email, subject, email_body)

def notify_delivery(delivery_email, delivery_address, expected_pickup, delivery_name = delivery_name, restaurant = restaurant_name, restaurant_address = restaurant_address):
  subject = "Nueva Entrega Disponible"
  random.seed()
  distance = "{}Km".format(random.randrange(1, 25))
  email_body = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{}</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f8f8; padding: 20px; border-radius: 5px;">
            <h1 style="color: #2b2b2b; margin-bottom: 20px;">¡Nueva Entrega Disponible!</h1>
            <p>Hola {},</p>
            <p>Hay un nuevo pedido disponible para entrega.</p>
            
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Información de la Entrega:</h3>
                <p><strong>Restaurante:</strong> {}</p>
                <p><strong>Dirección del restaurante:</strong> {}</p>
                <p><strong>Dirección de entrega:</strong> {}</p>
                <p><strong>Distancia aproximada:</strong> {}</p>
                <p><strong>Se estima que lo recojas del restaurante a las:</strong> {}</p>
            </div>

            <div style="background-color: #4CAF50; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0;">¿Aceptas esta entrega?</p>
                <p style="margin: 5px 0;">Tienes 30 segundos para responder</p>
            </div>

            <p>Accede a la app para aceptar o rechazar este pedido.</p>
            
            <p style="color: #666;">Este es un mensaje automático, por favor no respondas a este correo.</p>
        </div>
    </body>
    </html>
  """.format(subject, delivery_name, restaurant, restaurant_address, delivery_address, distance, expected_pickup)
  send_email(delivery_email, subject, email_body)

def notify_customer(customer_email, name, order, amount, expected_arrival, client_address, restaurant = restaurant_name):
  subject = "AjoloEats - Confirmación de pedido"
  email_body = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{}</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f8f8; padding: 20px; border-radius: 5px;">
            <h1 style="color: #2b2b2b; margin-bottom: 20px;">¡Gracias por tu pedido!</h1>
            <p>Hola {},</p>
            <p>Hemos recibido tu pedido #{} correctamente. A continuación, te mostramos los detalles:</p>
            
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Restaurante:</strong> {}</p>
                <p><strong>Total:</strong> ${}</p>
                <p><strong>Tiempo estimado de entrega:</strong> {}</p>
                <p><strong>Dirección de entrega:</strong> {}</p>
            </div>

            <p>Te mantendremos informado sobre el estado de tu pedido.</p>
            <p><strong>¿Preguntas?</strong> Contáctanos a través de nuestra app o responde a este correo.</p>
            
            <p style="margin-top: 20px;">¡Que disfrutes tu comida!</p>
        </div>
    </body>
    </html>
  """.format(subject, name, order, restaurant, amount, expected_arrival, client_address)
  send_email(customer_email, subject, email_body)

def create_events(expected_confirmation, expected_pickup, expected_arrival, expected_feedback, order_id, client_email, client_name):
  client = boto3.client("scheduler")

  scheduler_time_format = f"%Y-%m-%dT%H:%M:%S"

  # Create restaurant check-in schedule
  confirmation = client.create_schedule(
    ActionAfterCompletion = 'DELETE',
    Name="{}_ready_confirmation".format(order_id),
    Description="Schedule to send the restaurant a check-in about order #{} status".format(order_id),
    FlexibleTimeWindow={
      'Mode': 'OFF'
    },
    ScheduleExpression="at({})".format(expected_confirmation.strftime(scheduler_time_format)),
    State="ENABLED",
    Target={
      'Arn': "arn:aws:lambda:us-west-2:833307389424:function:orderCheckIn",
      'RoleArn': "arn:aws:iam::833307389424:role/AllowLambdasRole",
      'Input': json.dumps({
        "order_id": order_id,
        "from_email": EMAIL_FROM,
        "restaurant_email": RESTAURANT_EMAIL,
        "restaurant_name": restaurant_name,
        "expected_pickup": "{}".format(expected_pickup.astimezone(mex_tz).strftime(time_format))
      })
    }
  )

  # Create order on its way schedule
  order_moving = client.create_schedule(
    ActionAfterCompletion = 'DELETE',
    Name="{}_order_moving".format(order_id),
    Description="Schedule to send the customer a notification about #{} status".format(order_id),
    FlexibleTimeWindow={
      'Mode': 'OFF'
    },
    ScheduleExpression="at({})".format(expected_pickup.strftime(scheduler_time_format)),
    State="ENABLED",
    Target={
      'Arn': "arn:aws:lambda:us-west-2:833307389424:function:orderSent",
      'RoleArn': "arn:aws:iam::833307389424:role/AllowLambdasRole",
      'Input': json.dumps({
        "order_id": order_id,
        "from_email": EMAIL_FROM,
        "client_email": client_email,
        "client_name": client_name,
        "expected_delivery": "{}".format(expected_arrival.astimezone(mex_tz).strftime(time_format))
      })
    }
  )

  # Create order delivered schedule
  confirmation = client.create_schedule(
    ActionAfterCompletion = 'DELETE',
    Name="{}_order_delivered".format(order_id),
    Description="Schedule to send the involved parties a notification about #{} being delivered".format(order_id),
    FlexibleTimeWindow={
      'Mode': 'OFF'
    },
    ScheduleExpression="at({})".format(expected_confirmation.strftime(scheduler_time_format)),
    State="ENABLED",
    Target={
      'Arn': "arn:aws:lambda:us-west-2:833307389424:function:orderDelivered",
      'RoleArn': "arn:aws:iam::833307389424:role/AllowLambdasRole",
      'Input': json.dumps({
        "order_id": order_id,
        "from_email": EMAIL_FROM,
        "client_email": client_email
      })
    }
  )

  # Create feedback schedule
  confirmation = client.create_schedule(
    ActionAfterCompletion = 'DELETE',
    Name="{}_feedback_request".format(order_id),
    Description="Schedule to send the customer a reminder to give feedback on #{}".format(order_id),
    FlexibleTimeWindow={
      'Mode': 'OFF'
    },
    ScheduleExpression="at({})".format(expected_confirmation.strftime(scheduler_time_format)),
    State="ENABLED",
    Target={
      'Arn': "arn:aws:lambda:us-west-2:833307389424:function:orderFeedback",
      'RoleArn': "arn:aws:iam::833307389424:role/AllowLambdasRole",
      'Input': json.dumps({
        "order_id": order_id,
        "from_email": EMAIL_FROM,
        "client_email": client_email,
        "client_name": client_name
      })
    }
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
  # Grab variables from event
  id = context.aws_request_id
  id = re.sub("[^0-9]", '', id)[:8]
  body = json.loads(event['body'])
  name = body['nombre']
  last_name = body['apellido']
  email = body['correo']
  order = body['pedido']
  order_total = body['total']
  client_address = body['direccion']
  # Define times
  now = datetime.now(tz=runtime_tz)
  received_time = now.astimezone(mex_tz)
  received_time = received_time.strftime(time_format)
  expected_confirmation = (now + timedelta(minutes = 3))
  expected_pickup = (now + timedelta(minutes = 6))
  expected_arrival = (now + timedelta(minutes = 9))
  expected_feedback = (now + timedelta(minutes = 12))
  # Create events
  create_events(expected_confirmation, expected_pickup, expected_arrival, expected_feedback, id, email, name)
  notify_restaurant(RESTAURANT_EMAIL, id, order, order_total, expected_pickup.astimezone(mex_tz).strftime(time_format))
  notify_delivery(DELIVERY_EMAIL, client_address, expected_pickup.astimezone(mex_tz).strftime(time_format))
  notify_customer(email, name, id, order_total, expected_arrival.astimezone(mex_tz).strftime(time_format), client_address)
  # Return successfully
  success = '''
    {
      "statusCode": 200,
      "message": "Order received successfully, will start processing."
    }
  '''
  return success

if __name__ == "__main__":
  logger.warning("Local invocation detected, using fixed event.")
  random.seed()
  context = {}
  event = {
    "event_id": "{:06d}".format(random.randrange(1, 999999)),
    "nombre": "Mariano",
    "apellido": "Rodríguez",
    "correo": "marianox1994@gmail.com",
    "pedido": "Pizza Margarita, Coca-Cola regular, Brownie",
    "total": "148.25",
    "direccion": "Col. Santa Cruz Buenavista, Puebla"
  }
  lambda_handler(event, context)
