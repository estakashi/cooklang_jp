import pytest
from cooklangjp.lexer import CookLexer

@pytest.fixture(scope="module")
def lexer():
    L = CookLexer()
    L.build()
    return L

def test_lex_simple_ingredient(lexer):

    tokens = list(lexer("Add @milk{200%ml}を#[pan]で~10分温める。\n--テスト"))

    assert tokens[0].type == "TEXT"
    assert tokens[0].value == "Add "

    assert tokens[1].type == "NAME"
    assert tokens[1].value == '@milk'

    assert tokens[2].type == 'LBRACE'
    assert tokens[3].type == 'NUMBER'
    assert tokens[3].value == 200
    assert tokens[4].type == 'TEXT'
    assert tokens[4].value == '%ml'
    assert tokens[5].type == 'RBRACE'
    assert tokens[6].type == 'TEXT'
    assert tokens[7].type == 'TOOL'
    assert tokens[7].value == '#[pan]'
    assert tokens[8].type == 'TEXT'
    assert tokens[9].type == 'TIMER'
    assert tokens[9].value == '~10分'
    assert tokens[10].type == 'TEXT'
    assert tokens[11].type == 'NEWLINE'

def test_tool_multiple(lexer):
    tokens = list(lexer("使う #[pan] と #[spoon] を準備する\n"))

    types = [t.type for t in tokens]
    assert types.count("TOOL") == 2

@pytest.mark.parametrize("text", [
    "~10s", "~10sec", "~10m", "~10min", "~1h", "~2hr", "~10秒", "~5分", "~1時間"
])
def test_timer_units(text, lexer):
    tok = list(lexer(text))[0]
    assert tok.type == "TIMER"

def test_note_multiline(lexer):
    tokens = list(lexer("> first\n> second\n\n"))
    assert tokens[0].type == "NOTE_LINE"
    assert tokens[1].type == "NEWLINE"
    assert tokens[2].type == "NOTE_LINE"

def test_metadata_line(lexer):
    tokens = list(lexer(">> servings: 2\n"))
    assert tokens[0].type == "METADATA_LINE"

def test_comment_line_and_block(lexer):
    tokens = list(lexer("text -- comment\n[- block -]text\n"))
    values = [t.value for t in tokens if t.type == "TEXT"]

    assert values == ["text ", "text"]

def test_amount_text(lexer):
    tokens = list(lexer("@milk{200%ml}\n"))
    assert tokens[0].type == "NAME"
    assert tokens[2].type == "NUMBER"
    assert tokens[3].type == "TEXT"   # %ml

def test_text_name_boundary(lexer):
    tokens = list(lexer("Add @sugar and @milk\n"))
    types = [t.type for t in tokens]

    assert types == ["TEXT", "NAME", "TEXT", "NAME", "NEWLINE"]

def test_blank_line(lexer):
    tokens = list(lexer("\n\n"))
    assert len(tokens) == 2
    assert tokens[0].type == "BLANK"
    

def test_blank_does_not_consume_note(lexer):
    tokens = list(lexer(">> servings: 2\n> note\n\n"))
    types = [t.type for t in tokens]

    # BLANK は note の後の空行だけに出る
    assert types == [
        "METADATA_LINE", "NEWLINE",
        "NOTE_LINE", "NEWLINE",
        "BLANK"
    ]
def test_lexer_metadata_and_note_debug(lexer):
    text = (
        ">> servings: 2\n"
        "> これはメモです\n"
        "> 二行目のメモ\n"
        "\n"
        "Add @milk{200ml}\n"
    )

    tokens = [(tok.type, tok.value) for tok in lexer(text)]
    print(tokens)

    # 期待されるトークン列
    expected = [
        ("METADATA_LINE", ">> servings: 2"),
        ("NEWLINE", "\n"),
        ("NOTE_LINE", "> これはメモです"),
        ("NEWLINE", "\n"),
        ("NOTE_LINE", "> 二行目のメモ"),
        ("NEWLINE", "\n"),
        ("BLANK", "\n"),
        ("TEXT", "Add "),
        ("NAME", "@milk"),
        ("LBRACE", "{"),
        ("NUMBER", 200),
        ("TEXT", "ml"),
        ("RBRACE", "}"),
        ("NEWLINE", "\n"),
    ]

    assert tokens == expected


def test_metadata_followed_by_newline(lexer):
    tokens = list(lexer(">> servings: 2\n> note\n"))
    types = [t.type for t in tokens]

    assert types[0] == "METADATA_LINE"
    assert types[1] == "NEWLINE"   # BLANK になってはいけない

def test_linestart_to_initial_regression(lexer):
    # 行頭からいきなり通常文字、または特殊記号が始まるケース
    # 無限ループする実装の場合、このテストを実行した時点で Jupyter や pytest がフリーズします。
    text = ">> title: test\n@milk を足す"
    
    tokens = list(lexer(text))
    
    # フリーズせずにここまで到達し、かつ適切なトークンに分解されていることをアサート
    assert len(tokens) > 0
    assert tokens[-3].type == "NEWLINE" # または適切な行末処理

