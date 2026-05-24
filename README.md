# cooklang_jp
Python PLYで日本語対応cooklangを作ってみました。
cooklangで書いたレシピファイル.cookを用意して
``` python
from cooklangjp.executor import CookExecutor

ex = CookExecutor()
recipe = ex.execute("test.cook")
recipe
```
のようにすれば、dictが返ってくるはずです。

## インストール
``` bash
git clone https://github.com/estakashi/cooklang_jp
cd cooklang_jp
pip install -e .
```

## テスト
git cloneしたディレクトリでpytestを叩けば動きます。
