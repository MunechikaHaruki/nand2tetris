#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from code_writer import CodeWriter    
import re
from typing import Literal
import os

class Parser:
    def __init__(self, vm_path: str) -> None:
        if os.path.isfile(vm_path):
            with open(vm_path, "r") as fp:
                vm_orders = fp.read().split("\n")
        elif os.path.isdir(vm_path):
            vm_orders = []
            for file in os.listdir(vm_path):
                if file.endswith(".vm"):
                    with open(f"{vm_path}/{file}", "r") as fp:
                        vm_orders += fp.read().split("\n")
        vm_orders = [re.sub(r'//.*', '', order).strip() for order in vm_orders]
        self.vm_orders = [order for order in vm_orders if order != ""]

        print(self.vm_orders)

        self.order=None
    @property
    def hasMoreLines(self) -> bool:
        return len(self.vm_orders) > 0
    def advance(self) -> None:
        self.order=self.vm_orders.pop(0)

    @property
    def commandType(self) -> Literal["C_ARITHMETIC","C_PUSH","C_POP","C_LABEL","C_GOTO","C_IF","C_FUNCTION","C_RETURN","C_CALL"]:
        """
        現在のコマンドの種類を返す
        """
        if len(self.order.split()) == 1:
            if self.order.startswith("return"):
                return "C_RETURN"
            else:
                return "C_ARITHMETIC"
        elif len(self.order.split()) == 3:
            if self.order.startswith("push"):
                return "C_PUSH"
            elif self.order.startswith("pop"):
                return "C_POP"
            elif self.order.startswith("function"):
                return "C_FUNCTION"
            elif self.order.startswith("call"):
                return "C_CALL"
        elif len(self.order.split()) == 2:
            if self.order.startswith("label"):
                return "C_LABEL"
            elif self.order.startswith("goto"):
                return "C_GOTO"
            elif self.order.startswith("if"):
                return "C_IF"

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

class VMTranslator:
    def __init__(self, vm_path: str) -> None:
        self.parser = Parser(vm_path)
        self.code_writer = CodeWriter(vm_path)
    def translate(self) -> None:
        while self.parser.hasMoreLines:
            self.parser.advance()

            if self.parser.commandType == "C_ARITHMETIC":
                self.code_writer.wirteArithmetic(self.parser.arg1)
            elif self.parser.commandType in ["C_PUSH", "C_POP"]:
                self.code_writer.writePushPop(self.parser.commandType, self.parser.arg1, self.parser.arg2)
            elif self.parser.commandType == "C_LABEL":
                self.code_writer.writeLabel(self.parser.arg1)
            elif self.parser.commandType == "C_GOTO":
                self.code_writer.writeGoto(self.parser.arg1)
            elif self.parser.commandType == "C_IF":
                self.code_writer.writeIf(self.parser.arg1)
            elif self.parser.commandType == "C_FUNCTION":
                self.code_writer.writeFunction(self.parser.arg1, self.parser.arg2)
            elif self.parser.commandType == "C_RETURN":
                self.code_writer.writeReturn()
            elif self.parser.commandType == "C_CALL":
                self.code_writer.writeCall(self.parser.arg1, self.parser.arg2)
        self.code_writer.close()

if __name__ == "__main__":
    # コマンドライン引数で入力ファイルの名前を受け取る
    args = sys.argv
    if len(args) < 2:
        print("Enter file name")
        sys.exit()
    VMTranslator(args[1]).translate()