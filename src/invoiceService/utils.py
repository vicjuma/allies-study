from src.utils import DatabaseTableMixin
from fastapi import (
        status,
        HTTPException
)
from src.models.models import (
    Invoice,
    Transaction,
    Tasks
)
import uuid
from typing import (
    Dict,
    Any,
    List,
    Iterable
)
from fastapi_restful.api_model import APIMessage
from src.PaymentService import MpesaHandler
import re

class InvoiceHandler:
    def __init__(self):
        self.invoice_handler = DatabaseTableMixin(Invoice)
        self.payment_handler = MpesaHandler()
        self.transaction_handler = DatabaseTableMixin(Transaction)
        self.task_handler = DatabaseTableMixin(Tasks)

    def createInvoice(self, payload, user):
        # payload['id'] = uuid.uuid4().hex
        payload["user_id"] = user['id']
        self.invoice_handler.__create_item__(payload)
        return payload
        
    def getInvoices(self, user: Dict[str, Any]):
        if user["is_admin"] == True:
            return {
                    "invoices": [
                        item.to_json() for item in iter(
                            self.invoice_handler
                        )
                    ]
                }
        raise HTTPException(
                detail="Authorization Failure",
                status_code=HTTP_403_FORBIDDEN
            )

    def getByUserid(self, user: Dict[str, Any]):
        return {
            "invoices": [
                item.to_json() for item in self.invoice_handler.filterDb(
                    **{
                        "user_id": user['id']
                    }
                ).all()
            ]
        }

    def getInvoice(self, invoice_id: str, user: Dict[str, Any]):
        # only the owner of the transaction and the Admin can view the transaction | invoice
        invoice = self.invoice_handler[invoice_id]
        if user['is_admin'] or user['id'] == invoice.user_id:
            return invoice.to_json()
        raise HTTPException(
                detail="UnAuthorized access",
                status_code=status.HTTP_403_FORBIDDEN
            )

    def deleteInvoice(self, invoice_id: str, user: Dict[str, Any]):
        if user['is_admin'] == True:
            if self.invoice_handler[invoice_id]:
                del self.invoice_handler[invoice_id]
                return APIMessage(
                        detail="Invoice deletion success",
                        status_code=status.HTTP_200_OK
                    )
            raise HTTPException(
                    detail="Invoice not Found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        raise HTTPException(
                detail="Unauthorized access",
                status=status.HTTP_403_FORBIDDEN
            )

    def patchInvoice(self, payload: Dict[str, Any], user: Dict[str, Any]):
        invoice = self.invoice_handler[payload["id"]]
        if user['is_admin'] == True or invoice.user_id == user['id']:
            # execute patch Query
            return self.invoice_handler.patchDb(payload)
        raise HTTPException(
                detail="Unauthorized Access",
                status_code=status.HTTP_403_FORBIDDEN
            )

    def payInvoice(self, invoice_number: str, payload: Dict[str, Any], user: Dict[str, Any]):
        # Check if the Invoice Number exixts
        invoice = self.invoice_handler[invoice_number]

        if invoice:
            # Get the payment Details to be processed from the invoice

            if invoice.payment_status == "unpaid":
                pay_det = {
                        "email": payload['email'],
                        "phone_number": payload['phone_number'],
                        "amount": invoice.amount,
                        "narrative": payload['comment']
                    }
                
                response = self.payment_handler.promptPayment(pay_det)

                # Get the invoice_id
                order_id = response["invoice"]["invoice_id"]
                
                # Check for the Status
                while True:
                    status = self.payment_handler.checkTransactionStatus(order_id)
                   
                    if status['invoice']['state'] == "COMPLETE":
                        # Update Invoice
                        update_payload = {
                                "id": invoice.id,
                                "payment_status": "paid"
                            }

                        self.task_handler.patchDb(update_payload)

                        self.invoice_handler.patchDb(update_payload)
                        

                        # Update the task status

                        task_update = {
                                    "id": invoice.task_id,
                                    "payment_status" : "paid"
                                }


                        transact_dict = {
                            # "id": uuid.uuid4().hex,
                            "code": response['id'],
                            "invoice_id": invoice.id
                        }

                        # Add to transaction_database if complete
                        
                        self.transaction_handler.__create_item__(transact_dict)

                        # Return payment Status of transaction
                        return transact_dict
                    elif status["invoice"]["state"] == "PROCESSING":
                        continue
            else:
                return {
                        "Message": "Invoice is already paid"
                    }
     
        raise HTTPException(
                detail="Invoice not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def massPayment(self, workers: Dict[str, List[Dict[str, Any]]], user: Dict[str, Any]):
        if user['is_admin'] == True:
            self.payment_handler.disburseFunds(workers['details'])
        raise HTTPException(
                detail="Unauthorized access",
                status_code=status.HTTP_403_FORBIDDEN
            )
