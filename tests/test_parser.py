import pytest
from cooklangjp.parser import CookParser
from cooklangjp.ast import Recipe, Note, Metadata, Step, Text, Tool, Timer, Ingredient, Amount

@pytest.fixture(scope="module")
def parser():
    P = CookParser()
    return P.build()

def test_ast_parse_simple(parser):
    ast = parser.parse("@egg\n")
    assert isinstance(ast, Recipe)
    assert len(ast.steps) == 1

    step = ast.steps[0]
    assert isinstance(step, Step)
    assert len(step.items) == 1

    ingredient = step.items[0]
    assert isinstance(ingredient, Ingredient)
    assert ingredient.name == "egg"

    assert repr(ingredient.amount) == "None"
    
def test_ingredient_amount_number_unit(parser):
    ast = parser.parse("Add @milk{200ml}\n")
    assert isinstance(ast, Recipe)
    assert len(ast.steps) == 1

    step = ast.steps[0]
    assert isinstance(step, Step)
    assert len(step.items) == 2

    text = step.items[0]
    assert isinstance(text, Text)
    assert repr(text) == "Text(Add)"

    ingredient = step.items[1]
    assert isinstance(ingredient, Ingredient)
    assert ingredient.name == "milk"

    assert repr(ingredient.amount) == "Amount(None, 200, ml)"

def test_ingredient_amount_text_number_text(parser):
    ast = parser.parse("@egg{たまご1個}\n")
    assert isinstance(ast, Recipe)
    assert len(ast.steps) == 1

    step = ast.steps[0]
    assert isinstance(step, Step)
    assert len(step.items) == 1

    ingredient = step.items[0]
    assert isinstance(ingredient, Ingredient)
    assert ingredient.name == "egg"

    assert repr(ingredient.amount) == "Amount(たまご, 1, 個)"

def test_ingredient_amount_percent(parser):
    ast = parser.parse("@milk{200%ml}\n")
    assert isinstance(ast, Recipe)
    assert len(ast.steps) == 1

    step = ast.steps[0]
    assert isinstance(step, Step)
    assert len(step.items) == 1

    ingredient = step.items[0]
    assert isinstance(ingredient, Ingredient)
    assert ingredient.name == "milk"

    assert repr(ingredient.amount) == "Amount(None, 200, ml)"

def test_step_multiple_items(parser):
    ast = parser.parse("Add @milk{200ml} and @sugar{10g}\n")
    assert isinstance(ast, Recipe)
    assert len(ast.steps) == 1

    step = ast.steps[0]
    assert isinstance(step, Step)
    assert len(step.items) == 4

    text = step.items[0]
    assert isinstance(text, Text)
    assert repr(text) == "Text(Add)"

    ingredient = step.items[1]
    assert isinstance(ingredient, Ingredient)
    assert ingredient.name == "milk"

    assert repr(ingredient.amount) == "Amount(None, 200, ml)"

    text = step.items[2]
    assert isinstance(text, Text)
    assert repr(text) == "Text(and)"

    ingredient = step.items[3]
    assert isinstance(ingredient, Ingredient)
    assert ingredient.name == "sugar"

    assert repr(ingredient.amount) == "Amount(None, 10, g)"

def test_tool_parse(parser):
    ast = parser.parse("卵を#[鍋]で温める\n")

    step = ast.steps[0]
    assert isinstance(step.items[1], Tool)
    assert step.items[1].name == "鍋"

def test_timer_parse(parser):
    ast = parser.parse("~10分待つ\n")

    step = ast.steps[0]
    timer = step.items[0]

    assert isinstance(timer, Timer)
    assert timer.number == 10
    assert timer.unit == "分"


def test_parser_metadata_note_step_mix(parser):
    ast = parser.parse(
        ">> servings: 2\n"
        "> これはメモです\n"
        "> 二行目のメモ\n"
        "\n"
        "Add @milk{200ml}\n"
    )

    # --- metadata ---
    assert len(ast.metadata) == 1
    meta = ast.metadata[0]
    assert meta.key == "servings"
    assert meta.value == "2"

    # --- note ---
    assert len(ast.steps) == 2  # note と step が並ぶ
    note = ast.steps[0]
    assert isinstance(note, Note)
    assert note.lines == ["これはメモです", "二行目のメモ"]

    # --- step ---
    step = ast.steps[1]
    assert isinstance(step, Step)
    assert len(step.items) == 2

    text = step.items[0]
    assert isinstance(text, Text)
    assert text.content == "Add"

    ing = step.items[1]
    assert isinstance(ing, Ingredient)
    assert ing.name == "milk"
    assert ing.amount.number == 200
    assert ing.amount.unit == "ml"
