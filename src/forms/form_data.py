"""
Form data structure for RCP Database Editor collections.
"""
from typing import Dict, Any

COLLECTION_TYPE_RACE = "Race"
COLLECTION_TYPE_CLASS = "Class"
COLLECTION_TYPE_PROFESSION = "Profession"
COLLECTION_TYPES = [COLLECTION_TYPE_RACE, COLLECTION_TYPE_CLASS, COLLECTION_TYPE_PROFESSION]

# Example form data structure for each collection type
FORM_DATA: Dict[str, Any] = {
    COLLECTION_TYPE_RACE: {
        # Define fields for Race
    },
    COLLECTION_TYPE_CLASS: {
        # Define fields for Class
    },
    COLLECTION_TYPE_PROFESSION: {
        # Define fields for Profession
    },
}

class FormData:
    def __init__(self, collection_type: str):
        self.collection_type = collection_type
        self.fields: Dict[str, Any] = {}

    def add_field(self, field_name: str, field_value: Any):
        self.fields[field_name] = field_value

    def get_field(self, field_name: str) -> Any:
        return self.fields.get(field_name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collection_type": self.collection_type,
            "fields": self.fields
        }

class RaceFormData(FormData):
    def __init__(self):
        super().__init__("Race")
        self.add_field("name", "")
        self.add_field("description", "")
        self.add_field("iconPath", "")
        self.add_field("racialStats", {})

class ClassFormData(FormData):
    def __init__(self):
        super().__init__("Class")
        self.add_field("name", "")
        self.add_field("description", "")
        self.add_field("classStats", {})

class ProfessionFormData(FormData):
    def __init__(self):
        super().__init__("Profession")
        self.add_field("name", "")
        self.add_field("description", "")
        self.add_field("professionStats", {})