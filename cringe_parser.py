class CringeParser:
    # error codes

    ERR_TOKEN_MISMATCH = 1  # token mismatch
    ERR_GET_SYMB = 2  # token mismatch
    ERR_UNEXP_END_OF_PROG = 3  # token mismatch
    ERR_INSTR_MISMATCH = 4  # token mismatch
    ERR_EXP_FACTOR_MISMATCH = 5  # token mismatch
    ERR_BOOL_EXPR_MISMATCH = 6  # token mismatch

    def __init__(self, table_of_tokens: dict[int, tuple], const_table):
        self.tableOfForHiddenId = {}
        self.table_of_tokens = table_of_tokens
        self.num_row = 1
        self.token_count = len(table_of_tokens)
        self.postfix_notation = []
        self.tableOfLabel = {}
        self.f_success = True
        self.hidden_table = {}
        self.const_table = const_table

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
            self.postfix_notation.append((lex, tok, None))
            self.num_row += 1
            if self.get_symb()[-1] == 'assign_op':
                self.get_back()
                self.parse_assign()
            else:
                self.get_back()
                self.parse_expression()
            self.parse_token(';', 'op_end', '\t' * 2)
            return True

        # якщо лексема - ключове слово 'if'
        # обробити інструкцію розгалудження
        elif (lex, tok) == ('if', 'keyword'):
            self.parse_if()
            # self.parse_token(';', 'op_end', '\t' * 2)
            return True
        
        elif (lex, tok) == ('for', 'keyword'):
            self.parse_for()
            # self.parse_token(';', 'op_end', '\t' * 2)
            return True
            
        elif (lex, tok) == ('print', 'keyword'):
            self.parse_print()
            self.parse_token(';', 'op_end', '\t' * 2)
            return True
        elif (lex, tok) == ('scan', 'keyword'):
            self.parse_scan()
            self.parse_token(';', 'op_end', '\t' * 2)
            return True
        elif lex in ('integer', 'real', 'boolean') and tok == 'keyword':
            self.parse_declaration()
            self.parse_token(';', 'op_end', '\t' * 2)
            return True
        elif (lex, tok) == ('}', 'end_block'):
            return False
        else:
            return False

    def fail_parse(self, error_code, what: tuple):
        self.f_success = False
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
            self.postfix_notation.append(('=', 'assign_op', None))
            return True
        else:
            return False

    def parse_expression(self):
        print('\t' * 5 + 'parseExpression():')
        num_row, lex, tok = self.get_symb()
        arithm_expr_parse_result = self.parse_arithm_expression()
        bool_expr_parse_result = self.parse_bool_expr()
        if arithm_expr_parse_result == False and bool_expr_parse_result == False:
            num_line, lex, tok = self.get_symb()
            self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'boolean, bool_op, rel_op, integer, real, ident або \'(\' Expression '
                                                 '\')\''))
        return True

    def parse_power(self):
        print('\t' * 6 + 'parsePower():')
        self.parse_factor()
        num_line, lex, tok = self.get_symb()
        if tok =='pow_op':
            self.num_row += 1
            self.parse_power()
            self.postfix_notation.append((lex, tok, None))
        return True


    def parse_term(self):
        print('\t' * 6 + 'parseTerm():')
        if self.parse_power():
            # продовжувати розбирати Множники (Factor)
            # розділені лексемами '*' або '/'
            # while F:
            numLine, lex, tok = self.get_symb()
            if tok == 'mult_op':
                self.num_row += 1
                print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
                # self.parse_power()
                self.parse_term()
                self.postfix_notation.append((lex, tok, None))
            # if (lex, tok) == ('^', 'pow_op'):
            #     self.num_row += 1
            #     print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            #     self.parse_term()
                # else:
                #     F = False
            return True
        else:
            return False

    def parse_factor(self):
        print('\t' * 7 + 'parseFactor():')
        num_line, lex, tok = self.get_symb()
        print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lex, tok):{1}'.format(num_line, (lex, tok)))

        # перша і друга альтернативи для Factor
        # якщо лексема - це константа або ідентифікатор
        if tok in ('integer', 'real', 'ident', 'boolean'):
            self.postfix_notation.append((lex, tok, None))
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
            return False
            # self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
            #                 (num_line, lex, tok, 'rel_op, integer, real, ident або \'(\' Expression \')\''))
        return True

    def parse_if(self):
        _, lex, tok = self.get_symb()
        if lex == 'if' and tok == 'keyword':
            self.num_row += 1
            self.parse_bool_expr()
            self.parse_token('then', 'keyword', '\t' * 5)
            m1 = self.create_label()
            self.postfix_notation.append(m1)
            self.postfix_notation.append(('JF', 'jf'))
            self.parse_statement_list()
            self.set_var_label(m1)
            self.postfix_notation.append(m1)
            self.postfix_notation.append((':', 'colon'))
            self.parse_token('fi', 'keyword', '\t' * 5)
            return True
        else:
            return False

    def parse_bool_expr(self):
        num_line, lex, tok = self.get_symb()
        print('\t' * 6 + 'parse_bool_expr: ' + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
        if tok == 'boolean':
            self.num_row += 1
            self.parse_bool_expr()
            self.postfix_notation.append((lex, tok, None))

        elif tok == 'rel_op':
            self.num_row += 1
            # self.postfix_notation.append((lex, tok, None))
            self.parse_arithm_expression()
            # self.postfix_notation.append((lex, tok, None))
            self.parse_bool_expr()
            self.postfix_notation.append((lex, tok, None))
            return True
            # print('\t' * 5 + f'в рядку {num_line} - {(lex, tok)}')
        elif tok == 'bool_op':
            self.num_row += 1
            self.parse_bool_expr()
            self.postfix_notation.append((lex, tok, None))
            return True
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
            self.parse_assign()
            self.postfix_notation.append((lex, tok))
            # num_line, lex, tok = self.get_symb()
            # if tok == 'ident':
            #     for_id_type = self.table_of_tokens[lex][1]
            # if self.const_table.get('1') is None:
            #     self.const_table['1'] = (len(self.const_table)+1, 'integer', 1)
            # if self.const_table.get('0') is None:
            #     self.const_table['0'] = (len(self.const_table)+1, 'integer', 0)

            self.parse_token('by', 'keyword', '')
            # postfixCode.append(('1', 'intnum'))
            self.postfix_notation.append(('=', 'assign_op'))
            m1 = self.create_label()
            m2 = self.create_label()
            m3 = self.create_label()


            self.set_var_label(m1)
            self.postfix_notation.append(m1)


            self.postfix_notation.append((':', 'colon'))
            self.parse_expression()
            self.parse_token('while', 'keyword', '')
            self.postfix_notation.append(('=', 'assign_op'))
            r1, r2 = self.generate_for_hidden_var('integer')
            self.postfix_notation.append(r1)
            self.postfix_notation.append(('0', 'integer'))
            self.postfix_notation.append(('==', 'rel_op'))
            self.postfix_notation.append(m2)
            self.postfix_notation.append(('JF', 'jf'))
            self.postfix_notation.append((lex, tok))
            self.postfix_notation.append((lex, tok))
            self.postfix_notation.append(r2)
            self.postfix_notation.append(('+', 'add_op'))
            self.postfix_notation.append(('=', 'assign_op'))


            self.set_var_label(m2)
            self.postfix_notation.append(m2)


            self.postfix_notation.append((':', 'colon'))
            self.postfix_notation.append(r1)
            self.postfix_notation.append(('0', 'intnum'))
            self.postfix_notation.append(('=', 'assign_op'))
            self.postfix_notation.append((lex, tok))
            self.parse_expression()
            self.parse_token('do', 'keyword', '\t' * 5)

            self.postfix_notation.append(('-', 'add_op'))
            self.postfix_notation.append(r2)
            self.postfix_notation.append(('*', 'mult_op'))
            self.postfix_notation.append(('0', 'intnum'))
            self.postfix_notation.append(('<', 'rel_op'))


            self.postfix_notation.append(m3)
            self.postfix_notation.append(('JF', 'jf'))

            self.parse_statement()

            self.parse_token(lex, tok, '')


            self.postfix_notation.append(m1)
            self.postfix_notation.append(('JUMP', 'jump'))


            self.set_var_label(m3)
            self.postfix_notation.append(m3)
            self.postfix_notation.append((':', 'colon'))

            return True
        else:
            return False

    def parse_print(self):
        _, lex, tok = self.get_symb()
        if (lex, tok) == ('print', 'keyword'):
            self.num_row += 1
            # self.postfix_notation.append((lex, tok))
            self.parse_token('(', 'par_op', '\t' * 5)
            self.parse_factor()
            self.parse_inner_print()
            self.parse_token(')', 'par_op', '\t' * 5)
            self.postfix_notation.append((lex, tok))
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
            self.postfix_notation.append((lex, tok))
            return True
        else:
            return False

    def parse_declaration(self):
        num_line, lex, tok = self.get_symb()
        self.num_row += 1
        if lex in ('integer', 'real', 'boolean') and tok == 'keyword':

            self.parse_var_init_list(lex)
            # self.parse_token(';', 'op_end', '')

        else:
            self.fail_parse(self.ERR_EXP_FACTOR_MISMATCH,
                           (num_line, lex, tok, 'integer, real, boolean, ident або \'(\' Expression \')\''))

    def parse_arithm_expression(self):
        if self.parse_term():
            num_line, lex, tok = self.get_symb()
            if tok in 'add_op':
                self.num_row += 1
                print('\t' * 6 + 'parse_arithm_expression: ' + f'в рядку {num_line} - {(lex, tok)}')
                self.parse_arithm_expression()
                self.postfix_notation.append((lex, tok, None))
                # if self.to_view:
                #     self.print_translator_step(lex)
            return True
        else:
            return False

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


    # def parse_power(self):
    #     # print('\t' * 6 + 'parseTerm():')
    #     self.parse_factor()
    #     while True:
    #         num_line, lex, tok = self.get_symb()
    #         if tok in 'pow_op':
    #             self.num_row += 1
    #             print('\t' * 6 + f'в рядку {num_line} - {(lex, tok)}')
    #             self.parse_factor()
    #             self.postfix_notation.append((lex, tok, None))
    #             # if self.to_view:
    #             #     self.print_translator_step(lex)
    #         else:
    #             break
    #     return True

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

    def create_label(self):
        nmb = len(self.tableOfLabel) + 1
        lexeme = "m" + str(nmb)
        val = self.tableOfLabel.get(lexeme)
        if val is None:
            self.tableOfLabel[lexeme] = 'val_undef'
            tok = 'label'
        else:
            tok = 'Конфлiкт мiток'
            print(tok)
            exit(1003)
        return lexeme, tok

    def set_var_label(self, lbl):
        lex, _tok = lbl
        self.tableOfLabel[lex] = len(self.postfix_notation)
        return True

    def generate_for_hidden_var(self, value_type):
        n = len(self.tableOfForHiddenId)
        id_n = len(self.table_of_tokens) + 1
        r1 = 'isForFirstStepId' + str(n)
        r2 = 'forStepExpressionValue' + str(n)
        if self.table_of_tokens.get(r1) is None:
            self.table_of_tokens[r1] = (id_n, 'integer', 1)
        else:
            self.fail_parse(self.ERR_GET_SYMB, (1, r1, 'id', 'id'))
        if self.table_of_tokens.get(r2) is None:
            self.table_of_tokens[r2] = (id_n + 1, value_type, 'undefined')
        else:
            self.fail_parse(self.ERR_GET_SYMB, (1, r2, 'ident', 'ident'))
        self.tableOfForHiddenId[n] = (r1, r2)
        return (r1, 'ident'), (r2, 'ident')
