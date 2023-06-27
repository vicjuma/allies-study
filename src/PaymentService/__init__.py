from typing import Iterable
from intasend import  APIService
from dotenv import load_dotenv
import os
from typing import (
        Dict,
        Any
    )

import threading

load_dotenv(
    os.path.join(
        os.path.abspath(
            os.path.dirname(
                __file__
            )
        ),
        "payment.env"
    )
)

TOKEN = os.environ.get("API_TOKEN")
PUBLISHABLE_KEY = os.environ.get("PUBLISHABLE_KEY")

class MpesaHandler:
    def __init__(self):
        self.service = APIService(
                token = TOKEN, 
                publishable_key = PUBLISHABLE_KEY,
                test=True
            )
    
    def requestPayment(self, user):
        self.response = self.service.collect.checkout(user)
        return self.response

    def promptPayment(self, user: Dict[str, Any]):
        return self.service.collect.mpesa_stk_push(**user)
    
    def disburseFunds(self, clients: Iterable[Dict[str, Any]]):
        self.response = self.service.transfer.mpesa(currency='KES', transactions=transactions)

    def checkTransactionStatus(self, invoice_id):
        self.response = self.service.collect.status(invoice_id)
        return self.response


