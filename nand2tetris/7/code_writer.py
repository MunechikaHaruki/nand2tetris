import os
from typing import Literal
from dataclasses import dataclass

@dataclass
class PointerInfo:
    symbol: str
    base: int

class CodeWriter:
    def __init__(self, vm_path:str):
        self.asm_file_name = os.path.basename(vm_path).split(".")[0]
        self.fp = open(f"{vm_path.replace('vm', 'asm')}", "w")

        self.pointer_map = {
            "stack": PointerInfo("SP", 256),
            "local": PointerInfo("LCL", 300),
            "argument": PointerInfo("ARG", 400),
            "this": PointerInfo("THIS", 3000),
            "that": PointerInfo("THAT", 3010),
        }
        for k , v in self.pointer_map.items():
            self._write_lines(f"//init {k} pointer", f"@{v.base}", "D=A", f"@{v.symbol}", "M=D") # init pointer
        self.jump_number=0
        
    def _write_lines(self,*lines):
        """ 複数行を書き込む """
        self.fp.write("\n".join(lines) + "\n")
    def _write_stack(self,command:Literal["pop_M","push_true","push_false","push_D","pop_D"]) -> None:
        store=["@SP", "A=M", "M=D"]# スタックポインタの先頭にDを格納
        get=["@SP", "A=M", "D=M"]  # スタックポインタの先頭をDに格納
        inc=["@SP", "M=M+1"]  # スタックポインタをインクリメント
        dec=["@SP", "M=M-1"]  # スタックポインタをデクリメント
        command_map = {
            "pop_M": ["@SP", "AM=M-1"],
            "push_true": ["@SP", "A=M", "M=-1"]+inc,
            "push_false": ["@SP", "A=M", "M=0"]+inc,
            "push_D": store + inc,  
            "pop_D": dec + get
        }
        if command in command_map:
            self._write_lines(*command_map[command])

    def wirteArithmetic(self,command:str) -> None:
        self._write_lines(f"//{command}")
        match command:
            case "add"|"sub"|"and"|"or"|"eq"|"gt"|"lt":
                self._write_stack("pop_D")
                self._write_stack("pop_M")#D,Mレジスタがそれぞれスタックを指すようにする
                if command in ["add","sub","and","or"]:
                    operations={
                        "add": "M=M+D",
                        "sub": "M=M-D",
                        "and": "M=M&D",
                        "or": "M=M|D"
                    }
                    self._write_lines(operations[command])
                    self._write_lines("@SP", "M=M+1")
                elif command in ["eq","gt","lt"]:
                    operations={
                        "eq": "JEQ",
                        "gt": "JGT",
                        "lt": "JLT"
                    }
                    self._write_lines("D=M-D")
                    self._write_lines(f"@TRUE{self.jump_number}")
                    self._write_lines(f"D;{operations[command]}")

                    self._write_stack("push_false")
                    self._write_lines(f"@END{self.jump_number}")
                    self._write_lines("0;JMP")

                    self._write_lines(f"(TRUE{self.jump_number})")
                    self._write_stack("push_true")

                    self._write_lines(f"(END{self.jump_number})")
                    
                    self.jump_number+=1
            case "neg"|"not":
                self._write_stack("pop_M")
                operations={
                    "neg": "M=-M",
                    "not": "M=!M"}
                self._write_lines(operations[command])
                self._write_lines("@SP", "M=M+1")

    def writePushPop(self,command: Literal["C_PUSH","C_POP"] , segment:str, index:int) -> None:
        self._write_lines(f"//{command} {segment} {index}")
        match segment:
            case "constant":
                self._write_lines(f"@{index}", "D=A")
                self._write_stack("push_D")
            case "local"|"argument"|"this"|"that":
                if command == "C_PUSH":
                    self._write_lines(f"@{self.pointer_map[segment].symbol}","D=M")
                    self._write_lines(f"@{index}", "A=D+A")
                    self._write_lines("D=M")#segment[index]の値をDに格納
                    self._write_stack("push_D")#Dをスタックに格納
                elif command == "C_POP":
                    self._write_lines(f"@{self.pointer_map[segment].symbol}","D=M")
                    self._write_lines(f"@{index}", "D=D+A","@SP", "A=M", "M=D")#スタックポインタの先頭にsegment[index]のアドレスを格納
                    self._write_stack("pop_D")
                    self._write_lines("A=A+1","A=M")#Mがsegment[index]を指すようにする
                    self._write_lines("M=D")
            case "temp":
                if command == "C_PUSH":
                    self._write_lines(f"@{5+index}", "D=M")#segment[index]の値をDに格納
                    self._write_stack("push_D")#Dをスタックに格納
                elif command == "C_POP":
                    self._write_stack("pop_D")
                    self._write_lines(f"@{5+index}", "M=D")
            case "pointer":
                if command == "C_PUSH":
                    self._write_lines(f"@{3+index}", "D=M")#segment[index]の値をDに格納
                    self._write_stack("push_D")#Dをスタックに格納
                elif command == "C_POP":
                    self._write_stack("pop_D")
                    self._write_lines(f"@{3+index}", "M=D")
            case "static":
                if command == "C_PUSH":
                    self._write_lines(f"@{self.asm_file_name}.{index}", "D=M")
                    self._write_stack("push_D")
                elif command == "C_POP":
                    self._write_stack("pop_D")
                    self._write_lines(f"@{self.asm_file_name}.{index}", "M=D")
    def close(self) -> None:
        self._write_lines("(END)", "@END", "0;JMP") #infinit loop
        self.fp.close()