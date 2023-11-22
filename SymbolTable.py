class BaseSymbolTable:
    def __init__(self):
        self.table = {
            "name": [],
            "type": [],
            "kind": [],
            "index": []
        }
    
    def define(self, name: str, type_: str, kind: str):
        self.table["name"].append(name)
        self.table["type"].append(type_)
        self.table["kind"].append(kind)
        self.table["index"].append(self.table["kind"].count(kind) + 1)
    
    def reset(self):
        for col in self.table:
            self.table[col] = []



class SymbolTable:
    def __init__(self):
        self.class_table = BaseSymbolTable()
        self.subroutine_table = BaseSymbolTable()
    
    def define(self, name: str, type_: str, kind: str):
        if kind in ("static", "field"):
            self.class_table.define(name, type_, kind)
        else:
            self.subroutine_table.define(name, type_, kind)
    
    def varCount(self, kind: str):
        if kind in ("static", "field"):
            self.class_table.table["kind"].count(kind)
        else:
            self.subroutine_table.table["kind"].count(kind)
    

    def attrOf(self, name: str, attr: str):
        try:
            return self.class_table.table[attr][self.class_table.table["name"].index(name)]
        except ValueError:
            return self.subroutine_table.table[attr][self.subroutine_table.table["name"].index(name)]
    

    def typeOf(self, name: str): return self.attrOf(name, "type")
    def kindOf(self, name: str): return self.attrOf(name, "kind")
    def indexOf(self, name: str): return self.attrOf(name, "index")

    def reset(self):
        self.subroutine_table.reset()