import os
from dotenv import load_dotenv
from signalwire.rest import RestClient

# Load environment variables from .env
load_dotenv()

SIGNALWIRE_SPACE = os.getenv("SIGNALWIRE_SPACE")
SIGNALWIRE_PROJECT_ID = os.getenv("SIGNALWIRE_PROJECT_ID")
SIGNALWIRE_API_TOKEN = os.getenv("SIGNALWIRE_API_TOKEN")


def functionauthenticate():

    # Validate credentials
    if not all([
        SIGNALWIRE_SPACE,
        SIGNALWIRE_PROJECT_ID,
        SIGNALWIRE_API_TOKEN
    ]):
        return {
            "success": False,
            "message": "SignalWire credentials are missing."
        }

    try:
        # Initialize SignalWire client
        client = RestClient(
            project=SIGNALWIRE_PROJECT_ID,
            token=SIGNALWIRE_API_TOKEN,
            host=SIGNALWIRE_SPACE
        )

        return {
            "success": True,
            "message": "SignalWire client initialized successfully.",
            "client": client
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }
    
if __name__ == "__main__":
    result = functionauthenticate()
    print(result)