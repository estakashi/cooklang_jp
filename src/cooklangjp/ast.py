# AST
import re

class Recipe:
    def __init__(self, steps):
        self.steps = []
        self.metadata = []

        for s in steps:
            if isinstance(s, Metadata):
                self.metadata.append(s)
            else:
                self.steps.append(s)

    def __repr__(self):
        return f"Recipe({self.steps})"

class Metadata:
    def __init__(self, raw_line):
        # raw_line = ">> servings: 2"
        line = raw_line.lstrip('>').lstrip('>').strip()
        if ':' in line:
            key, value = line.split(':', 1)
            self.key = key.strip()
            self.value = value.strip()
        else:
            self.key = None
            self.value = None
    
    def __repr__(self):
        return f"Metadata({self.key}: {self.value})"
        

class Note:
    def __init__(self, raw_lines):
        # lines=["> 一行目", "> 二行目", ...]
        self.lines = [self._clean(line) for line in raw_lines]

    def _clean(self, line):
        return line.lstrip('> ').rstrip()

    def __repr__(self):
        return f"Note({self.lines})"

class Step:
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return f"Step({self.items})"

class Text:
    def __init__(self, content):
        self.content = content.strip()

    def __repr__(self):
        return f"Text({self.content})"

class Tool:
    def __init__(self, raw):
        self.name = raw.lstrip('#').strip('[]')

    def __repr__(self):
        return f"Tool({self.name})"

class Timer:
    def __init__(self, raw):
        m = re.match(r'~(\d+)(.+)', raw)
        if m:
            self.number = int(m.group(1))
            self.unit = m.group(2)
        else:
            self.number = None
            self.unit = None

    def __repr__(self):
        return f"Timer({self.number}, {self.unit})"

class Ingredient:
    def __init__(self, raw_name, amount):
        self.name = raw_name.lstrip('@')
        self.amount = amount

    def __repr__(self):
        return f"Ingredient({self.name}, {self.amount})"

class Amount:
    def __init__(self, prefix, number, raw_unit):
        self.prefix = prefix
        self.number = number
        self.unit = raw_unit.lstrip('%')

    def __repr__(self):
        return f"Amount({self.prefix}, {self.number}, {self.unit})"
        
        
