import os
from dotenv import load_dotenv

load_dotenv()

def contact_info(request):
    return {
        "email": os.getenv("EMAIL"),
        "phone": os.getenv("PHONE"),
        "address": os.getenv("ADDRESS"),
    }