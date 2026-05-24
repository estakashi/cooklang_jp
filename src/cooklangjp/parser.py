import ply.yacc as yacc
from cooklangjp.lexer import CookLexer
from cooklangjp.ast import Amount, Ingredient, Text, Tool, Timer, Note, Metadata, Step, Recipe
# Parser
class CookParser:
    tokens = CookLexer.tokens

    start = "recipe"

    def __init__(self):
        self.lexer = CookLexer().build()

    def build(self):
        self.parser = yacc.yacc(module=self)
        return self

    def parse(self, text):
        return self.parser.parse(text, lexer=self.lexer)
        

    def p_amount_multi(self, p):
        'amount : LBRACE TEXT NUMBER TEXT RBRACE'
        p[0] = Amount(p[2], p[3], p[4])
    
    def p_amount_simple(self, p):
        'amount : LBRACE NUMBER TEXT RBRACE'
        p[0] = Amount(None, p[2], p[3])
    
    def p_ingredient_simple(self, p):
        'ingredient : NAME'
        p[0] = Ingredient(p[1], None)

    def p_ingredient_amount(self, p):
        'ingredient : NAME amount'
        p[0] = Ingredient(p[1], p[2])

    def p_tool(self, p):
        'tool : TOOL'
        p[0] = Tool(p[1])

    def p_timer(self, p):
        'timer : TIMER'
        p[0] = Timer(p[1])
        
    def p_text(self, p):
        'text : TEXT'
        p[0] = Text(p[1])

    def p_item_tool(self, p):
        'item : tool'
        p[0] = p[1]

    def p_item_timer(self, p):
        'item : timer'
        p[0] = p[1]
        
    def p_item_text(self, p):
        'item : text'
        p[0] = p[1]

    def p_item_ingredient(self, p):
        'item : ingredient'
        p[0] = p[1]

    def p_items_multi(self, p):
        'items : items item'
        p[0] = p[1] + [p[2]]

    def p_items_single(self, p):
        'items : item'
        p[0] = [p[1]]

    def p_step(self, p):
        'step : items NEWLINE'
        p[0] = Step(p[1])

    def p_note_lines_multi(self, p):
        'note_lines : note_lines NOTE_LINE NEWLINE'
        p[0] = p[1] + [p[2]]

    def p_note_lines_single(self, p):
        'note_lines : NOTE_LINE NEWLINE'
        p[0] = [p[1]]
    
    def p_note(self, p):
        'note : note_lines'
        p[0] = Note(p[1])

    def p_metadata(self, p):
        'metadata : METADATA_LINE NEWLINE'
        p[0] = Metadata(p[1])

    def p_recipe_single(self, p):
        '''recipe : step
                  | note
                  | metadata'''
        p[0] = Recipe([p[1]])

    def p_recipe_blank(self, p):
        'recipe : recipe BLANK'
        p[0] = p[1]

    def p_recipe_multi(self, p):
        '''recipe : recipe step
                  | recipe note
                  | recipe metadata'''
        p[0] = Recipe(p[1].steps + p[1].metadata + [p[2]])

    def p_error(self, p):
        print("Syntax error", p)
