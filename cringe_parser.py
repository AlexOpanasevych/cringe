class CringeParser:
    # error codes

    ERR_TOKEN_MISMATCH = 1  # token mismatch
    ERR_GET_SYMB = 2  # token mismatch
    ERR_UNEXP_END_OF_PROG = 3  # token mismatch
    ERR_INSTR_MISMATCH = 4  # token mismatch
    ERR_EXP_FACTOR_MISMATCH = 5  # token mismatch
    ERR_BOOL_EXPR_MISMATCH = 6  # token mismatch

    def __init__(self, table_of_tokens: dict[int, tuple]):
        self.table_of_tokens = table_of_tokens
        self.num_row = 1
        self.token_count = len(table_of_tokens)
        self.postfix_notation = []

    def parse_token(self, lexeme, token, ident):
        if self.num_row > self.token_count:
            self.fail_parse(self.ERR_UNEXP_END_OF_PROG, (lexeme, token, self.num_row))

        line_num, lex, tok = self.get_symb()
        self.num_row += 1

        if (lex, tok) == (lexeme, token):
            print(ident + 'parseToken: В рядку {0} токен {1}'.format(line_num, (lexeme, token)))
            return True
        else:
            self.fail_parse(self.ERR_TOKEN_MISMATCH, (line_num, lex, tok, lexeme, token))
            return False

    def get_symb(self):
        return self.get_row(self.num_row)

    def parse_statement_list(self):
        print('\t parseStatementList():')
        if self.parse_statement():
            self.parse_statement_list()
        return True

    def parse_statement(self):
        print('\t\t parseStatement():')
        num_line, lex, tok = self.get_symb()
        if tok == 'ident':
            self.parse_assign()
            return True

        # якщо лексема - ключове слово 'if'
        # обробити інструкцію розгалудження
        elif (lex, tok) == ('if', 'keyword'):
            self.parse_if()
            return True
        
        elif (lex, tok) == ('for', 'keyword'):
            self.parse_for()
            return True
            
        elif (lex, tok) == ('print', 'keyword'):
            self.parse_print()
            return True
        elif (lex, tok) == ('scan', 'keyword'):
            self.parse_scan()
            return True
        elif lex in ('integer', 'real', 'boolean') and tok == 'keyword':
            self.parse_declaration()
            return True
        elif (lex, tok) == (';', 'op_end'):
            self.num_row += 1
            return True
        elif (lex, tok) == ('}', 'end_block'):
            return False
        else:
            # жодна з інструкцій не відповідає
            # поточній лексемі у таблиці розбору,
            # self.fail_parse(self.ERR_INSTR_MISMATCH, (num_line, lex, tok, 'ident або if'))
            return False

    def fail_parse(self, error_code, what: tuple):
        if error_code == self.ERR_UNEXP_END_OF_PROG:
            (lexeme, token, num_row) = what
            print(
                'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
                'номером {1}. \n\t Очікувалось - {0}'.format(
                    (lexeme, token), num_row))
        if error_code == self.ERR_GET_SYMB:
            (num_row) = what
            print(
                'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
                'номером {0}. \n\t Останній запис - {1}'.format(
                    num_row, self.table_of_tokens[num_row - 1]))
        elif error_code == self.ERR_TOKEN_MISMATCH:
            (num_line, lexeme, token, lex, tok) = what
            print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
                num_line, lexeme, token, lex, tok))
        elif error_code == self.ERR_INSTR_MISMATCH:
            (num_line, lex, tok, expected) = what
            print(
                'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(num_line,
                                                                                                               lex, tok,
                                                                                                               expected))
        elif error_code == self.ERR_EXP_FACTOR_MISMATCH:
            (num_line, lex, tok, expected) = what
            print(
                'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(num_line,
                                                                                                               lex, tok,
                                                                                                               expected))
        elif error_code == self.ERR_BOOL_EXPR_MISMATCH:
            (num_line,lex,tok, expected) = what
            print(
                'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(num_line,
                                                                                                               lex, tok,
                                                                                                               expected))

        exit(error_code)

    def parse_assign(self):
        print('\t' * 4 + 'parseAssign():')

        # взяти поточну лексему
        num_line, lex, tok = self.get_symb()

        # встановити номер нової поточної лексеми
        self.num_row += 1

        print('\t' * 5 + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
        # якщо була прочитана лексема - '='
        if self.parse_token('=', 'assign_op', '\t' * 5):
            # розібрати арифметичний вираз
            self.parse_expression()
            return True
        else:
            return False

    def parse_expression(self):
        print('\t' * 5 + 'parseExpression():')
        self.parse_arithm_expression()
        self.parse_bool_expr()
        return True

    def parse_term(self):
        print('\t' * 6 + 'parseTerm():')
        self.parse_factor()
        # продовжувати розбирати Множники (Factor)
        # розділені лексемами '*' або '/'
        # while F:
        numLine, lex, tok = self.get_symb()
        if tok == 'mult_op':
            self.num_row += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            self.parse_term()
        if (lex, tok) == ('^', 'pow_op'):
            self.num_row += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            self.parse_term()
            # else:
            #     F = False
        return True

    def parse_factor(self):
        print('\t' * 7 + 'parseFactor():')
        num_line, lex, tok = self.get_symb()
        print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lex, tok):{1}'.format(num_line, (lex, tok)))

        # перша і друга альтернативи для Factor
        # якщо лексема - це константа або ідентифікатор
        if tok in ('integer', 'real', 'ident'):
            self.num_row += 1
            print('\t' * 7 + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))

        # третя альтернатива для Factor
        # якщо лексема - це відкриваюча дужка
        elif lex == '(':
            self.num_row += 1
            self.parse_arithm_expression()
            self.parse_token(')', 'par_op', '\t' * 7)
            print('\t' * 7 + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
        else:
            self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'rel_op, integer, real, ident або \'(\' Expression \')\''))
        return True

    def parse_if(self):
        _, lex, tok = self.get_symb()
        if lex == 'if' and tok == 'keyword':
            self.num_row += 1
            self.parse_expression()
            self.parse_token('then', 'keyword', '\t' * 5)
            self.parse_statement_list()
            self.parse_token('fi', 'keyword', '\t' * 5)
            # self.parse_statement()
            # self.parse_token('endif', 'keyword', '\t' * 5)
            return True
        else:
            return False

    def parse_bool_expr(self):
        # self.parse_arithm_expression()
        num_line, lex, tok = self.get_symb()
        if tok in 'rel_op':
            print('\t' * 6 + 'parse_bool_expr: ' + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
            self.num_row += 1
            self.parse_arithm_expression()
            self.parse_bool_expr()
            self.postfix_notation.append((lex, tok, None))
            return True
            # print('\t' * 5 + f'в рядку {num_line} - {(lex, tok)}')

        # elif required:
        #     self.fail_parse(self.ERR_BOOL_EXPR_MISMATCH, (num_line, lex, tok, 'rel_op'))
        else:
            return False

    def parse_program(self):
        try:
            self.parse_token('program', 'keyword', '')
            self.parse_token('{', 'start_block', '')
            self.parse_statement_list()
            self.parse_token('}', 'end_block', '')
            print('Parser: Синтаксичний аналіз завершився успішно')
            return True
        except SystemExit as e:
            # Повідомити про факт виявлення помилки
            print('Parser: Аварійне завершення програми з кодом {0}'.format(e))

    def parse_for(self):
        num_line, lex, tok = self.get_symb()
        if (lex, tok) == ('for', 'keyword'):
            self.num_row += 1
            # self.parse_token('(', 'brackets_op', '\t' * 5)
            # self.num_row += 1
            # num_line, lex, tok = self.get_symb()
            # self.num_row += 1
            # if tok == 'ident':
            self.parse_assign()
            self.parse_token('by', 'keyword', '')
            # self.parse_token(';', 'punct', '\t' * 5)
            self.parse_expression()
            # self.parse_token(';', 'punct', '\t' * 5)
            self.parse_token('while', 'keyword', '')
            self.parse_expression()
            self.parse_token('do', 'keyword', '\t' * 5)
            # self.parse_token('{', 'curve_brackets_op', '\t' * 5)
            self.parse_statement()
            # self.parse_token('}', 'curve_brackets_op', '\t' * 5)
            return True
        else:
            return False

    def parse_print(self):
        _, lex, tok = self.get_symb()
        if (lex, tok) == ('print', 'keyword'):
            self.num_row += 1
            self.parse_token('(', 'par_op', '\t' * 5)
            self.parse_factor()
            self.parse_inner_print()
            self.parse_token(')', 'par_op', '\t' * 5)
            return True
        else:
            return False

    def parse_inner_print(self):
        _, lex, tok = self.get_symb()
        if(lex, tok) == (',', 'punct'):

            self.num_row += 1
            self.parse_factor()
            self.parse_inner_print()
            return True
        else:
            return False

    def parse_scan(self):
        _, lex, tok = self.get_symb()
        if (lex, tok) == ('scan', 'keyword'):
            self.num_row += 1
            # self.parse_factor()
            self.parse_token('(', 'par_op', '\t' * 5)
            self.parse_var_list()
            self.parse_token(')', 'par_op', '\t' * 5)
            return True
        else:
            return False

    def parse_declaration(self):
        num_line, lex, tok = self.get_symb()
        self.num_row += 1
        if lex in ('integer', 'real', 'boolean') and tok == 'keyword':

            self.parse_var_init_list(lex)
            self.parse_token(';', 'op_end', '')

        else:
            self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
                           (num_line, lex, tok, 'integer, real, boolean, ident або \'(\' Expression \')\''))

    def parse_arithm_expression(self):
        self.parse_term()
        # while True:
        num_line, lex, tok = self.get_symb()
        if tok in 'add_op':
            self.num_row += 1
            print('\t' * 6 + 'parse_arithm_expression: ' + f'в рядку {num_line} - {(lex, tok)}')
            self.parse_arithm_expression()
            self.postfix_notation.append((lex, tok, None))
            # if self.to_view:
            #     self.print_translator_step(lex)
        return True

    def parse_var_init_list(self, var_type):
        num_line, lex, tok = self.get_symb()
        # prev_num_line, prev_lex, prev_tok = self.get_row(self.num_row - 1)
        self.num_row += 1

        if tok == 'ident': # or (prev_lex == ',' and prev_tok == 'punct'): # tok == ident
            print('\t' * 5 + f'в рядку {num_line} - {(lex, tok)}')
            self.postfix_notation.append((lex, tok, var_type))
            pass
        else:
            self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'bracket_op, int, float, bool, ident або \'(\' Expression \')\''))
        num_line, lex, tok = self.get_symb()
        if lex == '=' and tok == 'assign_op':
            self.get_back()
            self.parse_assign()
            # self.parse_var_list(var_type)

        num_line, lex, tok = self.get_symb()
        # if lex == ';' and tok == 'op_end':
        #     return True
        if lex == ',' and tok == 'punct':
            self.num_row += 1
            self.parse_var_init_list(var_type)


    def parse_power(self):
        # print('\t' * 6 + 'parseTerm():')
        self.parse_factor()
        while True:
            num_line, lex, tok = self.get_symb()
            if tok in 'pow_op':
                self.num_row += 1
                print('\t' * 6 + f'в рядку {num_line} - {(lex, tok)}')
                self.parse_factor()
                self.postfix_notation.append((lex, tok, None))
                # if self.to_view:
                #     self.print_translator_step(lex)
            else:
                break
        return True

    def get_row(self, index):
        if index > self.token_count:
            self.fail_parse(self.ERR_GET_SYMB, (index,))
        # таблиця розбору реалізована у формі словника (dictionary)
        # tableOfSymb[numRow]={numRow: (numLine, lexeme, token, indexOfVarOrConst)
        num_line, lexeme, token, _ = self.table_of_tokens[index]
        return num_line, lexeme, token

    def parse_var_list(self):
        num_line, lex, tok = self.get_symb()
        # prev_num_line, prev_lex, prev_tok = self.get_row(self.num_row - 1)
        self.num_row += 1

        if tok == 'ident': # or (prev_lex == ',' and prev_tok == 'punct'): # tok == ident
            print('\t' * 5 + f'в рядку {num_line} - {(lex, tok)}')
            self.postfix_notation.append((lex, tok, ''))
            pass
        else:
            self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'bracket_op, int, float, bool, ident або \'(\' Expression \')\''))

        num_line, lex, tok = self.get_symb()
        if lex == ',' and tok == 'punct':
            self.num_row += 1
            self.parse_var_list()

    def get_back(self):
        self.num_row -= 1
