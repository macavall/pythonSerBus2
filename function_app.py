import azure.functions as func
import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from typing import Optional
import os

sbconnstring = os.environ.get("sbconnstring")
sbtopicname = os.environ.get("sbtopicname")

# Service Bus Handler class with static client
class ServiceBusHandler:
    _client: Optional[ServiceBusClient] = None
    _connection_string = sbconnstring   # Replace with your connection string
    _topic_name = sbtopicname  # Replace with your topic name

    @classmethod
    def get_client(cls) -> ServiceBusClient:
        if cls._client is None:
            cls._client = ServiceBusClient.from_connection_string(cls._connection_string)
        return cls._client

    @classmethod
    async def send_message(cls, message_content: str):
        client = cls.get_client()
        try:
            with client.get_topic_sender(topic_name=cls._topic_name) as sender:
                message = ServiceBusMessage(message_content)
                sender.send_messages(message)
                logging.info(f"Sent message to Service Bus: {message_content}")
        except Exception as e:
            logging.error(f"Error sending message to Service Bus: {str(e)}")

app = func.FunctionApp()

@app.route(route="http1", auth_level=func.AuthLevel.ANONYMOUS)
async def http1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        # Send message to Service Bus topic
        message = f"User greeting: Hello, {name}"
        await ServiceBusHandler.send_message(message)
        
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully. Message sent to Service Bus."
        )
    else:
        # Send default message to Service Bus topic
        message = "Anonymous user accessed the function"
        await ServiceBusHandler.send_message(message)
        
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response. Message sent to Service Bus.",
            status_code=200
        )

# @app.route(route="http1", auth_level=func.AuthLevel.ANONYMOUS)
# def http1(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )