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
このリポジトリをクローンして、開発モードでインストールします。
``` bash
git clone https://github.com/estakashi/cooklang_jp
cd cooklang_jp
pip install -e .
```
これで `cooklangjp` パッケージが利用可能になります。

## テスト
git cloneしたディレクトリでpytestを叩けば動きます。
``` bash
cd cooklang_jp
pytest
```
