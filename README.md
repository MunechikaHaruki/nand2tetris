# Nand2Tetris Projects (Chapters 7, 8, 10, 11)

書籍『[コンピュータシステムの理論と実装](https://www.oreilly.co.jp/books/9784814400874/)』(Nand2Tetris) の第7, 8章および第10, 11章の実装です。

高水準言語（Jack）から、Hackプラットフォーム上で動作するアセンブリ言語までの変換を行うコンパイラ群を実装しました。

## 構成
* **Chapter 7, 8 (VM Translator)**
    * VMコード（中間コード）からアセンブリ言語へ変換するトランスレータ
* **Chapter 10, 11 (Jack Compiler)**
    * Jack言語（高水準言語）からVMコード（中間コード）へ変換するコンパイラ

## References
本実装にあたり、以下のリポジトリを参考にさせていただきました。
* https://github.com/ikenox/nand2tetris