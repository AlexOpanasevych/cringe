import traceback

import cringe_stack


def is_undefined(variable_type):
    return variable_type == 'undefined'


def is_nullable(variable_value):
    return variable_value == 'null'


class CringeInterpreter:
    operator_mapping = {
        '+': '+', '-': '-', '*': '*', '/': '/', '^': '**', '=': '=',
        '<': '<', '<=': '<=', '==': '==', '!=': '!=', '>=': '>=', '>': '>', '&&': 'and', '||': 'or'
    }

    type_mapping = {'real': 'float', 'integer': 'int', 'boolean': 'bool'}

    run_time_errors = {
        'types_mismatch': ('%s\n\tТипи операндів відрізняються: %s %s %s.', 1),
        'undefined_var': ('%s\n\tНевідома змінна \'%s\'.', 2),
        'zero_division': ('%s\n\tДілення на нуль: %s %s %s.', 3),
        'invalid_operand_types': ('%s\n\tНевалідний тип одного або декількох операндів: %s %s %s.', 4),
        'undefined': ('%s\n\tНевизначена змінна \'%s\' не може використовуватись в операціях.', 5),
        'invalid_operator': ('%s\n\tНевідомий оператор %s', 322),
    }

    def __init__(self, postfix_notation, ident_table, const_table):
        self.tableOfLabel = {}
        self.command_track = []
        self.postfix_notation = postfix_notation

        self.ident_table = ident_table
        self.const_table = const_table
        self.stack = cringe_stack.Stack()

        self.success = True

    def interpret(self):
        try:
            i = 0
            num_it = len(self.postfix_notation)
            max_it = 10000
            current_it = 0
            while i < num_it and current_it < max_it:
                print(self.ident_table)
                current_it += 1
                lex = None
                tok = None
                var_type = None
                if len(self.postfix_notation[0]) > 2:
                    lex, tok, var_type = self.postfix_notation.pop(0)
                else:
                    lex, tok = self.postfix_notation.pop(0)
                self.command_track.append((num_it, lex, tok))
                if tok in ('integer', 'real', 'boolean', 'ident'):
                    self.stack.push((lex, tok))
                    next_instr = num_it + 1
                    if tok == 'ident' and var_type:
                        self.ident_table[lex] = (
                            self.ident_table[lex][0],
                            var_type,
                            self.ident_table[lex][2]
                        )
                elif tok in ('jump', 'jf', 'colon'):
                    next_instr = self.do_jumps(tok, num_it)
                else:
                    self.do_action(lex, tok)
                    next_instr = num_it + 1
                num_it = next_instr
            return self.command_track

            # if self.to_view:
            #     self.stepToPrint(i + 1, lex, tok)
        except SystemExit as e:
            print('CringeInterpreter: Аварійне завершення програми з кодом {0}'.format(e))
            return False
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        print('CringeInterpreter: Інтерпретатор завершив роботу успішно')
        return True

    def do_action(self, lex, tok):
        if lex == "=" and tok == "assign_op":
            lex_right, tok_right = self.stack.pop()
            value_right, type_right = self.check_token_and_lexeme(tok_right, lex_right)
            lex_left, tok_left = self.stack.pop()
            _, type_left = self.check_token_and_lexeme(tok_left, lex_left)

            if type_left != type_right:
                self.fail_runtime('types_mismatch', type_left, lex, type_right)

            if tok_left == 'ident':
                _type = self.ident_table[lex_left][1]
            else:
                _type = type_left

            try:
                self.ident_table[lex_left] = (
                    self.ident_table[lex_left][0],
                    _type,
                    eval(f"{self.type_mapping[_type]}({value_right})")
                )
            except KeyError:
                self.fail_runtime('undefined', lex_left)
        elif tok in ('add_op', 'mult_op', 'pow_op'):
            lex_right, tok_right = self.stack.pop()
            lex_left, tok_left = self.stack.pop()

            if (tok_right, tok_left) in (('integer', 'real'), ('real', 'integer')):
                self.fail_runtime('types_mismatch', lex_left, lex, lex_right)

            self.process_operator((lex_left, tok_left), lex, (lex_right, tok_right))

        elif tok in ('rel_op', 'bool_op'):
            lex_right, tok_right = self.stack.pop()
            lex_left, tok_left = self.stack.pop()
            print()
            if lex not in ('==', '!=', '&&', '||') and not all(
                    (tok in ('integer', 'real', 'ident', 'boolean') for tok in (tok_right, tok_left))):
                self.fail_runtime('invalid_operand_types', lex_left, lex, lex_right)

            self.process_operator((lex_left, tok_left), lex, (lex_right, tok_right))
        elif lex == 'print':
            (lexR, tokR) = self.stack.pop()
            self.processing_print((lexR, tokR), lex)
        elif lex == 'scan':
            (lexR, tokR) = self.stack.pop()
            self.processing_scan((lexR, tokR), lex)


    def processing_print(self, param, lex):
        valL = None
        lexL, tokL = param
        if tokL == 'id':
            if self.ident_table[lexL][2] == 'val_undef':
                self.fail_runtime('неініціалізована змінна',
                                  (lexL, self.ident_table[lexL], (lexL, tokL), lex, (None, None)))
            else:
                valL, tokL = (self.ident_table[lexL][2], self.ident_table[lexL][1])
        else:
            valL = self.const_table[lexL][2]
        print(valL)
        toTableOfConst(valL, tokL)

    def processing_scan(self, param, lex):
        lexL, tokL = lex
        if tokL == 'ident':
            valL, tokL = (self.ident_table[lexL][2], self.ident_table[lexL][1])
        else:
            self.fail_runtime('неочікуваний аргумент у scan', (lexL, self.ident_table[lexL], (lexL, tokL), lex, (None, None)))
        if tokL == 'integer':
            f = int
        elif tokL == 'real':
            f = float
        else:
            f = bool
        try:
            input_val = input()
            valL = f(input_val)
        except ValueError:
            self.fail_runtime('невідповідність типів', ((lexL, tokL), 'та ', ('input_val', input_val)))
        self.ident_table[lexL] = (self.ident_table[lexL][0], self.ident_table[lexL][1], valL)
        toTableOfConst(valL, tokL)

    def run_operator(self, left, lex, right):
        lex_left, type_left, value_left = left
        lex_right, type_right, value_right = right

        if self.ident_table.get(lex_left, None) and is_nullable(value_left):
            self.fail_runtime('nullable', lex_left)
        if self.ident_table.get(lex_right, None) and is_nullable(value_right):
            self.fail_runtime('nullable', lex_right)
        if operator := self.operator_mapping.get(lex, None):
            try:
                print(f"CALC: {value_left} {operator} {value_right}")
                calc_result = eval(f"{value_left} {operator} {value_right}")
            except ZeroDivisionError:
                self.fail_runtime('zero_division', value_left, operator, value_right)
            else:
                if lex == "/" and type_right:
                    calc_result = int(calc_result)
                if lex in ('<', '<=', '==', '!=', '>=', '>',):
                    _type = 'bool'
                else:
                    _type = type_left
                self.stack.push((calc_result, _type))
                self.push_to_consts_table(_type, calc_result)
        else:
            self.fail_runtime('invalid_operator', operator)

    def check_token_and_lexeme(self, token, lexeme):
        lexeme = str(lexeme)
        if token == 'ident':
            if is_undefined(self.ident_table[lexeme][1]):
                self.fail_runtime('undefined_var', lexeme)

            return self.ident_table[lexeme][2], self.ident_table[lexeme][1]
        else:
            return self.const_table[lexeme][2], self.const_table[lexeme][1]

    def fail_runtime(self, error: str, *args):
        error_msg, error_code = self.run_time_errors.get(error, (None, None))
        print(error_msg % ('CringeInterpreterError:', *args))
        exit(error_code)

    def process_operator(self, left, lex, right):
        lex_left, tok_left = left
        lex_right, tok_right = right

        value_left, type_left = self.check_token_and_lexeme(tok_left, lex_left)
        value_right, type_right = self.check_token_and_lexeme(tok_right, lex_right)

        self.run_operator((lex_left, type_left, value_left), lex, (lex_right, type_right, value_right))

    def push_to_consts_table(self, token, value):
        if not self.const_table.get(str(value), None):
            index = len(self.const_table) + 1
            self.const_table[str(value)] = (index, token, value)

    def do_jumps(self, tok, num_it):
        if tok == 'colon':
            return self.processing_colon(num_it)
        elif tok == 'jf':
            return self.processing_JF(num_it)
        else:
            return self.processing_JUMP(num_it)

    def processing_JUMP(self, num_it):
        m = self.stack.pop()
        return self.tableOfLabel[m[0]]

    def processing_JF(self, num_it):
        m = self.stack.pop()
        bool_expr = self.stack.pop()
        if self.getBoolValue(bool_expr[0]):
            return num_it + 1
        else:
            return self.tableOfLabel[m[0]]

    def processing_colon(self, num_it):
        # global instrNum
        m = self.stack.pop()
        return num_it + 1

    def getBoolValue(self, param):
        pass
