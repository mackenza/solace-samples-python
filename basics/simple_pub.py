import os
import time

# Import Solace Python  API modules from the pysolace package
from pysolace.messaging.messaging_service import MessagingService
from pysolace.messaging.utils.topic import Topic

# No. of messages per second
# Note: Standard edition PubSub+ broker is limited to 10k max ingress
MSG_RATE = 5

def direct_message_publish(messaging_service: MessagingService, topic, message):
    try:
        # Create a direct message publish service and start it
        direct_publish_service = messaging_service.create_direct_message_publisher_builder().build()
        direct_publish_service.start_async()
        # Publish the message!
        direct_publish_service.publish(destination=topic, message=message)
    finally:
        direct_publish_service.terminate()

host = os.environ.get('SOL_HOST') or "localhost"
vpn_name = os.environ.get('SOL_VPN') or "default"
username = os.environ.get('SOL_USERNAME') or "default"
password = os.environ.get('SOL_PASSWORD') or "default"

# Broker Config
broker_props = {
    "solace.messaging.transport.host": host,
    "solace.messaging.service.vpn-name": vpn_name,
    "solace.messaging.authentication.scheme.basic.user-name": username,
    "solace.messaging.authentication.scheme.basic.password": password
    }

# Initialize A messaging service + Connect to the broker
messaging_service = MessagingService.builder().from_properties(broker_props).build()
messaging_service.connect_async()

# Set the message body
body = "this is the body of the msg"

rate = 1
try: 
    while True:
        while rate <= MSG_RATE:
            # Build a dynamic topic
            topic = Topic.of("taxinyc/ops/ride/called/v1" + f'/{rate}')
            # Direct publish the message
            direct_message_publish(messaging_service, topic, body)
            print(f'Published message on {topic}')
            rate += 1
            time.sleep(0.1)
        rate = 1
        time.sleep(1)
except KeyboardInterrupt:
    print('\nDisconnecting Messaging Service')
    messaging_service.disconnect()