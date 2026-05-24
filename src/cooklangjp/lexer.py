import ply.lex as lex

class CookLexer:
    def build(self):
        self.lexer = lex.lex(module=self)
        return self.lexer

    def __call__(self, text):
        self.lexer.input(text)
        self.lexer.begin('LINESTART')
        for tok in self.lexer:
            yield tok

    states = (
        ('LINESTART', 'exclusive'),
        ('BBLOCK', 'exclusive'),
    )

    tokens = (
        'NAME',
        'TOOL',
        'TIMER',
        'TEXT',
        'LBRACE', 'RBRACE',
        'NUMBER',
        'NOTE_LINE',
        'METADATA_LINE',
        'NEWLINE',
        'BLANK',
    )

    # ==========================================
    # 1. 行頭（LINESTART）でしか発動しないルール
    # ==========================================
    def t_LINESTART_METADATA_LINE(self, t):
        r'\>\>[^\n]*'
        t.lexer.begin('INITIAL')
        return t

    def t_LINESTART_NOTE_LINE(self, t):
        r'\>(?!\>)[^\n]*'
        t.lexer.begin('INITIAL')
        return t

    def t_LINESTART_BLANK(self, t):
        r'[ \t]*\n'
        # 空行の場合は、次の行も「行頭」なので LINESTART のまま維持！
        return t


    # ==========================================
    # 2. 通常状態（INITIAL）と行頭（LINESTART）の共有ルール
    # （ハック不要！PLYの公式機能で両方の部屋に同居させます）
    # ==========================================
    def t_INITIAL_LINESTART_NAME(self, t):
        r'@([一-龯ぁ-んァ-ンーA-Za-z0-9（）\(\)・]+?)(?=(を|に|で|へ|と|が|は|から|まで))'
        t.type = 'NAME'
        t.lexer.begin('INITIAL')
        return t

    def t_INITIAL_LINESTART_NAMEFALLBACK(self, t):
        r'@([^{\s\n]+)'
        t.type = 'NAME'
        t.lexer.begin('INITIAL')
        return t


    def t_INITIAL_LINESTART_TOOL(self, t):
        r'\#([一-龯ぁ-んァ-ンーA-Za-z0-9（）\(\)・]+?)(?=(を|に|で|へ|と|が|は|から|まで))'
        t.type = 'TOOL'
        t.lexer.begin('INITIAL')
        return t

    def t_INITIAL_LINESTART_TOOL_FALLBACK(self, t):
        r'\#([^\s\nをにでへとがはからまで]+)'
        t.type = 'TOOL'
        t.lexer.begin('INITIAL')
        return t


    def t_INITIAL_LINESTART_TIMER(self, t):
        r'\~(\d+)(s|sec|m|min|h|hr|秒|分|時間)'
        t.lexer.begin('INITIAL')
        return t

    def t_INITIAL_LINESTART_TEXT(self, t):
        r'([^\n@#~{\[\-]|-(?!-)|\[(?!-))+'
        t.lexer.begin('INITIAL')
        return t

    def t_INITIAL_LINESTART_LBRACE(self, t):
        r'{'
        t.lexer.begin('BBLOCK')
        return t

    def t_INITIAL_LINESTART_NEWLINE(self, t):
        r'\n'
        t.lexer.begin('LINESTART') # 改行が来たら行頭部屋へ！
        return t

    def t_INITIAL_LINESTART_COMMENT_LINE(self, t):
        r'--[^\n]*'
        t.lexer.begin('INITIAL')
        pass

    def t_INITIAL_LINESTART_COMMENT_BLOCK(self, t):
        r'\[\-[\s\S]*?-\]'
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        pass


    # ==========================================
    # 3. 数量部屋（BBLOCK）専用ルール
    # ==========================================
    def t_BBLOCK_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_BBLOCK_TEXT(self, t):
        # 数量部屋のTEXTは、数字と閉じカッコを吸い込まないようにする
        r'[^\d}\n]+'
        return t

    def t_BBLOCK_RBRACE(self, t):
        r'}'
        t.type = 'RBRACE'
        t.lexer.begin('INITIAL')
        return t


    # ==========================================
    # 共通設定・エラーハンドリング
    # ==========================================
    t_ignore = ' \t'
    t_LINESTART_ignore = ' \t'
    t_BBLOCK_ignore = ' \t'

    def t_LINESTART_error(self, t):
        t.lexer.skip(1)

    def t_BBLOCK_error(self, t):
        t.lexer.skip(1)   

    def t_error(self, t):
        t.lexer.skip(1)
