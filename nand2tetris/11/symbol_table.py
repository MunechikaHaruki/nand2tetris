from typing import Literal

class Identifier:
    def __init__(self, identifier_type, index):
        self.type = identifier_type
        self.index = index
class SymbolTable:
    def __init__(self):
        self.tables={
            'var':{},
            'arg':{},
            'field':{},
            'static':{}
        }
    def define(self, name, identifier_type, kind:Literal['field','static','var','arg']):
        table=self.tables[kind]
        table[name] = Identifier(identifier_type, self.var_count(kind))
    def start_subroutine(self):
        self.tables['arg'] = {}
        self.tables['var'] = {}
    def var_count(self, kind):
        return len(self.tables[kind])
    def kind_of(self, name):
        for kind,kind_table in self.tables.items():
            for _name,identifier in kind_table.items():
                if _name==name:
                    return kind
    def type_of(self, name):
        kind=self.kind_of(name)
        return self.tables[kind][name].type
    def index_of(self, name):
        kind=self.kind_of(name)
        return self.tables[kind][name].index