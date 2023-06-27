from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from src.invoiceService.utils import InvoiceHandler
from typing import (
   Dict,
   Any
)
from fastapi import (
    status,
    Request
)
from src.models.schema import (
    InvoiceSchema,
    InvoicesSchema,
    CreateInvoiceSchema,
    PaymentSchema,
    MassPayDisburseSchema
)

invoice_router = InferringRouter()

@cbv(invoice_router)
class InvoiceService:
    def __init__(self):
        self.invoice_handler = InvoiceHandler()
    
    @invoice_router.get("/invoices", status_code=status.HTTP_200_OK, response_model=InvoicesSchema)
    def getInvoices(self):
        return self.invoice_handler.getInvoices()

    @invoice_router.post("/invoice", status_code=status.HTTP_201_CREATED, response_model=InvoiceSchema)
    async def createInvoice(self, request: Request, payload: CreateInvoiceSchema):
        return self.invoice_handler.createInvoices(payload.dict())

    @invoice_router.get("/invoice/{invoice_id}", status_code=status.HTTP_200_OK, response_model=InvoiceSchema)
    def getInvoice(self, invoice_id: str):
        return self.invoice_handler.getInvoice(invoice_id)

    @invoice_router.delete("/invoice/{invoice_id}")
    def deleteInvoice(self, invoice_id: str):
        return self.invoice_handler.deleteInvoice(invoice_id)

    @invoice_router.patch("/invoice")
    async def patchInvoice(self, payload: Request):
        return self.invoice_handler.patchInvoice(await payload.json())

    @invoice_router.post("/pay/invoice/{invoice_id}")
    async def payInvoice(self, request: Request, invoice_id:str, payload: PaymentSchema):
        # Request Payment from User
        return self.invoice_handler.payInvoice(invoice_id, payload.dict())
    
    @invoice_router.post("/disburse/funds/users")
    async def disburseFunds(self, request: Request, payload: MassPayDisburseSchema):
        return self.invoice_handler.massPayment(payload.dict())

    @invoice_router.get("/my/invoices", status_code=status.HTTP_200_OK, response_model=InvoicesSchema)
    def getMyInvoices(self):
        return self.invoice_handler.getByUserid()
