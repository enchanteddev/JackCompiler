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
    operators = '+-*/&|<>='

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
    

    def check_and_write(self, condition, callback = None):
        if condition(self.tokens[self.cursor]):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
        else:
            print(self.tokens[self.cursor])
            callback()

    
    def compileClassVarDec(self):
        self.xml.open_tag('classVarDec')

        self.check_and_write(lambda x: x[0] == 'keyword' and x[1] in ('static', 'field'))
        self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char')) or (x[0] == 'identifier'))
        self.check_and_write(lambda x: x[0] == 'identifier')

        while self.tokens[self.cursor] == ('symbol', ','):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
            self.check_and_write(lambda x: x[0] == 'identifier')

        self.check_and_write(lambda x: x == ('symbol', ';'))

        self.xml.close_tag('classVarDec')
    

    def compileVarDec(self):
        self.xml.open_tag('VarDec')

        self.check_and_write(lambda x: x[0] == 'keyword' and x[1] == 'var')
        self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char')) or (x[0] == 'identifier'))
        self.check_and_write(lambda x: x[0] == 'identifier')

        while self.tokens[self.cursor] == ('symbol', ','):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
            self.check_and_write(lambda x: x[0] == 'identifier')

        self.check_and_write(lambda x: x == ('symbol', ';'))

        self.xml.close_tag('VarDec')
    

    def compileSubroutineDec(self):
        self.xml.open_tag('subroutineDec')
        self.check_and_write(lambda x: x[0] == 'keyword' and x[1] in ('constructor', 'function', 'method'))
        self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char', 'void')) or (x[0] == 'identifier'))
        self.check_and_write(lambda x: x[0] == 'identifier')
        self.check_and_write(lambda x: x == ('symbol', '('))
        self.compileParameterList()
        self.compileSubroutineBody()
        self.xml.close_tag('subroutineDec')

    
    def compileParameterList(self):
        if self.tokens[self.cursor][1] == ')':
            self.xml.open_tag('parameterList')
            self.xml.close_tag('parameterList')
            self.check_and_write(lambda x: x[1] == ')')
        else:
            self.xml.open_tag('parameterList')
            self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char')) or (x[0] == 'identifier'))
            self.check_and_write(lambda x: x[0] == 'identifier')
            while self.tokens[self.cursor] == ('symbol', ','):
                self.xml.write(*self.tokens[self.cursor])
                self.cursor += 1
                self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char')) or (x[0] == 'identifier'))
                self.check_and_write(lambda x: x[0] == 'identifier')
            self.xml.close_tag('parameterList')
            self.check_and_write(lambda x: x[1] == ')')



    def compileSubroutineBody(self):
        self.xml.open_tag('subroutineBody')
        self.check_and_write(lambda x: x == ('symbol', '{'))
        while self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] == 'var':
            self.compileVarDec()
        self.compileStatements()
        self.check_and_write(lambda x: x == ('symbol', '}'))
        self.xml.close_tag('subroutineBody')
    

    def compileStatements(self):
        self.xml.open_tag('statements')
        while self.tokens[self.cursor][0] == 'keyword':
            match self.tokens[self.cursor][1]:
                case 'let': self.compileLetStatement()
                case 'if': self.compileIfStatement()
                case 'while': self.compileWhileStatement()
                case 'do': self.compileDoStatement()
                case 'return': self.compileReturnStatement()
        self.xml.close_tag('statements')

    
    def compileLetStatement(self):
        self.xml.open_tag('letStatement')
        self.check_and_write(lambda x: x == ('keyword', 'let'))
        self.check_and_write(lambda x: x[0] == 'identifier')
        if self.tokens[self.cursor] == ('symbol', '['):
            self.check_and_write(lambda x: x == ('symbol', '['))
            self.compileExpression()
            self.check_and_write(lambda x: x == ('symbol', ']'))
        self.xml.close_tag('letStatement')
    

    def compileExpression(self):
        self.xml.open_tag('expression')
        self.compileTerm()
        if self.tokens[self.cursor][1] in self.operators:
            self.check_and_write(lambda x: x in self.operators)
            self.compileTerm()
        self.xml.close_tag('expression')

    
    def compileTerm(self):
        self.xml.open_tag('term')
        self.check_and_write(lambda x: x[0] in ('integerConstant', 'stringConstant', 'keywordConstant', 'identifier'))
        if self.tokens[self.cursor - 1][0] == 'identifier':
            if self.tokens[self.cursor] == ('symbol', '['):
                self.check_and_write(lambda x: x == ('symbol', '['))
                self.compileExpression()
                self.check_and_write(lambda x: x == ('symbol', ']'))
            
            elif self.tokens[self.cursor] == ('symbol', '('):
                self.check_and_write(lambda x: x == ('symbol', '('))
                self.compileExpressionList()
                self.check_and_write(lambda x: x == ('symbol', ')'))

        self.xml.close_tag('term')

    
    def compileExpressionList(self):
        self.xml.open_tag('expressionList')
        if self.tokens[self.cursor][0] == 'identifier':
            self.check_and_write(lambda x: x[0] == 'identifier')
        self.xml.close_tag('expressionList')


    def compileClass(self):
        self.xml.open_tag('class')

        self.check_and_write(lambda x: x == ('keyword', 'class'))
        self.check_and_write(lambda x: x[0] == 'identifier')
        self.check_and_write(lambda x: x == ('symbol', '{'))
        
        while self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] in ('static', 'field'):
            self.compileClassVarDec()
        
        while self.tokens[self.cursor][0] == 'keyword' and self.tokens[self.cursor][1] in ('constructor', 'function', 'method'):
            self.compileSubroutineDec()
        
        self.check_and_write(lambda x: x == ('symbol', '}'))

        
        self.xml.close_tag('class')
        self.xml.close()