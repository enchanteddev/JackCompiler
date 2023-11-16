import sys
from pathlib import Path

from Tokeniser import JackTokeniser

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
            if self.tokeniser.tokenType() == "stringConstant":
                result += f"<{self.tokeniser.tokenType()}> {self.tokeniser.currToken[1:-1]} </{self.tokeniser.tokenType()}>\n"
            else:
                result += f"<{self.tokeniser.tokenType()}> {self.escape(self.tokeniser.currToken)} </{self.tokeniser.tokenType()}>\n"
        with open(save_path, 'w') as f:
            f.write('<tokens>\n')
            f.write(result)
            f.write('</tokens>\n')


J = JackAnalyser(sys.argv[1])
J.tokenise()