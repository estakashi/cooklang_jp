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
