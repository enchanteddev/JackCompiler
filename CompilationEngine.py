from pathlib import Path

class XML:
    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)
        self._buffer = ""
        self.tag_depth = 0

    def open_tag(self, tag: str):
        self._buffer += '\t' * self.tag_depth + f"<{tag}>\n"
        self.tag_depth += 1

    def close_tag(self, tag: str):
        self.tag_depth -= 1
        self._buffer += '\t' * self.tag_depth + f"</{tag}>\n"

    def write(self, tag: str, value: str):
        self._buffer += '\t' * self.tag_depth + f"<{tag}> {value} </{tag}>\n"
    
    def close(self):
        with open(self.fp, "w") as outf:
            outf.write(self._buffer)


class CompilationEngine:
    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)
        self.outfp = self.fp.with_name(self.fp.name.split('.')[0] + '.f.xml')
        self.xml = XML(self.outfp)
        
        with open(self.fp) as txmlfile:
            self.txml = txmlfile.read()
        
        self.tokens = []
        self.cursor = 0
        self.constructor()

    def constructor(self):
        tokens = []
        txml_lines = self.txml.splitlines()
        for line in txml_lines:
            if line == "<tokens>" or line == "</tokens>":
                continue
            parts = line.split()
            token = parts[1]
            token_type = parts[0][1:-1]
            tokens.append((token_type, token))
        
        self.tokens = tokens

    
    def compileClassVarDec(self):
        self.xml.open_tag('classVarDec')
        if self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] in ('static', 'field'):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        if ((self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] in ('boolean', 'int', 'char')) or
            (self.tokens[self.cursor][0] == 'identifier')):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        if self.tokens[self.cursor][0] == 'identifier':
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        while self.tokens[self.cursor] == ('symbol', ','):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
            if self.tokens[self.cursor][0] == 'identifier':
                self.xml.write(*self.tokens[self.cursor])
                self.cursor += 1
            else:
                ...
        if self.tokens[self.cursor] == ('symbol', ';'):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        self.xml.close_tag('classVarDec')
    

    def compileSubroutineDec(self):
        ...


    def compileClass(self):
        self.xml.open_tag('class')
        if self.tokens[self.cursor] == ('keyword', 'class'):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        if self.tokens[self.cursor][0] == 'identifier':
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        if self.tokens[self.cursor] == ('symbol', '{'):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        
        while self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] in ('static', 'field'):
            self.compileClassVarDec()
        
        while self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] in ('constructor', 'function', 'method'):
            self.compileSubroutineDec()
        
        if self.tokens[self.cursor] == ('symbol', '}'):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            ...
        
        self.xml.close_tag('class')
        self.xml.close()