import json
import pytest
from cooklangjp.executor import CookExecutor
from cooklangjp.ast import Recipe

def test_load_file(tmp_path):
    p = tmp_path / "sample.cook"
    p.write_text("Hello", encoding="utf-8")

    exe = CookExecutor()
    assert exe.load_file(str(p)) == "Hello"

def test_load_file_not_found():
    exe = CookExecutor()
    with pytest.raises(FileNotFoundError):
        exe.load_file("no_such_file.cook")

def test_parse_file_to_ast_basic():
    text = """
# Title
Mix @sugar{10g}
Boil @water{100ml}
""".strip()

    exe = CookExecutor()
    ast = exe.parse_file_to_ast(text)

    # AST の基本構造を確認
    assert isinstance(ast, Recipe)
    assert len(ast.steps) == 3

    # ステップ内容の確認（属性名は実装に合わせて調整）
    assert ast.steps[1].items[0].content == "Mix"
    assert ast.steps[2].items[0].content == "Boil"

def test_execute_to_json(tmp_path):
    p = tmp_path / "recipe.cook"
    p.write_text(
        "# Tea\nHeat @water{200ml}\nAdd @tea{5g}",
        encoding="utf-8"
    )

    exe = CookExecutor()
    json_text = exe.execute_to_json(str(p))
    data = json.loads(json_text)

    # JSON の基本構造を確認
    assert "title" in data
    assert "steps" in data
    assert len(data["steps"]) == 3

    assert data["steps"][1]["items"][0]["content"] == "Heat"
    assert data["steps"][2]["items"][0]["content"] == "Add"
