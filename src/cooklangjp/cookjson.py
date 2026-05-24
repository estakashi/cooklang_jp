from dataclasses import dataclass
from typing import List, Optional, Union

# schema
# {
#   "title": "string or null",
#   "metadata": [
#     { "key": "string", "value": "string" }
#   ],
#   "ingredients": [
#     {
#       "name": "string",
#       "amount": {
#         "prefix": "string or null",
#         "number": "number or null",
#         "unit": "string or null"
#       }
#     }
#   ],
#   "steps": [
#     {
#       "type": "note",
#       "lines": ["string"]
#     },
#     {
#       "type": "step",
#       "items": [
#         { "type": "text", "content": "string" },
#         { "type": "ingredient", "name": "milk", "amount": {...} },
#         { "type": "tool", "name": "pan" },
#         { "type": "timer", "number": 10, "unit": "分" }
#       ]
#     }
#   ],
#   "categories": [],
#   "graph_links": []
# }

# Amount
@dataclass
class AmountJSON:
    prefix: Optional[str]
    number: Optional[Union[int, float]]
    unit: Optional[str]

    def to_dict(self):
        return {
            "prefix": self.prefix,
            "number": self.number,
            "unit": self.unit,
        }

# Ingredient
@dataclass
class IngredientJSON:
    name: str
    amount: AmountJSON

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount.to_dict(),
        }

# Metadata
@dataclass
class MetadataJSON:
    key: str
    value: str

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
        }

# Step items
@dataclass
class TextItemJSON:
    type: str
    content: str

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
        }

@dataclass
class IngredientItemJSON:
    type: str
    name: str
    amount: AmountJSON

    def to_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "amount": self.amount.to_dict(),
        }

@dataclass
class ToolItemJSON:
    type: str
    name: str

    def to_dict(self):
        return {
            "type": self.type,
            "name": self.name,
        }

@dataclass
class TimerItemJSON:
    type: str
    number: int
    unit: str

    def to_dict(self):
        return {
            "type": self.type,
            "number": self.number,
            "unit": self.unit,
        }

# Step / Note
@dataclass
class NoteJSON:
    type: str
    lines: List[str]

    def to_dict(self):
        return {
            "type": self.type,
            "lines": self.lines,
        }
        
@dataclass
class StepJSON:
    type: str
    items: List[
        Union[
            TextItemJSON,
            IngredientItemJSON,
            ToolItemJSON,
            TimerItemJSON
            ] 
        ]

    def to_dict(self):
        return {
            "type": self.type,
            "items": [i.to_dict() for i in self.items],
        }
            
    
# Recipe
@dataclass
class RecipeJSON:
    title: Optional[str]
    metadata: List[MetadataJSON]
    ingredients: List[IngredientJSON]
    steps: List[Union[StepJSON, NoteJSON]]
    categories: List[str]
    graph_links: List[dict]

    def to_dict(self):
        return {
            "title": self.title,
            "metadata": [m.to_dict() for m in self.metadata],
            "ingredients": [i.to_dict() for i in self.ingredients],
            "steps": [s.to_dict() for s in self.steps],
            "categories": self.categories,
            "graph_links": self.graph_links,
        }  
    
