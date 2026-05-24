import json
from ast import Recipe, Step, Note, Metadata, Text, Ingredient, Tool, Timer, Amount
from cookjson import (
    AmountJSON,
    IngredientJSON,
    IngredientItemJSON,
    ToolItemJSON,
    TimerItemJSON,
    TextItemJSON,
    MetadataJSON,
    StepJSON,
    NoteJSON,
    RecipeJSON,
)



class CookEvaluator:
    def __init__(self, es_client=None, index_name="recipes"):
        self.es = es_client
        self.index = index_name

    # --- AST → 材料一覧 ---
    def extract_ingredients(self, recipe):
        ingredients = {}
        for step in recipe.steps:
            if not isinstance(step, Step):
                continue
            for item in step.items:
                if isinstance(item, Ingredient):
                    amt = item.amount
                    ingredients[item.name] = {
                        "name": item.name,
                        "amount": {
                            "number": amt.number if amt else None,
                            "unit": amt.unit if amt else None,
                            "prefix": amt.prefix if amt else None,
                        }
                    }
        return list(ingredients.values())

    # --- AST → dataclass ---
    def item_to_json(self, item):
        if isinstance(item, Text):
            return TextItemJSON(type="text", content=item.content)
        if isinstance(item, Ingredient):
            amt = item.amount
            return IngredientItemJSON(
               type="ingredient",
               name=item.name,
               amount=AmountJSON(
                   prefix=amt.prefix if amt else None,
                   number=amt.number if amt else None,
                   unit=amt.unit if amt else None,
               )
           )

        if isinstance(item, Tool):
            return ToolItemJSON(
                type="tool",
                name=item.name
            )
        
        if isinstance(item, Timer):
            return TimerItemJSON(
                type="timer",
                number=item.number,
                unit=item.unit
            )
            
        if isinstance(item, Note):
            return NoteJSON(
                type="note",
                lines=item.lines
            )
            
    def step_to_json(self, s):
        if isinstance(s, Step):
            return StepJSON(
                type="step",
                items=[self.item_to_json(i) for i in s.items]
            )
            
        if isinstance(s, Note):
            return NoteJSON(
                type="note",
                lines=s.lines
            )
            
    # --- AST → dict（ES 用スキーマ）---
    def build_recipe_json(self, recipe):
        metadata_list = recipe.metadata or []
        return RecipeJSON(
            title=getattr(recipe, "title", None),
            metadata=[
                MetadataJSON(key=m.key, value=m.value.strip())
                for m in metadata_list
            ],
            ingredients=[
                IngredientJSON(
                    name=ing["name"],
                    amount=AmountJSON(
                        prefix=ing["amount"]["prefix"],
                        number=ing["amount"]["number"],
                        unit=ing["amount"]["unit"],
                    )
                )
                for ing in self.extract_ingredients(recipe)
            ],
            steps=[self.step_to_json(s) for s in recipe.steps],
            categories=[],
            graph_links=[],
        )
        
    # --- dict → JSON（外部出力）---
    def to_json(self, recipe):
        data = self.build_recipe_json(recipe)
        return json.dumps(data.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)

    # --- ES 登録 ---
    def index_to_es(self, recipe, doc_id=None):
        if self.es is None:
            raise ValueError("Elasticsearch client is not set")

        body = self.build_recipe_json(recipe).to_dict()
        return self.es.index(index=self.index, id=doc_id, document=body)

