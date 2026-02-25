from pydantic import BaseModel, Field
from typing import Optional, Literal

TransferType = Literal["FULL", "PARTIAL", "CASH", "IN_KIND", "UNKNOWN"]
AccountType = Literal["TFSA", "RRSP", "FHSA", "NON_REGISTERED", "UNKNOWN"]

class TransferFormFields(BaseModel):
    client_full_name: Optional[str] = Field(default=None)
    client_email: Optional[str] = Field(default=None)
    client_phone: Optional[str] = Field(default=None)

    sending_institution: Optional[str] = Field(default=None)
    receiving_institution: Optional[str] = Field(default="Wealthsimple")

    transfer_type: TransferType = Field(default="UNKNOWN")
    account_type: AccountType = Field(default="UNKNOWN")

    account_number_last4: Optional[str] = Field(default=None)
    requested_date: Optional[str] = Field(default=None)  # YYYY-MM-DD
    has_signature: Optional[bool] = Field(default=None)