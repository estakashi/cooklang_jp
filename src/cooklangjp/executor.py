import json
import os
from cookjson import RecipeJSON
from parser import CookParser
from evaluator import CookEvaluator
# 合成用に AST クラス（Recipe）をインポート
from ast import Recipe 

class CookExecutor:
    def __init__(self, parser=None, evaluator=None):
        self.parser = parser or CookParser().build()
        self.evaluator = evaluator or CookEvaluator()

    def load_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"ファイルが見つかりません: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def parse_file_to_ast(self, text: str):
        """
        複数行のテキストを1行ずつ安全にパースし、1つの Recipe AST に統合します。
        """
        combined_steps = []
        final_recipe = None

        # 改行で分割し、空行を除外して1行ずつ処理
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        for line in lines:
            # PLYのルールに合わせて、末尾に改行コードを付与してパース
            ast_line = self.parser.parse(line + "\n")
            
            if ast_line is None:
                raise ValueError(f"次の行のパースに失敗しました: '{line}'")
            
            # 各行のパース結果からステップ（Step や Note）を回収
            if hasattr(ast_line, 'steps'):
                combined_steps.extend(ast_line.steps)
                # 最初の行などからベースとなる Recipe 構造（タイトルやメタデータ用）をキープ
                if final_recipe is None:
                    final_recipe = ast_line
            else:
                # ast_line 自体が Step や Note 単体の場合
                combined_steps.append(ast_line)

        if final_recipe is None:
            raise ValueError("有効なレシピデータが解析できませんでした。")

        # 集めたすべてのステップを最終的な Recipe AST に上書きセット
        final_recipe.steps = combined_steps
        return final_recipe

    def build(self, ast):
        if ast is None:
            raise ValueError("ASTがNoneです。")
        return self.evaluator.build_recipe_json(ast)

    def execute(self, path: str) -> RecipeJSON:
        text = self.load_file(path)
        # 1行ずつパースする新しいメソッドを呼び出す
        ast = self.parse_file_to_ast(text)
        return self.build(ast)

    def execute_to_json(self, path: str) -> str:
        recipe = self.execute(path)
        return json.dumps(recipe.to_dict(), ensure_ascii=False, indent=2)
