import sys
from pathlib import Path

from Tokeniser import JackTokeniser, Token


def token2string(token: Token) -> str:
    match token:
        case Token.STRING_CONST: return "stringConstant"
        case Token.INT_CONST: return "integerConstant"
        case Token.IDENTIFIER: return "identifier"
        case Token.KEYWORD: return "keyword"
        case Token.SYMBOL: return "symbol"



class JackAnalyser:
    def __init__(self, fp: str | Path) -> None:
        self.fp = Path(fp)
        self.tokeniser = JackTokeniser(self.fp)
        # print(self.tokeniser.jackCode)
    
    def escape(self, text):
        if text == "<": return "&lt;"
        if text == ">": return "&gt;"
        if text == "&": return "&amp;"
        if text == '"': return "&quot;"
        return text
    
    def tokenise(self):
        save_path = self.fp.with_name(self.fp.name + '.new.xml')
        result = ""
        while self.tokeniser.hasMoreTokens():
            self.tokeniser.advance()
            if self.tokeniser.tokenType() == Token.STRING_CONST:
                result += f"<{token2string(self.tokeniser.tokenType())}> {self.tokeniser.currToken[1:-1]} </{token2string(self.tokeniser.tokenType())}>\n"
            else:
                result += f"<{token2string(self.tokeniser.tokenType())}> {self.escape(self.tokeniser.currToken)} </{token2string(self.tokeniser.tokenType())}>\n"
        with open(save_path, 'w') as f:
            f.write('<tokens>\n')
            f.write(result)
            f.write('</tokens>\n')


J = JackAnalyser(sys.argv[1])
J.tokenise()