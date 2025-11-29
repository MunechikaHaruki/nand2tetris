from typing import Literal

class Parser:
    def __init__(self, vm_path: str) -> None:
        with open(vm_path, "r") as fp:
            self.asm = fp.read().split("\n")
        self.order=None
    @property
    def hasMoreLines(self) -> bool:
        return len(self.asm) > 0
    def advance(self) -> None:
        self.order=self.asm.pop(0)
        if self.order.startswith("//") or self.order == "":
            self.order = None

    @property
    def commandType(self) -> Literal["C_ARITHMETIC","C_PUSH","C_POP","C_LABEL","C_GOTO","C_IF","C_FUNCTION","C_RETURN","C_CALL"]:
        """
        現在のコマンドの種類を返す
        """
        if len(self.order.split()) == 1:
            return "C_ARITHMETIC"
        elif len(self.order.split()) == 3:
            if self.order.startswith("push"):
                return "C_PUSH"
            elif self.order.startswith("pop"):
                return "C_POP"
    @property
    def arg1(self) -> str:
        """
        現在のコマンドの最初の引数を返す    C_ARITHMETICの場合、コマンド自体（add, subなど）を返す
        """
        if self.commandType == "C_ARITHMETIC":
            return self.order
        else:
            return self.order.split()[1]
    @property
    def arg2(self) -> int:
        """
        現在のコマンドの2番目の引数を返す   C_PUSH, C_POP, C_FUNCTION, C_CALLのみ呼ぶ
        """
        return int(self.order.split()[2])