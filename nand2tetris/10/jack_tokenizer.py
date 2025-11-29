from const import TokenType,Tokens,Identifier,StringConstant,IntegerConstant
import re

IDENTIFIER_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
INTEGER_PATTERN = re.compile(r'^[0-9]+$')
STRING_PATTERN = re.compile(r'^".*"$')
TOKEN_MAP = {
    'class': Tokens.CLASS,
    'constructor': Tokens.CONSTRUCTOR,
    'function': Tokens.FUNCTION,
    'method': Tokens.METHOD,
    'field': Tokens.FIELD,
    'static': Tokens.STATIC,
    'var': Tokens.VAR,
    'int': Tokens.INT,
    'char': Tokens.CHAR,
    'boolean': Tokens.BOOLEAN,
    'void': Tokens.VOID,
    'true': Tokens.TRUE,
    'false': Tokens.FALSE,
    'null': Tokens.NULL,
    'this': Tokens.THIS,
    'let': Tokens.LET,
    'do': Tokens.DO,
    'if': Tokens.IF,
    'else': Tokens.ELSE,
    'while': Tokens.WHILE,
    'return': Tokens.RETURN,
    '{': Tokens.LEFT_CURLY_BRACKET,
    '}': Tokens.RIGHT_CURLY_BRACKET,
    '(': Tokens.LEFT_ROUND_BRACKET,
    ')': Tokens.RIGHT_ROUND_BRACKET,
    '[': Tokens.LEFT_BOX_BRACKET,
    ']': Tokens.RIGHT_BOX_BRACKET,
    '.': Tokens.DOT,
    ',': Tokens.COMMA,
    ';': Tokens.SEMI_COLON,
    '+': Tokens.PLUS,
    '-': Tokens.MINUS,
    '*': Tokens.MULTI,
    '/': Tokens.DIV,
    '&': Tokens.AND,
    '|': Tokens.PIPE,
    '<': Tokens.LESS_THAN,
    '>': Tokens.GREATER_THAN,
    '=': Tokens.EQUAL,
    '~': Tokens.TILDE,
    '/*': Tokens.COMMENT_START,
    '*/': Tokens.COMMENT_END,
}

class JackTokenizer():
    def __init__(self, filepath):
        self.current_token = None
        self.linenum = 0
        self.remained_line = ''
        self.remained_tokens = []

        self.readfile = open(filepath)

        with open(filepath[:-5] + "T.myImpl.xml", 'w') as writef:
            writef.write('<tokens>\n')
            while 1:
                token = self._parse_next_token()
                if token:
                    elem_name = ''
                    if token.type == TokenType.SYMBOL:
                        elem_name = 'symbol'
                    elif token.type == TokenType.STRING_CONST:
                        elem_name = 'stringConstant'
                    elif token.type == TokenType.KEYWORD:
                        elem_name = 'keyword'
                    elif token.type == TokenType.IDENTIFIER:
                        elem_name = 'identifier'
                    elif token.type == TokenType.INT_CONST:
                        elem_name = 'integerConstant'

                    self.remained_tokens.append(token)
                    writef.write(f"<{elem_name}> {token.token_escaped} </{elem_name}>\n")
                else:
                    break
            writef.write('</tokens>\n')
            # print(self.remained_tokens)
        self.readfile.close()

    def _readline(self):
        self.linenum += 1
        line = self.readfile.readline()
        if line:
            self.remained_line = line.split(Tokens.LINE_COMMENT_START.token)[0].strip()
        else:
            self.remained_line = None

    def _parse_next_token(self):
        while True:
            # read new line
            if self.remained_line == '':
                self._readline()
                if self.remained_line is None:
                    return None
            if self.remained_line:
                return self._pop_token_from_remained_line()

    def _pop_token_from_remained_line(self):
        self.remained_line = self.remained_line.lstrip()
        for i in range(1, len(self.remained_line) + 1):
            t_0 = self._judge_token(self.remained_line[0:i])
            if t_0 == Tokens.COMMENT_START:#コメント開始トークンが見つかった場合
                while 1:
                    end_i = self.remained_line.find(Tokens.COMMENT_END.token)
                    if end_i > -1:#コメント終了トークンが見つかった場合
                        self.remained_line = self.remained_line[end_i + 2:]
                        if len(self.remained_line) > 0:
                            return self._pop_token_from_remained_line()
                        else:
                            self._readline()
                            return self._pop_token_from_remained_line()
                    self._readline()
            if i == len(self.remained_line):
                if self._judge_token(self.remained_line) is not None:
                    self.current_token = self._judge_token(self.remained_line)
                    self.remained_line = ''
                    return self.current_token
                else:
                    raise Exception(f'Unknown token exists at line {self.linenum}')
            else:
                t_1 = self._judge_token(self.remained_line[0:i + 1])
                if t_0 is not None:
                    if t_1 is not None:
                        continue
                    else:
                        self.current_token = t_0
                        self.remained_line = self.remained_line[i:]
                        return self.current_token

    def _judge_token(self, judged_token):
        if judged_token in TOKEN_MAP:
            return TOKEN_MAP[judged_token]
        elif INTEGER_PATTERN.match(judged_token):
            try:
                return IntegerConstant(judged_token)
            except Exception as e:
                raise Exception(f'{e.message} at line {self.linenum}')
        elif IDENTIFIER_PATTERN.match(judged_token):
            return Identifier(judged_token)
        elif STRING_PATTERN.match(judged_token):
            return StringConstant(judged_token[1:-1])
        else:
            return None

    def advance(self):
        if len(self.remained_tokens) > 0:
            self.current_token = self.remained_tokens.pop(0)
        else:
            self.current_token = None
        return self.current_token
    def see_next(self,idx=0):
        if len(self.remained_tokens) > idx:
            return self.remained_tokens[idx]
        else:
            return None