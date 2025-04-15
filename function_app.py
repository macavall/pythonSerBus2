import azure.functions as func
import logging
from azure.servicebus.aio import ServiceBusClient, ServiceBusMessage
import os
import asyncio

# Load environment variables
sbconnstring = os.environ.get("sbconnstring")
sbtopicname = os.environ.get("sbtopicname")

# Initialize the async ServiceBusClient at module level
service_bus_client = ServiceBusClient.from_connection_string(sbconnstring)

# Service Bus Handler class with async operations
class ServiceBusHandler:
    _topic_name = sbtopicname  # Topic name from environment

    @classmethod
    async def send_message(cls, message_content: str):
        try:
            async with service_bus_client.get_topic_sender(topic_name=cls._topic_name) as sender:
                message = ServiceBusMessage(message_content)
                await sender.send_messages(message)
                logging.info(f"Sent message to Service Bus: {message_content}")
        except Exception as e:
            logging.error(f"Error sending message to Service Bus: {str(e)}")
            raise  # Re-raise to allow caller to handle

# Create the Function App
app = func.FunctionApp()

@app.route(route="http1", auth_level=func.AuthLevel.ANONYMOUS)
async def http1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Send message to Service Bus topic asynchronously
        message = "test"
        await ServiceBusHandler.send_message(message)
        
        return func.HttpResponse(
            f"Testing message to Service Bus Topic: {message}",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            "An error occurred while processing the request.",
            status_code=500
        )