# cooklang_jp
Python PLYで日本語対応cooklangを作ってみました。
cooklangで書いたレシピファイル.cook
``` text
>> title: ポトフ
>> servings: 2

@じゃがいも{2個}を切る
@にんじん{1本}を切る
#鍋で炒める
~10分煮る
```
を用意して
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
