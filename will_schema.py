from pydantic import BaseModel
from typing import Optional, List

class Asset(BaseModel):
    asset_type: str
    description: str
    identifier: Optional[str] = None
    estimated_value: Optional[float] = None

class Beneficiary(BaseModel):
    name: str
    relationship: str
    age: int
    allocation: str
    is_minor: bool = False

class WillData(BaseModel):
    testator_name: Optional[str] = None
    testator_age: Optional[int] = None
    testator_address: Optional[str] = None
    religion: Optional[str] = None
    family_type: Optional[str] = None
    assets: List[Asset] = []
    beneficiaries: List[Beneficiary] = []
    executor_name: Optional[str] = None
    executor_relationship: Optional[str] = None
    witnesses: List[str] = []
    minor_guardian: Optional[str] = None
    residuary_beneficiary: Optional[str] = None