def test_text_with_numbers_outside_brace(lexer):
    # {} の外にある数字は、NUMBERではなくTEXTの一部として一塊になってほしい
    tokens = list(lexer("フライパンで3分炒める\n"))
    
    types = [t.type for t in tokens]
    assert "NUMBER" not in types  # NUMBERに化けていないこと
    
    # 強力になったTEXTは、分断されずに1つのトークンになります
    assert tokens[0].type == "TEXT"
    assert tokens[0].value == "フライパンで3分炒める"

def test_text_with_allowed_symbols(lexer):
    # 行頭ではない場所にある「>」や「-」は、ただの文字列としてTEXTに含まれてほしい
    tokens = list(lexer("A -> Bの順に混ぜる（重さは>10g）\n"))
    
    # 完全に一繋ぎのTEXTとして抽出できているかテスト
    assert tokens[0].type == "TEXT"
    assert tokens[0].value == "A -> Bの順に混ぜる（重さは>10g）"

def test_multiline_comment_block(lexer):
    # 複数行にわたるブロックコメントが、前後の改行を壊さずに正しく無視されるか
    text = "一行目\n[- 複数行の\nコメントです -]\n二行目\n"
    tokens = list(lexer(text))
    
    # コメント部分（と、その中にある改行）は完全に消え去り、
    # 「一行目」「NEWLINE」「二行目」「NEWLINE」となるのが理想
    types = [t.type for t in tokens]
    assert types == ["TEXT", "NEWLINE", "NEWLINE", "TEXT", "NEWLINE"]

def test_name_particle_boundary_basic(lexer):
    tokens = list(lexer("@卵を割る\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@卵"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "を割る"
    assert tokens[2].type == "NEWLINE"

@pytest.mark.parametrize("particle", ["を", "に", "で", "へ", "と", "が", "は", "から", "まで"])
def test_name_particle_variants(particle, lexer):
    text = f"@玉ねぎ{particle}炒める\n"
    tokens = list(lexer(text))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@玉ねぎ"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == particle + "炒める"

def test_name_particle_vs_fallback(lexer):
    # 助詞あり → 助詞境界 NAME
    tokens = list(lexer("@牛肉を焼く\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@牛肉"

    # 助詞なし → fallback NAME
    tokens = list(lexer("@牛肉{200g}\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@牛肉"

def test_name_not_eaten_by_text(lexer):
    tokens = list(lexer("Add @milkを混ぜる\n"))
    assert tokens[1].type == "NAME"
    assert tokens[1].value == "@milk"
    assert tokens[2].type == "TEXT"
    assert tokens[2].value == "を混ぜる"

def test_name_particle_english(lexer):
    tokens = list(lexer("@sugarを加える\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@sugar"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "を加える"

def test_name_particle_with_parens(lexer):
    tokens = list(lexer("@玉ねぎ（大）を炒める\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@玉ねぎ（大）"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "を炒める"

def test_name_and_tool_with_particles(lexer):
    tokens = list(lexer("@卵を#[pan]で焼く\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@卵"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "を"
    assert tokens[2].type == "TOOL"
    assert tokens[2].value == "#[pan]"
    assert tokens[3].type == "TEXT"
    assert tokens[3].value == "で焼く"

def test_tool_particle_boundary_basic(lexer):
    tokens = list(lexer("#フライパンで炒める\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#フライパン"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "で炒める"

import pytest

@pytest.mark.parametrize("particle", ["を", "に", "で", "へ", "と", "が", "は", "から", "まで"])
def test_tool_particle_variants(particle, lexer):
    text = f"#包丁{particle}切る\n"
    tokens = list(lexer(text))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#包丁"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == particle + "切る"

def test_tool_boundary_vs_fallback(lexer):
    # 助詞あり → 助詞境界 TOOL が勝つ
    tokens = list(lexer("#鍋で煮る\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#鍋"

    # 助詞なし → fallback TOOL が発火
    tokens = list(lexer("#鍋\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#鍋"

def test_tool_fallback_stops_at_particle(lexer):
    tokens = list(lexer("#panで焼く\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#pan"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "で焼く"

def test_name_and_tool_sequence(lexer):
    tokens = list(lexer("@卵を#フライパンで焼く\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "@卵"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "を"
    assert tokens[2].type == "TOOL"
    assert tokens[2].value == "#フライパン"
    assert tokens[3].type == "TEXT"
    assert tokens[3].value == "で焼く"

def test_tool_with_attribute_bblock(lexer):
    tokens = list(lexer("#オーブン{200C}で焼く\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#オーブン{200C}"
    assert tokens[1].type == "TEXT"
    assert tokens[1].value == "で焼く"

def test_tool_english_with_particle(lexer):
    tokens = list(lexer("#panで焼く\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#pan"

def test_tool_with_symbols(lexer):
    tokens = list(lexer("#電子レンジ600Wで温める\n"))
    assert tokens[0].type == "TOOL"
    assert tokens[0].value == "#電子レンジ600W"

def test_tool_not_eaten_by_text(lexer):
    tokens = list(lexer("Use #panで焼く\n"))
    assert tokens[1].type == "TOOL"
    assert tokens[1].value == "#pan"
