# from cringe_lex import CringeLexer
from cringe_lexer2 import CringeLexer
from cringe_parser import CringeParser
from cringe_interpreter import CringeInterpreter
import pprint

if __name__ == '__main__':
    with open('test.cringe', 'r') as source_file:
        source_code = source_file.read()

        lexer = CringeLexer(source_code)
        lexer.lex()
        lexer.print_symbols_table()
        lexer.print_ids_table()
        lexer.print_const_table()

        parser = CringeParser(lexer.tableOfSymb)
        parser.parse_program()
        pprint.pprint(parser.postfix_notation)

        translator = CringeInterpreter(parser.postfix_notation, lexer.tableOfId, lexer.tableOfConst)
        translator.interpret()
        if translator.success:
            print(translator.ident_table)
            print(translator.const_table)






