from pathlib import Path
from enum import Enum, auto
from SymbolTable import Kind


class Segment(Enum):
    CONSTANT = auto()
    ARGUMENT = auto()
    LOCAL = auto()
    STATIC = auto()
    THIS = auto()
    THAT = auto()
    TEMP = auto()
    POINTER = auto()


class ArithmeticCommand(Enum):
    ADD = auto()
    SUB = auto()
    NEG = auto()
    EQ = auto()
    GT = auto()
    LT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()


def kind2seg(kind: Kind) -> Segment:
    match kind:
        case Kind.ARG: return Segment.ARGUMENT
        case Kind.VAR: return Segment.LOCAL
        case Kind.STATIC: return Segment.STATIC
        case Kind.FIELD: return Segment.THIS


class VMWriter:
    def __init__(self, fp: Path) -> None:
        self.fp = fp
        self._buffer = ""

    def writePush(self, segment: Segment, index: int):
        self._buffer += f"push {segment.name.lower()} {index}\n"
    

    def writePop(self, segment: Segment, index: int):
        self._buffer += f"pop {segment.name.lower()} {index}\n"
    

    def writeArithmetic(self, command: ArithmeticCommand):
        self._buffer += command.name.lower() + '\n'

    
    def writeLabel(self, label: str):
        self._buffer += f"label {label}\n"


    def writeGoto(self, label: str):
        self._buffer += f"goto {label}\n"


    def writeIf(self, label: str):
        self._buffer += f"if-goto {label}\n"
    

    def writeCall(self, name: str, nArgs: int):
        self._buffer += f"call {name} {nArgs}\n"
    

    def writeFunction(self, name: str, nVars: int):
        self._buffer += f"function {name} {nVars}\n"
    

    def writeReturn(self): self._buffer += "return\n"


    def close(self):
        with open(self.fp, 'w') as of:
            of.write(self._buffer)
