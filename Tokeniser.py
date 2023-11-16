import re

from pathlib import Path
from enum import Enum, auto

class Token(Enum):
    KEYWORD = auto()
    SYMBOL = auto()
    IDENTIFIER = auto()
    INT_CONST = auto()
    STRING_CONST = auto()


def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)
    return regex.sub(_replacer, string)


class JackTokeniser:
    
    symbols = '(){}[].;,+-*/=&|<>~'
    keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

    def __init__(self, fp: str | Path) -> None:
        self.fp = fp
        with open(self.fp) as file:
            self.jackCode = file.read()
        self.clean()
        self.cursor = 0
        self.fileLength = len(self.jackCode)
        self.currToken = ''
    
    def hasMoreTokens(self) -> bool:
        return self.cursor < self.fileLength
    
    def clean(self):
        self.jackCode = remove_comments(self.jackCode)
        self.jackCode = self.jackCode.strip('\n\t ')
    
    def advance(self):
        temp = ''
        nc = self.cursor
        letter = self.jackCode[nc]            
        if (letter) in self.symbols:
            self.currToken = letter
            self.cursor = nc + 1
            return
        while (letter := self.jackCode[nc]) not in self.symbols:
            nc += 1
            whitespace = "\n\t "
            if temp and temp[0] == '"':
                whitespace = "\n"
            if letter in whitespace:
                if temp:
                    break
                else: continue
            temp += letter
        self.currToken = temp
        self.cursor = nc
        if temp == '':
            return self.advance()
    
    def tokenType(self) -> Token:
        if self.currToken in self.symbols: return 'symbol'
        if self.currToken in self.keywords: return 'keyword'
        if self.currToken[0] == '"' and self.currToken[-1] == '"': return 'stringConstant'
        if self.currToken.isdigit(): return 'integerConstant'
        else: return 'identifier'

        
