class Token:
    def __init__(self, token, token_escaped=None):
        self.token = token
        if token_escaped:
            self.token_escaped = token_escaped
        else:
            self.token_escaped = token
class Symbol(Token):
    token_type='symbol'
class Keyword(Token):
    token_type='keyword'
class Identifier(Token):
    token_type='identifier'
class IntegerConstant(Token):
    token_type='integerConstant'
    def __init__(self, token):
        Token.__init__(self, int(token))
        if self.token > 32767:
            raise Exception('too large integer')
class StringConstant(Token):
    token_type='stringConstant'

class Tokens:
    CLASS = Keyword('class')
    METHOD = Keyword('method')
    FUNCTION = Keyword('function')
    CONSTRUCTOR = Keyword('constructor')
    INT = Keyword('int')
    BOOLEAN = Keyword('boolean')
    CHAR = Keyword('char')
    VOID = Keyword('void')
    VAR = Keyword('var')
    STATIC = Keyword('static')
    FIELD = Keyword('field')
    LET = Keyword('let')
    DO = Keyword('do')
    IF = Keyword('if')
    ELSE = Keyword('else')
    WHILE = Keyword('while')
    RETURN = Keyword('return')
    TRUE = Keyword('true')
    FALSE = Keyword('false')
    NULL = Keyword('null')
    THIS = Keyword('this')

    LEFT_CURLY_BRACKET = Symbol('{')
    RIGHT_CURLY_BRACKET = Symbol('}')
    LEFT_ROUND_BRACKET = Symbol('(')
    RIGHT_ROUND_BRACKET = Symbol(')')
    LEFT_BOX_BRACKET = Symbol('[')
    RIGHT_BOX_BRACKET = Symbol(']')
    DOT = Symbol('.')
    COMMA = Symbol(',')
    SEMI_COLON = Symbol(';')
    PLUS = Symbol('+')
    MINUS = Symbol('-')
    MULTI = Symbol('*')
    DIV = Symbol('/')
    AND = Symbol('&', token_escaped='&amp;')
    PIPE = Symbol('|')
    LESS_THAN = Symbol('<', token_escaped='&lt;')
    GREATER_THAN = Symbol('>', token_escaped='&gt;')
    EQUAL = Symbol('=')
    TILDE = Symbol('~')

    COMMENT_START = Symbol('/*')
    COMMENT_END = Symbol('*/')
    LINE_COMMENT_START = Symbol('//')