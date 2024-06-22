from datetime import datetime
from enum import Enum
from typing import List

from beanie import Document, init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ValidationError, ConfigDict


class DeStatus(str, Enum):
    READY = "READY"
    DONE = "DONE"


class ImageStatus(str, Enum):
    DONE = "OCR_DONE"
    REVIEWED = "REVIEWED"
    REJECTED = "REJECTED"
    GARBAGE = "GARBAGE"


class AttachmentInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    attachment_type: str = Field(alias="attachmentType")
    attachment_name: str = Field(alias="attachmentName")
    attachment_create: str = Field(alias="attachmentCreate")
    attachment_len: str = Field(alias="attachmentLen")
    attachment: str
    class_type: str = Field(alias="_class")


class AssignInfo(BaseModel):
    assign_at: datetime
    uuid: str


class AccidentInfo(BaseModel):
    accno: str
    mrtg: str
    ordrank: str


class Icd(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    class_type: str = Field(alias="_class")
    accident_info: AccidentInfo
    api_account: str
    assign: AssignInfo | None = Field(default=None)
    # attachments: List[dict] = Field(default_factory=list)
    attachments: List[AttachmentInfo] = Field(default_factory=list)
    create_at: datetime = Field(default_factory=datetime.now)
    image_status: ImageStatus
    ins_type: str
    raw_logs: List[dict] | None = Field(default=None)
    request_by: str
    de_status: DeStatus = Field(alias="status")
    vin_code: str
    request_by: str | None = Field(default="")
    request_id: str | None = Field(default="")
    brand: str | None = Field(default="")
    type: int | None = Field(default=None)

    class Settings:
        name = "icd_log"
        validate_on_save = True


async def init():
    # Beanie uses Motor async client under the hood
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    # collection = client.amass_logs.icd_log

    # Initialize beanie with the Product document class
    await init_beanie(database=client.amass_logs, document_models=[Icd])

    try:
        attachment_info = AttachmentInfo(
            attachment_type="PDF",
            attachment_name="typing_A_00218719881_202306738855_001_001.pdf",
            attachment_create="2024-02-01",
            attachment_len="11111",
            attachment="https://amassdev.blob.core.windows.net/api/icd%2F20240403%2F1712126019381_2066.PDF",
            _class="kr.co.amass.api.domain.icd.controller.dto.IcdRequest$IcdAttachment",
        )
        icd = Icd(
            class_type="TEST",
            accident_info=AccidentInfo(accno="TEST", mrtg="001", ordrank="002"),
            api_account="admin",
            attachments=[attachment_info],
            image_status=ImageStatus.DONE,
            ins_type="DBINS",
            de_status=DeStatus.READY,
            vin_code="WAUZZZ8K6DN014133",
            request_by="ADMIN",
            brand="BMW",
            type=26001,
        )
        await icd.insert()
        print("ICD inserted: ", icd)
    except ValidationError as e:
        print(e.json())
    # Beanie documents work just like pydantic models

    # You can find documents with pythonic syntax
    # icd_f = await collection.find_one(PydanticObjectId("661e17f14f1d385e7ceef222"))
    # print("ICD find : ", icd_f)
    icd_u = await Icd.find_one(Icd.id == PydanticObjectId("661e17f14f1d385e7ceef222"))
    if icd_u:  # None이 아닌 경우에만 set 메서드 호출
        await icd_u.set({Icd.image_status: ImageStatus.REVIEWED})
        print("ICD updated: ", icd_u)
