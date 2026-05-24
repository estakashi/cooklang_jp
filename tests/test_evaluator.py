import pytest

from cooklangjp.parser import CookParser
from cooklangjp.evaluator import CookEvaluator
from cooklangjp.cookjson import (
    AmountJSON,
    IngredientJSON,
    IngredientItemJSON,
    ToolItemJSON,
    TimerItemJSON,
    MetadataJSON,
    StepJSON,
    NoteJSON,
    RecipeJSON,
)

# @pytest.fixture
# def mock_es(mocker):
#     # ESクラスをモック化
#     from elasticsearch import Elasticsearch
#     mock = mocker.patch("cookeval.Elasticsearch", autospec=True)
#     instance = mock.return_value
#     instance.index.return_value = {"result": "created"}
#     return instance

# def test_index_to_es(mock_es):
#     parser = CookParser()
#     ast = parser.parser.parse("@milk{200ml}\n")

#     ev = Evaluator(es_client=mock_es)
#     result = ev.index_to_es(ast, doc_id="abc")

#     assert result["result"] == "created"
#     mock_es.index.assert_called_once()

@pytest.fixture
def mock_es(mocker):
    es = mocker.MagicMock()
    es.index.return_value = {"result": "created"}
    return es

@pytest.fixture(scope="module")
def parser():
    P = CookParser()
    return P.build()

@pytest.fixture
def evaluator(mock_es):
    return CookEvaluator(es_client=mock_es)
    
def test_index_to_es(parser, evaluator):
    ast = parser.parse("@milk{200ml}\n")

    result = evaluator.index_to_es(ast, doc_id="abc")

    assert result["result"] == "created"
    evaluator.es.index.assert_called_once()

def test_eval_tool_and_timer(parser, evaluator):
    ast = parser.parse("Add @milk{200ml}を#[pan]で~10分温める\n")

    data = evaluator.build_recipe_json(ast)

    items = data.steps[0].items

    assert isinstance(items[1], IngredientItemJSON)
    assert isinstance(items[3], ToolItemJSON)
    assert items[3].name == "pan"
    assert items[5].type == "timer"
    assert items[5].number == 10
    assert items[5].unit == "分"

def test_eval_metadata_output(parser, evaluator):
    ast = parser.parse(">> servings: 2\n@egg\n")
    data = evaluator.build_recipe_json(ast)

    assert data.metadata == [MetadataJSON(key="servings", value="2")]
    

def test_eval_note_output(parser, evaluator):
    ast = parser.parse(
        "> line1\n"
        "> line2\n"
        "\n"
    )
    data = evaluator.build_recipe_json(ast)

    assert isinstance(data.steps[0], NoteJSON)
    assert data.steps[0].lines == ["line1", "line2"]

def test_eval_amount_prefix(parser, evaluator):
    ast = parser.parse("@egg{たまご1個}\n")

    data = evaluator.build_recipe_json(ast)

    ing = data.ingredients[0]
    assert ing.amount.prefix == "たまご"
    assert ing.amount.number == 1
    assert ing.amount.unit == "個"

def test_eval_multiple_steps(parser, evaluator):
    ast = parser.parse("@egg\n@milk\n")

    data = evaluator.build_recipe_json(ast)

    assert len(data.steps) == 2
    assert data.steps[0].items[0].name == "egg"
    assert data.steps[1].items[0].name == "milk"

def test_eval_mixed_items_order(parser, evaluator):
    ast = parser.parse("Add @milk{200ml} #[pan] ~10分\n")

    data = evaluator.build_recipe_json(ast)
    items = data.steps[0].items

    assert [i.type for i in items] == ["text", "ingredient", "tool", "timer"]
