from const_token import Tokens , Identifier , StringConstant , IntegerConstant , Symbol ,Keyword
from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from typing import Literal,Type
from contextlib import contextmanager
class VmWriter():
    def __init__(self, filepath):
        self.f = open(filepath, 'w')

    def write_code(self, code):
        self.f.write(code + '\n')
    def write_push(self, segment:Literal['constant','argument','local','static','this','that','pointer','temp'], index:str):
        self.write_code(f'push {segment} {int(index)}')
    def write_pop(self, segment:Literal['constant','argument','local','static','this','that','pointer','temp'], index:str):
        self.write_code(f'pop {segment} {index}')
    def write_arithmetic(self, command:Literal['add','sub','neg','eq','gt','lt','and','or','not']):
        self.write_code(command)
    def write_label(self, label):
        self.write_code(f'label {label}')
    def write_goto(self, label):
        self.write_code(f'goto {label}')
    def write_if(self, label):
        self.write_code(f'if-goto {label}')
    def write_call(self, name, n_args):
        self.write_code(f'call {name} {n_args}')
    def write_function(self,name,locals):
        self.write_code(f'function {name} {locals}')
    def write_return(self):
        self.write_code('return')

class CompilationEngine():
    def __init__(self, filepath):
        self.wf = open(filepath[:-5] + ".myImpl.xml", 'w')
        self.vmw=VmWriter(filepath[:-5]+".myImpl.vm")
        self.symbol_table=SymbolTable()
        self.tokenizer = JackTokenizer(filepath)
        self.label_num_if=0
        self.label_num_while=0
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wf.close()
        self.vmw.f.close()
    def compile(self):
        self.compile_class()
    def write_token_element(self, elem_name, value):
        self.wf.write(f'<{elem_name}> {value} </{elem_name}>\n')
    @staticmethod
    def write_element(tag_name):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                self.wf.write(f'<{tag_name}>\n')
                result = func(self, *args, **kwargs)
                self.wf.write(f'</{tag_name}>\n')
                return result
            return wrapper
        return decorator

    @write_element('class')
    def compile_class(self):
        self.compile_pre_determined(tokentype=Keyword,verify_token=Tokens.CLASS)
        self.compile_identifier(category='class')
        self.compiled_cls_name=self.tokenizer.current_token.token
        with self.compile_backet(backet_type=r'{}'):
            while self.next_is([Tokens.STATIC, Tokens.FIELD]):
                self.compile_class_var_dec()
            while self.next_is([Tokens.CONSTRUCTOR, Tokens.FUNCTION, Tokens.METHOD]):
                self.compile_subroutine_dec()

    @write_element('classVarDec')
    def compile_class_var_dec(self):
        str_var_kind=self.tokenizer.see_next().token
        self.compile_pre_determined(tokentype=Keyword)
        str_var_type=self.tokenizer.see_next().token
        self.compile_type()
        self.compile_identifier(category=str_var_kind,identifier_type=str_var_type)
        while self.next_is(Tokens.COMMA):
            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.COMMA)
            self.compile_identifier(category=str_var_kind)
        self.compile_pre_determined(tokentype=Symbol)

    @write_element('subroutineDec')
    def compile_subroutine_dec(self):
        self.symbol_table.start_subroutine()
        self.compile_pre_determined(tokentype=Keyword)  # method, constructor, function
        self.routine_type = self.tokenizer.current_token
        if self.tokenizer.see_next() == Tokens.VOID:
            self.compile_pre_determined(tokentype=Keyword, verify_token=Tokens.VOID)
        else:
            self.compile_type()
        self.compile_identifier(category='subroutine')
        self.compiled_subroutine_name = self.tokenizer.current_token.token

        if self.routine_type == Tokens.METHOD:
            self.symbol_table.define(name='this', identifier_type=self.compiled_cls_name, kind='arg')

        with self.compile_backet(backet_type='()'):
            self.compile_parameter_list()
        self.compile_subroutine_body()

    @write_element('parameterList')
    def compile_parameter_list(self):
        if self.tokenizer.see_next() in [Tokens.INT, Tokens.CHAR, Tokens.BOOLEAN] or isinstance(
                self.tokenizer.see_next(), Identifier):
            self.compile_type()
            self.compile_identifier(category='arg')

            while self.next_is(Tokens.COMMA):
                self.compile_pre_determined(tokentype=Symbol)
                self.compile_type()
                self.compile_identifier(category='arg')

    @write_element('subroutineBody')
    def compile_subroutine_body(self):
        local_num=0
        with self.compile_backet(backet_type=r'{}'):
            while self.next_is(Tokens.VAR):
                local_num+=self.compile_var_dec()
            self.vmw.write_function(f'{self.compiled_cls_name}.{self.compiled_subroutine_name}',local_num)
            if self.routine_type == Tokens.METHOD:
                self.vmw.write_push("argument", 0)
                self.vmw.write_pop("pointer", 0)
            if self.routine_type == Tokens.CONSTRUCTOR:
                field_count = self.symbol_table.var_count('field')
                self.vmw.write_push('constant', field_count)
                self.vmw.write_call('Memory.alloc', 1)
                self.vmw.write_pop('pointer', 0)

            self.compile_statements()

    @write_element('varDec')
    def compile_var_dec(self):
        var_num=0
        self.compile_pre_determined(tokentype=Keyword,verify_token=Tokens.VAR)
        Identifier_type=self.tokenizer.see_next().token
        self.compile_type()
        self.compile_identifier(category='var',identifier_type=Identifier_type)
        var_num +=1
        while self.next_is(Tokens.COMMA):
            self.compile_pre_determined(tokentype=Symbol)
            self.compile_identifier(category='var',identifier_type=Identifier_type)
            var_num+=1
        self.compile_pre_determined(tokentype=Symbol)
        return var_num

    @write_element('statements')
    def compile_statements(self):
        while self.next_is([Tokens.LET, Tokens.IF, Tokens.WHILE, Tokens.DO, Tokens.RETURN]):
            self.compile_statement()

    
    @write_element('letStatement')
    def compileLet(self):
        self.compile_pre_determined(tokentype=Keyword,verify_token=Tokens.LET)
        self.compile_identifier(need_symbol_table=True)
        let_var=self.tokenizer.current_token.token#unimplemented
        kind_map={
            'var':'local',
            'arg':'argument',
            'field':'this',
            'static':'static'
        }
        segment=kind_map[self.symbol_table.kind_of(let_var)]
        if self.next_is(Tokens.LEFT_BOX_BRACKET):
            with self.compile_backet(backet_type='[]'):
                self.compile_expression()
                self.vmw.write_push(segment,self.symbol_table.index_of(let_var))
                self.vmw.write_arithmetic('add')
            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.EQUAL)

            self.compile_expression()
            self.vmw.write_pop('temp', 0)
            self.vmw.write_pop('pointer', 1)
            self.vmw.write_push('temp', 0)
            self.vmw.write_pop('that', 0)

            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.SEMI_COLON)
        else:
            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.EQUAL)
            self.compile_expression()
            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.SEMI_COLON)
            self.vmw.write_pop(segment,self.symbol_table.index_of(let_var))
    @write_element('ifStatement')
    def compileIf(self):
        self.compile_pre_determined(tokentype=Keyword,verify_token=Tokens.IF)
        with self.compile_backet(backet_type='()'):
            self.compile_expression()
        l_true = f'IF_TRUE{self.label_num_if}'
        l_false = f'IF_FALSE{self.label_num_if}'
        l_end=f'IF_END{self.label_num_if}'
        self.label_num_if+=1
        # if self.label_num_if==2:
        #     self.label_num_if=0

        self.vmw.write_if(l_true)
        self.vmw.write_goto(l_false)
        with self.compile_backet(backet_type=r'{}'):
            self.vmw.write_label(l_true)
            self.compile_statements()
            self.vmw.write_goto(l_end)
            self.vmw.write_label(l_false)
        if self.next_is(Tokens.ELSE):
            self.compile_pre_determined(tokentype=Keyword)
            with self.compile_backet(backet_type=r'{}'):
                self.compile_statements()
        self.vmw.write_label(l_end)
    
    @write_element('whileStatement')
    def compileWhile(self):
        self.compile_pre_determined(tokentype=Keyword,verify_token=Tokens.WHILE)
        l1=f'WHILE_EXP{self.label_num_while}'
        l2=f'WHILE_END{self.label_num_while}'
        self.label_num_while+=1
        # if self.label_num_while==1:
        #     self.label_num_while=0
        with self.compile_backet(backet_type='()'):
            self.vmw.write_label(l1)
            self.compile_expression()
            self.vmw.write_arithmetic('not')
            self.vmw.write_if(l2)
        with self.compile_backet(backet_type=r'{}'):
            self.compile_statements()
            self.vmw.write_goto(l1)
        self.vmw.write_label(l2)
    
    @write_element('doStatement')
    def compileDo(self):
        self.compile_pre_determined(tokentype=Keyword,verify_token=Tokens.DO)
        self.compile_subroutine_call()
        self.compile_pre_determined(tokentype=Symbol)
        self.vmw.write_pop('temp',0)
    @write_element('returnStatement')
    def compileReturn(self):
        self.compile_pre_determined(tokentype=Keyword)
        if not self.next_is(Tokens.SEMI_COLON):
            self.compile_expression()
        else:
            self.vmw.write_push('constant',0)
        self.compile_pre_determined(tokentype=Symbol)
        self.vmw.write_return()        


    def compile_statement(self):
        if self.next_is(Tokens.LET):
            self.compileLet()
        elif self.next_is(Tokens.IF):
            self.compileIf()
        elif self.next_is(Tokens.WHILE):
            self.compileWhile()
        elif self.next_is(Tokens.DO):
            self.compileDo()
        elif self.next_is(Tokens.RETURN):
            self.compileReturn()

    def compile_subroutine_call(self):   
        if self.next_is(Tokens.LEFT_ROUND_BRACKET, idx=1):
            method_name=self.tokenizer.see_next(idx=0).token
            self.compile_identifier(category='subroutine')
            self.vmw.write_push('pointer',0)
            with self.compile_backet(backet_type='()'):
                args=self.compile_expression_list()+1
            self.vmw.write_call(f"{self.compiled_cls_name}.{method_name}",args)
        elif self.next_is(Tokens.DOT, idx=1):
            clsOrVarName=self.tokenizer.see_next().token
            subroutineName=self.tokenizer.see_next(idx=2).token
            # print(subroutineName)
            kind=self.symbol_table.kind_of(clsOrVarName)
            if kind is not None:#varName メソッドの呼び出し
                self.compile_identifier(need_symbol_table=True)

                self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.DOT)
                self.compile_identifier(category='subroutine')

                self.vmw.write_push(self.kind_to_segment(kind),self.symbol_table.index_of(clsOrVarName))
                with self.compile_backet(backet_type='()'):
                    args=self.compile_expression_list()+1
                self.vmw.write_call(f"{self.symbol_table.type_of(clsOrVarName)}.{subroutineName}",args)
            elif kind is None:#clsName
                self.compile_identifier(category='class')
                self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.DOT)
                self.compile_identifier(category='subroutine')
                with self.compile_backet(backet_type='()'):
                    args=self.compile_expression_list()
                self.vmw.write_call(f"{clsOrVarName}.{subroutineName}",args)

    def kind_to_segment(self, kind):
        kind_map = {
            'var': 'local',
            'arg': 'argument',
            'field': 'this',
            'static': 'static'
        }
        return kind_map[kind]

    @write_element('expressionList')
    def compile_expression_list(self):
        i=0
        if not self.next_is(Tokens.RIGHT_ROUND_BRACKET):
            self.compile_expression()
            i+=1
            while self.next_is(Tokens.COMMA):
                self.compile_pre_determined(tokentype=Symbol)
                self.compile_expression()
                i+=1
        return i

    @write_element('expression')
    def compile_expression(self):
        self.compile_term()
        while self.next_is([
            Tokens.PLUS,
            Tokens.MINUS,
            Tokens.MULTI,
            Tokens.DIV,
            Tokens.AND,
            Tokens.PIPE,
            Tokens.LESS_THAN,
            Tokens.GREATER_THAN,
            Tokens.EQUAL]):
            self.compile_pre_determined(tokentype=Symbol)
            op_token=self.tokenizer.current_token
            self.compile_term()
            if op_token == Tokens.PLUS:
                self.vmw.write_arithmetic('add')
            elif op_token == Tokens.MINUS:
                self.vmw.write_arithmetic('sub')
            elif op_token == Tokens.MULTI:
                self.vmw.write_call('Math.multiply', 2)
            elif op_token == Tokens.DIV:
                self.vmw.write_call('Math.divide', 2)
            elif op_token == Tokens.AND:
                self.vmw.write_arithmetic('and')
            elif op_token == Tokens.PIPE:
                self.vmw.write_arithmetic('or')
            elif op_token == Tokens.LESS_THAN:
                self.vmw.write_arithmetic('lt')
            elif op_token == Tokens.GREATER_THAN:
                self.vmw.write_arithmetic('gt')
            elif op_token == Tokens.EQUAL:
                self.vmw.write_arithmetic('eq')

    @write_element('term')
    def compile_term(self):
        if isinstance(self.tokenizer.see_next(),IntegerConstant):
            self.compile_integer_constant()
            self.vmw.write_push('constant',self.tokenizer.current_token.token)
        elif isinstance(self.tokenizer.see_next(),StringConstant):
            self.compile_string_constant()
        elif self.next_is([Tokens.NULL, Tokens.THIS, Tokens.TRUE, Tokens.FALSE]):
            self.compile_pre_determined(tokentype=Keyword)
            if self.tokenizer.current_token == Tokens.TRUE:
                self.vmw.write_push('constant',0)
                self.vmw.write_arithmetic('not')
            if self.tokenizer.current_token == Tokens.FALSE:
                self.vmw.write_push('constant',0)
            if self.tokenizer.current_token == Tokens.THIS:
                self.vmw.write_push('pointer',0)
            if self.tokenizer.current_token == Tokens.NULL:
                self.vmw.write_push('constant',0)
        elif isinstance(self.tokenizer.see_next(),Identifier):
            if self.next_is(Tokens.LEFT_BOX_BRACKET, idx=1):
                self.compile_identifier(need_symbol_table=True,write_push=True)
                with self.compile_backet(backet_type='[]'):
                    self.compile_expression()
                    self.vmw.write_arithmetic('add')
                    self.vmw.write_pop('pointer',1)
                    self.vmw.write_push('that',0)
            elif self.next_is([Tokens.LEFT_ROUND_BRACKET, Tokens.DOT], idx=1):#subroutineCall
                self.compile_subroutine_call()
            else:
                self.compile_identifier(need_symbol_table=True,write_push=True)#varName

        elif self.next_is(Tokens.LEFT_ROUND_BRACKET):
            with self.compile_backet('()'):
                self.compile_expression()
        elif self.next_is(Tokens.TILDE):
            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.TILDE)
            self.compile_term()
            self.vmw.write_arithmetic('not')
        elif self.next_is(Tokens.MINUS):
            self.compile_pre_determined(tokentype=Symbol,verify_token=Tokens.MINUS)
            self.compile_term()
            self.vmw.write_arithmetic('neg')

        
        else:
            raise Exception('')

    def compile_type(self):
        if self.next_is([Tokens.INT, Tokens.CHAR, Tokens.BOOLEAN]):
            self.compile_pre_determined(tokentype=Keyword)
        elif isinstance(self.tokenizer.see_next(), Identifier):
            self.compile_identifier(category='class')

    def next_is(self, tokens, idx=0):
        if type(tokens) is list:
            return self.tokenizer.see_next(idx=idx) in tokens
        else:
            return self.tokenizer.see_next(idx=idx) == tokens
    
    def advance_token(self,type=Literal[Symbol,Keyword,IntegerConstant,StringConstant,Identifier]):
        self.tokenizer.advance()
        if not isinstance(self.tokenizer.current_token,type):
            raise Exception("Type Error")

    @contextmanager
    def compile_backet(self,backet_type=Literal['()',r'{}','[]']):
        match backet_type:
            case '()':
                left_backet=Tokens.LEFT_ROUND_BRACKET
                right_backet=Tokens.RIGHT_ROUND_BRACKET
            case r'{}':
                left_backet=Tokens.LEFT_CURLY_BRACKET
                right_backet=Tokens.RIGHT_CURLY_BRACKET
            case '[]':
                left_backet=Tokens.LEFT_BOX_BRACKET
                right_backet=Tokens.RIGHT_BOX_BRACKET
        self.compile_pre_determined(tokentype=Symbol,verify_token=left_backet)
        yield
        self.compile_pre_determined(tokentype=Symbol,verify_token=right_backet)

    def compile_integer_constant(self):
        self.advance_token(type=IntegerConstant)
        token=self.tokenizer.current_token
        self.write_token_element(token.token_type,token.token_escaped)

    def compile_pre_determined(self,tokentype:Type[Keyword | Symbol],verify_token=None):
        self.advance_token(type=tokentype)
        token=self.tokenizer.current_token
        if verify_token is not None and verify_token is not token:
            raise Exception(f'Unexpected Token Error verify_token:{verify_token.token} token:{token.token}')
        self.write_token_element(token.token_type,token.token_escaped)


    def compile_string_constant(self):
        self.advance_token(type=StringConstant)
        token=self.tokenizer.current_token
        string=self.tokenizer.current_token.token
        self.write_token_element(token.token_type, string)
        self.vmw.write_push('constant', len(string))
        self.vmw.write_call('String.new', 1)
        for c in string:
            self.vmw.write_push('constant', ord(c))
            self.vmw.write_call('String.appendChar', 2)

    def compile_identifier(self,category='not_setted',identifier_type='not_setted',need_symbol_table=False,write_push=False):
        self.advance_token(type=Identifier)
        identifier= self.tokenizer.current_token.token_escaped
        if need_symbol_table is False:
            self.write_token_element(f'identifier category=\"{category}\" ',identifier)
            if category in ['field','static','var','arg']:
                self.symbol_table.define(name=self.tokenizer.current_token.token_escaped,identifier_type=identifier_type,kind=category)
        elif need_symbol_table is True:
            category=self.symbol_table.kind_of(identifier)
            self.write_token_element(f'identifier category= \"{category}\"', identifier)
            if write_push is True:
                kind_map={
                    'var':'local',
                    'arg':'argument',
                    'field':'this',
                    'static':'static'
                }
                self.vmw.write_push(kind_map[category],self.symbol_table.index_of(identifier))