"""
Pydantic models for data validation in RCP Database Editor.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

class CustomFieldModel(BaseModel):
    key: str
    value: Any

class DocumentModel_Base(BaseModel):
    displayName: str
    tag: str
    full_tag: str
    description: Optional[str] = ""
    iconPath: Optional[str] = ""
    grantedTags: List[str] = Field(default_factory=list)
    customFields: Optional[Dict[str, Any]] = None
    grantStats: Optional[Dict[str, Any]] = None
    grantAbilities: Optional[Dict[str, Any]] = None

    @field_validator('tag', 'displayName')
    @classmethod
    def not_empty(cls, v: Any):
        if not v or not str(v).strip():
            raise ValueError('Field cannot be empty')
        return v

class DocumentModel_Race(DocumentModel_Base):
    meshPath: Optional[str] = None