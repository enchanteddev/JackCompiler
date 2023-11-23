from pathlib import Path
from SymbolTable import SymbolTable, Kind
from VMWriter import VMWriter

class XML:
    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)
        self._buffer = ""
        self.tag_depth = 0
        self.indent_char = '  '

    def open_tag(self, tag: str):
        self._buffer += self.indent_char * self.tag_depth + f"<{tag}>\n"
        self.tag_depth += 1

    def close_tag(self, tag: str):
        self.tag_depth -= 1
        self._buffer += self.indent_char * self.tag_depth + f"</{tag}>\n"

    def write(self, tag: str, value: str):
        self._buffer += self.indent_char * self.tag_depth + f"<{tag}> {value} </{tag}>\n"
    
    def close(self):
        with open(self.fp, "w") as outf:
            outf.write(self._buffer)


class CompilationEngine:
    operators = list('+-*/|=') + ['&lt;', '&gt;', '&amp;']

    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)
        self.outfp = self.fp.with_name(self.fp.name.split('.')[0] + '.f.xml')
        self.xml = XML(self.outfp)
        
        with open(self.fp) as txmlfile:
            self.txml = txmlfile.read()
        
        self.tokens = []
        self.symtab = SymbolTable()
        self.vmwriter = VMWriter(self.fp.with_suffix('.vm'))
        self.cursor = 0
        self.constructor()

    def constructor(self):
        tokens = []
        txml_lines = self.txml.splitlines()
        for line in txml_lines:
            if line == "<tokens>" or line == "</tokens>":
                continue
            parts = line.split('>')
            token = parts[1].split('<')[0][1:-1]
            token_type = parts[0][1:]
            tokens.append((token_type, token))
        
        self.tokens = tokens
    

    def check_and_write(self, condition, callback = lambda:None):
        if condition(self.tokens[self.cursor]):
            self.xml.write(*self.tokens[self.cursor])
            self.cursor += 1
            return True
        else:
            # print(self.tokens[self.cursor], self.cursor)
            callback()
            return False
            # raise SyntaxError

    @property
    def currToken(self):
        return self.tokens[self.cursor]

    def check_and_next(self, condition, task = lambda:None, callback = print):
        if condition(self.currToken):
            task()
            self.cursor += 1
        else:
            callback(f"Failed at: {self.currToken}")
    
    def compileClassVarDec(self):
        if self.currToken[0] == 'keyword':
            match self.currToken[1]:
                case 'static': kind = Kind.STATIC
                case 'field': kind = Kind.FIELD
                case _: raise SyntaxError()
        else: raise SyntaxError

        if (self.currToken[0] == 'keyword' and self.currToken[1] in ('boolean', 'int', 'char')) or (self.currToken[0] == 'identifier'):
            type_ = self.currToken[1]
        else: raise SyntaxError

        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
        else: raise SyntaxError
        
        self.symtab.define(name, type_, kind)
        
        while self.currToken == ('symbol', ','):
            self.cursor += 1
            self.check_and_write(lambda x: x[0] == 'identifier')
            
            if self.currToken[0] == 'identifier':
                name = self.currToken[1]
            else:
                raise SyntaxError
            
            self.symtab.define(name, type_, kind)
        
        # self.xml.open_tag('classVarDec')

        # self.check_and_write(lambda x: x[0] == 'keyword' and x[1] in ('static', 'field'))
        # self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char')) or (x[0] == 'identifier'))
        # self.check_and_write(lambda x: x[0] == 'identifier')

        # while self.tokens[self.cursor] == ('symbol', ','):
        #     self.xml.write(*self.tokens[self.cursor])
        #     self.cursor += 1
        #     self.check_and_write(lambda x: x[0] == 'identifier')

        # self.check_and_write(lambda x: x == ('symbol', ';'))

        # self.xml.close_tag('classVarDec')
    



    def compileVarDec(self):
        self.check_and_next(lambda x: x[0] == 'keyword' and x[1] == 'var')
        kind = Kind.VAR
        if (self.currToken[0] == 'keyword' and self.currToken[1] in ('boolean', 'int', 'char')) or (self.currToken[0] == 'identifier'):
            type_ = self.currToken[1]
        else:
            raise SyntaxError
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
        else:
            raise SyntaxError
        
        self.symtab.define(name, type_, kind)
        vars_ = 1

        while self.currToken == ('symbol', ','):
            self.cursor += 1
            self.check_and_write(lambda x: x[0] == 'identifier')
            
            if self.currToken[0] == 'identifier':
                name = self.currToken[1]
            else:
                raise SyntaxError
            
            self.symtab.define(name, type_, kind)
            vars_ += 1
        
        return vars_

        # self.xml.open_tag('varDec')

        # self.check_and_write(lambda x: x[0] == 'keyword' and x[1] == 'var')
        # self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char')) or (x[0] == 'identifier'))
        # self.check_and_write(lambda x: x[0] == 'identifier')

        # while self.tokens[self.cursor] == ('symbol', ','):
        #     self.xml.write(*self.tokens[self.cursor])
        #     self.cursor += 1
        #     self.check_and_write(lambda x: x[0] == 'identifier')

        # self.check_and_write(lambda x: x == ('symbol', ';'))

        # self.xml.close_tag('varDec')
    

    def compileSubroutineDec(self):
        self.check_and_next(lambda x: x[0] == 'keyword' and x[1] in ('constructor', 'function', 'method'))
        self.check_and_next(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char', 'void')) or (x[0] == 'identifier'))
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
        else: raise SyntaxError

        self.check_and_next(lambda x: x == ('symbol', '('))
        while self.currToken[1] != ')': self.cursor += 1
        
        self.compileSubroutineBody(name)

        # self.xml.open_tag('subroutineDec')
        # self.check_and_write(lambda x: x[0] == 'keyword' and x[1] in ('constructor', 'function', 'method'))
        # self.check_and_write(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char', 'void')) or (x[0] == 'identifier'))
        # self.check_and_write(lambda x: x[0] == 'identifier')
        # self.check_and_write(lambda x: x == ('symbol', '('))
        # self.compileParameterList()
        # self.compileSubroutineBody()
        # self.xml.close_tag('subroutineDec')

    
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



    def compileSubroutineBody(self, name: str):
        self.check_and_next(lambda x: x == ('symbol', '{'))
        nVars = 0
        while self.currToken == ('keyword', 'var'):
            nVars += self.compileVarDec()
        self.vmwriter.writeFunction(name, nVars)
        self.compileStatements()
        self.check_and_next(lambda x: x == ('symbol', '}'))
    

    def compileStatements(self):
        # self.xml.open_tag('statements')
        while self.tokens[self.cursor][0] == 'keyword':
            match self.tokens[self.cursor][1]:
                case 'let': self.compileLetStatement()
                case 'if': self.compileIfStatement()
                case 'while': self.compileWhileStatement()
                case 'do': self.compileDoStatement()
                case 'return': self.compileReturnStatement()
        # self.xml.close_tag('statements')

    
    def compileLetStatement(self):
        # self.xml.open_tag('letStatement')
        self.check_and_next(lambda x: x == ('keyword', 'let'))
        # self.check_and_write(lambda x: x[0] == 'identifier')
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
        else: raise SyntaxError

        

        if self.tokens[self.cursor] == ('symbol', '['):
            self.check_and_write(lambda x: x == ('symbol', '['))
            self.compileExpression()
            self.check_and_write(lambda x: x == ('symbol', ']'))
        self.check_and_write(lambda x: x[1] == '=')
        self.compileExpression()
        self.check_and_write(lambda x: x[1] == ';')
        # self.xml.close_tag('letStatement')
    
    def compileIfStatement(self):
        self.xml.open_tag('ifStatement')
        self.check_and_write(lambda x: x == ('keyword', 'if'))
        self.check_and_write(lambda x: x == ('symbol', '('))
        self.compileExpression()
        self.check_and_write(lambda x: x == ('symbol', ')'))
        self.check_and_write(lambda x: x == ('symbol', '{'))
        self.compileStatements()
        self.check_and_write(lambda x: x == ('symbol', '}'))
        if self.tokens[self.cursor] == ('keyword', 'else'):
            self.check_and_write(lambda x: x == ('keyword', 'else'))
            self.check_and_write(lambda x: x == ('symbol', '{'))
            self.compileStatements()
            self.check_and_write(lambda x: x == ('symbol', '}'))
        self.xml.close_tag('ifStatement')
    
    def compileWhileStatement(self):
        self.xml.open_tag('whileStatement')
        self.check_and_write(lambda x: x == ('keyword', 'while'))
        self.check_and_write(lambda x: x == ('symbol', '('))
        self.compileExpression()
        self.check_and_write(lambda x: x == ('symbol', ')'))
        self.check_and_write(lambda x: x == ('symbol', '{'))
        self.compileStatements()
        self.check_and_write(lambda x: x == ('symbol', '}'))
        self.xml.close_tag('whileStatement')
    
    def compileDoStatement(self):
        self.xml.open_tag('doStatement')
        self.check_and_write(lambda x: x == ('keyword', 'do'))
        if self.tokens[self.cursor][0] == 'identifier':
            self.check_and_write(lambda x: x[0] == 'identifier')            
            if self.tokens[self.cursor] == ('symbol', '('):
                self.check_and_write(lambda x: x == ('symbol', '('))
                self.compileExpressionList()
                self.check_and_write(lambda x: x == ('symbol', ')'))
            
            elif self.tokens[self.cursor] == ('symbol', '.'):
                self.check_and_write(lambda x: x == ('symbol', '.'))
                self.check_and_write(lambda x: x[0] == 'identifier')
                self.check_and_write(lambda x: x == ('symbol', '('))
                self.compileExpressionList()
                self.check_and_write(lambda x: x == ('symbol', ')'))
        self.check_and_write(lambda x: x == ('symbol', ';'))
        self.xml.close_tag('doStatement')
    
    def compileReturnStatement(self):
        self.xml.open_tag('returnStatement')
        self.check_and_write(lambda x: x == ('keyword', 'return'))
        if self.tokens[self.cursor][1] != ';':
            self.compileExpression()
        self.check_and_write(lambda x: x == ('symbol', ';'))
        self.xml.close_tag('returnStatement')
    

    def compileExpression(self):
        self.xml.open_tag('expression')
        self.compileTerm()
        if self.tokens[self.cursor][1] in self.operators:
            self.check_and_write(lambda x: x[1] in self.operators)
            self.compileTerm()
        self.xml.close_tag('expression')

    
    def compileTerm(self):
        self.xml.open_tag('term')
        flag = self.check_and_write(lambda x: x[0] in ('integerConstant', 'stringConstant', 'identifier') or 
                                    (x[0] == 'keyword' and x[1] in ('true', 'false', 'this', 'null')))
        if self.tokens[self.cursor - 1][0] == 'identifier':
            if self.tokens[self.cursor] == ('symbol', '['):
                self.check_and_write(lambda x: x == ('symbol', '['))
                self.compileExpression()
                self.check_and_write(lambda x: x == ('symbol', ']'))
            
            elif self.tokens[self.cursor] == ('symbol', '('):
                self.check_and_write(lambda x: x == ('symbol', '('))
                self.compileExpressionList()
                self.check_and_write(lambda x: x == ('symbol', ')'))
            
            elif self.tokens[self.cursor] == ('symbol', '.'):
                self.check_and_write(lambda x: x == ('symbol', '.'))
                self.check_and_write(lambda x: x[0] == 'identifier')
                self.check_and_write(lambda x: x == ('symbol', '('))
                self.compileExpressionList()
                self.check_and_write(lambda x: x == ('symbol', ')'))

        
        if not flag:
            match self.tokens[self.cursor][1]:
                case '(':
                    self.check_and_write(lambda x: x[1] == '(')
                    self.compileExpression()
                    self.check_and_write(lambda x: x[1] == ')')
                case '~':
                    self.check_and_write(lambda x: x[1] == '~')
                    self.compileTerm()
                case '-':
                    self.check_and_write(lambda x: x[1] == '-')
                    self.compileTerm()

        self.xml.close_tag('term')

    
    def compileExpressionList(self):
        self.xml.open_tag('expressionList')
        if self.tokens[self.cursor][1] != ')':
            self.compileExpression()
            while self.tokens[self.cursor][1] == ',':
                self.check_and_write(lambda x: x[1] == ',')
                self.compileExpression()
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