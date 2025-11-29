#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from parser import Parser
from code_writer import CodeWriter    

class VMTranslator:
    def __init__(self, vm_path: str) -> None:
        self.parser = Parser(vm_path)
        self.code_writer = CodeWriter(vm_path)
    def translate(self) -> None:
        while self.parser.hasMoreLines:
            self.parser.advance()
            if self.parser.order is None:
                continue
            if self.parser.commandType == "C_ARITHMETIC":
                self.code_writer.wirteArithmetic(self.parser.arg1)
            elif self.parser.commandType in ["C_PUSH", "C_POP"]:
                self.code_writer.writePushPop(self.parser.commandType, self.parser.arg1, self.parser.arg2)
        self.code_writer.close()

def main():
    # コマンドライン引数で入力ファイルの名前を受け取る
    args = sys.argv
    if len(args) < 2:
        print("ファイル名を入力してください。")
        return
    vm_path = args[1]

    vmtranslator = VMTranslator(vm_path)
    vmtranslator.translate()

if __name__ == "__main__":
    main()