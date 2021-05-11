tableOfLanguageTokens = {'program': 'keyword', 'if': 'keyword', 'then': 'keyword', 'fi': 'keyword', '=': 'assign_op',
                         '.': 'punct', ' ': 'ws', '\t': 'ws', '\n': 'eol', '-': 'add_op', '+': 'add_op', '*': 'mult_op',
                         '/': 'mult_op',  # 'e': 'mult_op',
                         '(': 'par_op', ')': 'par_op', '{': 'start_block',
                         '}': 'end_block', 'by': 'keyword', ',': 'punct', '||': 'bool_op', '&&': 'bool_op',
                         'true': 'bool', 'false': 'bool', ';': 'op_end', ':': 'punct', '<': 'rel_op', '>': 'rel_op',
                         '>=': 'rel_op', '<=': 'rel_op', '==': 'rel_op', '^': 'pow_op', '\n\r': 'eol', '\r\n': 'eol',
                         'while': 'keyword', 'do': 'keyword', 'for': 'keyword', 'scan': 'keyword', 'print': 'keyword',
                         'boolean': 'keyword', 'real': 'keyword', 'integer': 'keyword', '!=': 'rel_op'
                         }

tableIdentFloatInt = {2: 'ident', 4: 'integer', 6: 'real', 15: 'real'}

classes = {
    'Digit': '0123456789',
    'Dot': '.',
    'WhiteSpace': ' \t',
    'EndOfLine': '\n\r',
    'Operators': '+-*/^(){}:;=<>!,',
    'ScientificNotation': 'e',
    'Letter': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
}

stf = {
    (0, 'WhiteSpace'): 0,  # WhiteSpace
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,  # ident
    (0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'other'): 4,  # int
    (3, 'Dot'): 5, (5, 'Digit'): 5, (5, 'other'): 6,  # float
    (0, '!'): 7, (7, '='): 8, (7, 'other'): 102,  # not equal or error
    (0, '='): 9, (0, '<'): 9, (0, '>'): 9, (9, '='): 10, (9, 'other'): 11,  # relative ops and is
    (0, '+'): 13, (0, '-'): 13, (0, '*'): 13, (0, '/'): 13, (0, '^'): 13,  # (0, 'e'): 13,  # Operators
    (0, '('): 13, (0, ')'): 13, (0, '{'): 13, (0, '}'): 13, (0, ':'): 13, (0, ';'): 13, (0, ','): 13,  # Operators
    (0, 'EndOfLine'): 12,  # EndOfLine
    (0, 'other'): 101,  # error
    (3, 'ScientificNotation'): 14, (14, 'Digit'): 14, (14, 'other'): 15, (5, 'ScientificNotation'): 14
}

states = {
    'initial': (0,),
    'star': (2, 4, 6, 11, 15),
    'error': (101, 102),
    'final': (2, 4, 6, 8, 10, 11, 12, 13, 15, 101, 102),
    'endOfLine': (12,),
    'operators': (8, 10, 11, 13),
    'double_operators': (8, 10),
    'const': (4, 6, 15),
    'identifier': (2,)
}

errorsDescription = {
    101: "CringeLexerError: у рядку %s нерозпізнаний символ %s",
    102: "CringeLexerError: у рядку %s очікувався символ '=', а не %s",
}
