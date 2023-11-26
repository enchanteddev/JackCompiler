from pathlib import Path
from SymbolTable import SymbolTable, Kind
from VMWriter import VMWriter, kind2seg, ArithmeticCommand, Segment


class CompilationEngine:
    operators = list('+-*/|=') + ['&lt;', '&gt;', '&amp;']

    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)
        self.outfp = self.fp.with_name(self.fp.name.split('.')[0] + '.f.xml')
        # self.xml = XML(self.outfp)
        
        with open(self.fp) as txmlfile:
            self.txml = txmlfile.read()
        
        self.tokens = []
        self.symtab = SymbolTable()
        self.vmwriter = VMWriter(self.fp.with_suffix('.vm'))
        self.cursor = 0
        self.ifLbC = 0
        self.whLbC = 0
        self.className = ''
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
            # self.xml.write(*self.tokens[self.cursor])
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
        # print("c&n:", self.currToken)
        if condition(self.currToken):
            task()
            self.cursor += 1
        else:
            callback(f"[{self.cursor}]: Failed at: {self.currToken} | {condition}")
    
    def compileClassVarDec(self):
        if self.currToken[0] == 'keyword':
            match self.currToken[1]:
                case 'static': kind = Kind.STATIC
                case 'field': kind = Kind.FIELD
                case _: raise SyntaxError()
            self.cursor += 1
        else: raise SyntaxError

        if (self.currToken[0] == 'keyword' and self.currToken[1] in ('boolean', 'int', 'char')) or (self.currToken[0] == 'identifier'):
            type_ = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError

        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError
        
        self.symtab.define(name, type_, kind)
        
        while self.currToken == ('symbol', ','):
            self.cursor += 1
            # self.check_and_write(lambda x: x[0] == 'identifier')
            
            if self.currToken[0] == 'identifier':
                name = self.currToken[1]
                self.cursor += 1
            else:
                raise SyntaxError
            
            self.symtab.define(name, type_, kind)
        self.check_and_next(lambda x: x == ('symbol', ';'))
        
    

    def compileVarDec(self):
        self.check_and_next(lambda x: x[0] == 'keyword' and x[1] == 'var')
        kind = Kind.VAR
        if (self.currToken[0] == 'keyword' and self.currToken[1] in ('boolean', 'int', 'char')) or (self.currToken[0] == 'identifier'):
            type_ = self.currToken[1]
            self.cursor += 1
        else:
            raise SyntaxError
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
            self.cursor += 1
        else:
            raise SyntaxError
        
        self.symtab.define(name, type_, kind)
        vars_ = 1

        while self.currToken == ('symbol', ','):
            self.cursor += 1
            
            if self.currToken[0] == 'identifier':
                name = self.currToken[1]
                self.cursor += 1
            else:
                raise SyntaxError(self.currToken)
            
            self.symtab.define(name, type_, kind)
            vars_ += 1
        
        self.check_and_next(lambda x: x == ('symbol', ';'))
        
        return vars_
    

    def compileSubroutineDec(self, className = ''):
        self.check_and_next(lambda x: x[0] == 'keyword' and x[1] in ('constructor', 'function', 'method'))
        if self.tokens[self.cursor - 1][1] == 'constructor':
            isC = True
        else: isC = False
        if self.tokens[self.cursor - 1][1] == 'method':
            isM = True
        else: isM = False
        self.check_and_next(lambda x: (x[0] == 'keyword' and x[1] in ('boolean', 'int', 'char', 'void')) or (x[0] == 'identifier'))
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError

        self.check_and_next(lambda x: x == ('symbol', '('))
        self.compileParameterList(isM)
        #  while self.currToken[1] != ')': self.cursor += 1
        
        self.compileSubroutineBody(f'{className}.{name}' if className else name, isC, isM)

    
    def compileParameterList(self, isM):
        # print(self.currToken)
        if self.tokens[self.cursor][1] == ')':
            self.check_and_next(lambda x: x[1] == ')')
            return
        
        if (self.currToken[0] == 'keyword' and self.currToken[1] in ('boolean', 'int', 'char')) or (self.currToken[0] == 'identifier'):
            type_ = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError
        
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError(self.currToken)

        self.symtab.define(name, type_, Kind.ARG, isM)

        while self.tokens[self.cursor] == ('symbol', ','):
            self.cursor += 1
            if (self.currToken[0] == 'keyword' and self.currToken[1] in ('boolean', 'int', 'char')) or (self.currToken[0] == 'identifier'):
                type_ = self.currToken[1]
                self.cursor += 1
            else: raise SyntaxError
            
            if self.currToken[0] == 'identifier':
                name = self.currToken[1]
                self.cursor += 1
            else: raise SyntaxError

            self.symtab.define(name, type_, Kind.ARG, isM)
        self.check_and_next(lambda x: x[1] == ')')


    def compileSubroutineBody(self, name: str, isC, isM):
        self.check_and_next(lambda x: x == ('symbol', '{'))
        nVars = 0
        while self.currToken == ('keyword', 'var'):
            nVars += self.compileVarDec()
        self.vmwriter.writeFunction(name, nVars)
        if isC:
            self.vmwriter.writePush(Segment.CONSTANT, self.symtab.class_table.table["kind"].count(Kind.FIELD))
            self.vmwriter.writeCall('Memory.alloc', 1)
            self.vmwriter.writePop(Segment.POINTER, 0)
        if isM:
            self.vmwriter.writePush(Segment.ARGUMENT, 0)
            self.vmwriter.writePop(Segment.POINTER, 0)
        self.compileStatements()
        self.check_and_next(lambda x: x == ('symbol', '}'))
    

    def compileStatements(self):
        while self.currToken[0] == 'keyword':
            match self.currToken[1]:
                case 'let': self.compileLetStatement()
                case 'if': self.compileIfStatement()
                case 'while': self.compileWhileStatement()
                case 'do': self.compileDoStatement()
                case 'return': self.compileReturnStatement()

    
    def compileLetStatement(self):
        self.check_and_next(lambda x: x == ('keyword', 'let'))
        if self.currToken[0] == 'identifier':
            name = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError

        kind = self.symtab.kindOf(name)
        index = self.symtab.indexOf(name)

        isArray = False

        if self.currToken == ('symbol', '['):
            isArray = True
            self.vmwriter.writePush(kind2seg(kind), index)
            self.check_and_next(lambda x: x == ('symbol', '['))
            self.compileExpression()
            self.check_and_next(lambda x: x == ('symbol', ']'))
            self.vmwriter.writeArithmetic(ArithmeticCommand.ADD)

        self.check_and_next(lambda x: x[1] == '=')
        # print('1')
        self.compileExpression()
        # print('2')
        self.check_and_next(lambda x: x[1] == ';')
        # print('3')

        if isArray:
            self.vmwriter.writePop(Segment.TEMP, 0)
            self.vmwriter.writePop(Segment.POINTER, 1)
            self.vmwriter.writePush(Segment.TEMP, 0)
            self.vmwriter.writePop(Segment.THAT, 0)
        else:
            self.vmwriter.writePop(kind2seg(kind), index)

    
    def compileIfStatement(self):
        self.check_and_next(lambda x: x == ('keyword', 'if'))
        self.check_and_next(lambda x: x == ('symbol', '('))
        self.compileExpression()
        self.vmwriter.writeArithmetic(ArithmeticCommand.NOT)
        self.check_and_next(lambda x: x == ('symbol', ')'))
        self.check_and_next(lambda x: x == ('symbol', '{'))

        label = f'if{self.ifLbC}'
        end = f'endif{self.ifLbC}'
        self.ifLbC += 1

        self.vmwriter.writeIf(label)
        self.compileStatements()
        self.vmwriter.writeGoto(end)
        self.check_and_next(lambda x: x == ('symbol', '}'))


        self.vmwriter.writeLabel(label)
        if self.tokens[self.cursor] == ('keyword', 'else'):
            self.check_and_next(lambda x: x == ('keyword', 'else'))
            self.check_and_next(lambda x: x == ('symbol', '{'))
            self.compileStatements()
            self.check_and_next(lambda x: x == ('symbol', '}'))
        self.vmwriter.writeLabel(end)
    
    def compileWhileStatement(self):
        whileLabel = f'while{self.whLbC}'
        self.check_and_next(lambda x: x == ('keyword', 'while'))
        self.check_and_next(lambda x: x == ('symbol', '('))
        self.vmwriter.writeLabel(whileLabel)
        self.compileExpression()
        self.vmwriter.writeArithmetic(ArithmeticCommand.NOT)
        self.check_and_next(lambda x: x == ('symbol', ')'))
        self.check_and_next(lambda x: x == ('symbol', '{'))
        end = f'endwhile{self.whLbC}'
        self.whLbC += 1
        self.vmwriter.writeIf(end)
        self.compileStatements()
        self.vmwriter.writeGoto(whileLabel)
        self.check_and_next(lambda x: x == ('symbol', '}'))
        self.vmwriter.writeLabel(end)
    
    def compileDoStatement(self):
        self.check_and_next(lambda x: x == ('keyword', 'do'))
        if self.currToken[0] == 'identifier':
            identifier = self.currToken[1]
            self.cursor += 1
            if self.currToken == ('symbol', '('):
                self.check_and_next(lambda x: x == ('symbol', '('))
                self.vmwriter.writePush(Segment.POINTER, 0)
                args = self.compileExpressionList()
                self.check_and_next(lambda x: x == ('symbol', ')'))
                self.vmwriter.writeCall(f'{self.className}.{identifier}', args + 1)
            
            elif self.currToken == ('symbol', '.'):
                isMethod = True
                try:
                    kind = self.symtab.kindOf(identifier)
                    index = self.symtab.indexOf(identifier)
                    type_ = self.symtab.typeOf(identifier)
                except ValueError:
                    isMethod = False
                self.check_and_next(lambda x: x == ('symbol', '.'))
                fnName = self.currToken[1]
                self.cursor += 1
                if isMethod:
                    self.vmwriter.writePush(kind2seg(kind), index) # type: ignore
                    self.check_and_next(lambda x: x == ('symbol', '('))
                    args = self.compileExpressionList()
                    self.check_and_next(lambda x: x == ('symbol', ')'))
                    self.vmwriter.writeCall(f'{type_}.{fnName}', args + 1) # type: ignore
                else:
                    self.check_and_next(lambda x: x == ('symbol', '('))
                    args = self.compileExpressionList()
                    self.check_and_next(lambda x: x == ('symbol', ')'))
                    self.vmwriter.writeCall(f'{identifier}.{fnName}', args)
        self.vmwriter.writePop(Segment.TEMP, 0)
        self.check_and_next(lambda x: x == ('symbol', ';'))
    
    def compileReturnStatement(self):
        self.check_and_next(lambda x: x == ('keyword', 'return'))
        if self.currToken[1] != ';':
            self.compileExpression()
        else:
            self.vmwriter.writePush(Segment.CONSTANT, 0)
        self.vmwriter.writeReturn()
        self.check_and_next(lambda x: x == ('symbol', ';'))
    

    def compileExpression(self):
        self.compileTerm()
        if self.currToken[1] in self.operators:
            op = self.currToken[1]
            self.cursor += 1
            self.compileTerm()
            
            match op:
                case '+': self.vmwriter.writeArithmetic(ArithmeticCommand.ADD)
                case '-': self.vmwriter.writeArithmetic(ArithmeticCommand.SUB)
                case '=': self.vmwriter.writeArithmetic(ArithmeticCommand.EQ)
                case '&gt;': self.vmwriter.writeArithmetic(ArithmeticCommand.GT)
                case '&lt;': self.vmwriter.writeArithmetic(ArithmeticCommand.LT)
                case '&amp;': self.vmwriter.writeArithmetic(ArithmeticCommand.AND)
                case '|': self.vmwriter.writeArithmetic(ArithmeticCommand.OR)
                case '*': self.vmwriter.writeCall('Math.multiply', 2)
                case '/': self.vmwriter.writeCall('Math.divide', 2)
            # self.cursor += 1

    
    def compileTerm(self):
        match self.currToken[1]:
            case '-':
                self.cursor += 1
                self.compileTerm()
                self.vmwriter.writeArithmetic(ArithmeticCommand.NEG)
                return
            case '~':
                self.cursor += 1
                self.compileTerm()
                self.vmwriter.writeArithmetic(ArithmeticCommand.NOT)
                return
            case '(':
                self.cursor += 1
                self.compileExpression()
                self.check_and_next(lambda x: x[1] == ')')
                return       
        

        match self.currToken:
            case ('keyword', kw) if kw in ('true', 'false', 'this', 'null'):
                val = 1 if kw == 'true' else 0
                seg = Segment.POINTER if kw == 'this' else Segment.CONSTANT
                self.vmwriter.writePush(seg, val)
                if kw == 'true':
                    self.vmwriter.writeArithmetic(ArithmeticCommand.NEG)
                # self.vmwriter.writeReturn()
                self.cursor += 1


            case ('integerConstant', integer):
                self.vmwriter.writePush(Segment.CONSTANT, int(integer))
                self.cursor += 1


            case ('stringConstant', string):
                self.vmwriter.writePush(Segment.CONSTANT, len(string))
                self.vmwriter.writeCall('String.new', 1)
                for letter in string:
                    self.vmwriter.writePush(Segment.CONSTANT, ord(letter))
                    self.vmwriter.writeCall('String.appendChar', 2)
                self.cursor += 1
                

            case ('identifier', identifier):
                temp = self.tokens[self.cursor + 1]
                match self.tokens[self.cursor + 1]:
                    case ('symbol', '['):
                        kind = self.symtab.kindOf(identifier)
                        index = self.symtab.indexOf(identifier)
                        self.vmwriter.writePush(kind2seg(kind), index)
                        self.cursor += 2
                        # print("array >", self.currToken)
                        self.compileExpression()
                        self.vmwriter.writeArithmetic(ArithmeticCommand.ADD)
                        self.vmwriter.writePop(Segment.POINTER, 1)
                        self.vmwriter.writePush(Segment.THAT, 0)
                        self.check_and_next(lambda x: x[1] == ']')

                    case ('symbol', '('):
                        subroutineName = identifier
                        self.cursor += 1
                        self.check_and_next(lambda x: x == ('symbol', '('))
                        args = self.compileExpressionList()
                        self.check_and_next(lambda x: x == ('symbol', ')'))
                        self.vmwriter.writeCall(f'{subroutineName}', args)
                    case ('symbol', '.'):
                        # TODO handle objects ?
                        self.cursor += 1
                        isMethod = True
                        try:
                            kind = self.symtab.kindOf(identifier)
                            index = self.symtab.indexOf(identifier)
                            type_ = self.symtab.typeOf(identifier)
                        except ValueError:
                            isMethod = False
                        self.check_and_next(lambda x: x == ('symbol', '.'))
                        fnName = self.currToken[1]
                        self.cursor += 1
                        self.check_and_next(lambda x: x == ('symbol', '('))
                        args = self.compileExpressionList()
                        self.check_and_next(lambda x: x == ('symbol', ')'))
                        if isMethod:
                            self.vmwriter.writePush(kind2seg(kind), index) # type: ignore
                            self.vmwriter.writeCall(f'{type_}.{fnName}', args + 1) # type: ignore
                        else:
                            self.vmwriter.writeCall(f'{identifier}.{fnName}', args)


                        # className = identifier
                        # self.cursor += 2
                        # subroutineName = self.currToken[1]
                        # self.cursor += 1
                        # self.check_and_next(lambda x: x == ('symbol', '('))
                        # args = self.compileExpressionList()
                        # self.check_and_next(lambda x: x == ('symbol', ')'))
                        # self.vmwriter.writeCall(f'{self.symtab.typeOf(className)}.{subroutineName}', args + 1)
                    case _:
                        # print('all catch', temp)
                        kind = self.symtab.kindOf(identifier)
                        index = self.symtab.indexOf(identifier)
                        self.vmwriter.writePush(kind2seg(kind), index)
                        self.cursor += 1
                        # print(self.currToken)

    
    def compileExpressionList(self) -> int:
        if self.currToken[1] != ')':
            self.compileExpression()
            expressions = 1
            while self.currToken[1] == ',':
                self.cursor += 1
                self.compileExpression()
                expressions += 1
            return expressions
        return 0
    

    def compileClass(self):
        self.check_and_next(lambda x: x == ('keyword', 'class'))
        if self.currToken[0] == 'identifier':
            self.className = self.currToken[1]
            self.cursor += 1
        else: raise SyntaxError
        self.check_and_next(lambda x: x == ('symbol', '{'))
        
        while self.currToken[0] == 'keyword' and self.currToken[1] in ('static', 'field'):
            self.compileClassVarDec()
        
        while self.currToken[0] == 'keyword' and self.currToken[1] in ('constructor', 'function', 'method'):
            self.symtab.reset()
            self.compileSubroutineDec(self.className)
        
        self.check_and_next(lambda x: x == ('symbol', '}'))

        self.vmwriter.close()