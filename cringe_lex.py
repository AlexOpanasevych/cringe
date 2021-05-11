from cringe_grammar import *
import pprint


# Діаграма станів
#               Q                                   q0          F
# M = ({0,1,2,4,5,6,9,11,12,13,14,101,102}, Σ,  δ , 0 , {2,6,9,12,13,14,101,102})


# δ - state-transition_function
# stf={(0,'Letter'):1,  (1,'Letter'):1, (1,'Digit'):1, (1,'other'):2, \
#      (0,'Digit'):4, (4,'Digit'):4, (4,'dot'):5, (4,'other'):9, (5,'Digit'):5, (5,'other'):6, \
#      (0, ':'):11, (11,'='):12, \
#      (11,'other'):102, \
#      (0, 'ws'):0, \
#      (0, 'eol'):13, \
#      (0, '+'):14, (0, '-'):14, (0, '*'):14, (0,'/'):14, (0, '('):14, (0, ')'):14, \
#      (0, 'other'):101
#      }


class CringeLexer:
    tableOfId = {}  # Таблиця ідентифікаторів
    tableOfConst = {}  # Таблиць констант
    tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)

    def __init__(self, source_code):
        self.tableOfLanguageTokens = tableOfLanguageTokens
        self.tableIdentFloatInt = tableIdentFloatInt
        self.classes = classes
        self.stf = stf
        self.states = states
        self.errorsDescription = errorsDescription

        # f = open('test.cringe', 'r')
        self.sourceCode = source_code + ' '
        # f.close()

        # ознака успішності розбору
        self.f_success = True

        self.state = states['initial'][0]

        self.lenCode = len(self.sourceCode) - 1  # номер останнього символа у файлі з кодом програми
        self.numLine = 1  # лексичний аналіз починаємо з першого рядка
        self.numChar = 0  # з першого символа (в Python'і нумерація - з 0)
        self.char = ''  # ще не брали жодного символа
        self.lexeme = ''  # ще не починали розпізнавати лексеми

    def lex(self):
        # global state, numLine, char, lexeme, numChar, FSuccess
        try:
            while self.numChar < self.lenCode:
                self.char = self.next_char()
                self.state = self.next_state(self.state, self.class_of_char(self.char))
                if self.is_initial_state(self.state):
                    self.lexeme = ''
                elif self.is_final_state(self.state):
                    self.processing()
                else:
                    self.lexeme += self.char
            print('CringeLexer: Лексичний аналіз завершено успішно')
            # Таблиці: розбору, ідентифікаторів та констант
            print('-' * 30)

            pprint.pprint('tableOfSymb:{0}'.format(self.tableOfSymb))
            pprint.pprint('tableOfId:{0}'.format(self.tableOfId))
            pprint.pprint('tableOfConst:{0}'.format(self.tableOfConst))

        except SystemExit as e:
            self.f_success = False
            print('CringeLexer: Аварійне завершення програми з кодом {0}'.format(e))

    def processing(self):
        if self.state in self.states['endOfLine']:
            self.numLine += 1
            self.state = self.states['initial'][0]
        elif self.state in (self.states['const'] + self.states['identifier']):
            token = self.get_token(self.state, self.lexeme)
            if token != 'keyword':
                index = self.index_id_const(self.state, self.lexeme)
                print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(self.numLine, self.lexeme, token, index))
                self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, index)
            else:
                print('{0:<3d} {1:<10s} {2:<10s} '.format(self.numLine, self.lexeme, token))
                self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
            self.lexeme = ''
            self.state = self.states['initial'][0]
            self.numChar = self.put_char_back(self.numChar)
        elif self.state in self.states['operators']:
            if not self.lexeme or self.state in self.states['double_operators']:
                self.lexeme += self.char
            token = self.get_token(self.state, self.lexeme)
            print('{0:<3d} {1:<10s} {2:<10s} '.format(self.numLine, self.lexeme, token))
            self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
            if self.state in self.states['star']:
                self.numChar = self.put_char_back(self.numChar)
            self.lexeme = ''
            self.state = self.states['initial'][0]
        elif self.state in self.states['error']:
            self.fail()

        #     def processing(self):
        # # global state, lexeme, char, numLine, numChar, tableOfSymb
        # if self.state == 13:  # \n
        #     self.numLine += 1
        #     self.state = self.states['initial'][0]
        # if self.state in (2, 6, 9):  # keyword, ident, float, int
        #     token = self.get_token(self.state, self.lexeme)
        #     if token != 'keyword':  # не keyword
        #         index = self.index_id_const(self.state, self.lexeme)
        #         print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(self.numLine, self.lexeme, token, index))
        #         self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, index)
        #     else:  # якщо keyword
        #         print('{0:<3d} {1:<10s} {2:<10s} '.format(self.numLine, self.lexeme, token))  # print(numLine,lexeme,
        #         # token)
        #         self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
        #     self.lexeme = ''
        #     self.numChar = self.put_char_back(self.numChar)  # зірочка
        #     self.state = self.states['initial'][0]
        # if self.state in (12, 14):  # 12:         # assign_op # in (12,14):
        #     self.lexeme += self.char
        #     token = self.get_token(self.state, self.lexeme)
        #     print('{0:<3d} {1:<10s} {2:<10s} '.format(self.numLine, self.lexeme, token))
        #     self.tableOfSymb[len(self.tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
        #     self.lexeme = ''
        #     self.state = self.states['initial'][0]
        # if self.state in self.errorsDescription:  # (101,102):  # ERROR
        #     self.fail()

    def fail(self):
        # global state, numLine, char
        print(self.numLine)
        if self.state == 101:
            print('Lexer: у рядку ', self.numLine, ' неочікуваний символ ' + self.char)
            exit(101)
        if self.state == 102:
            print('Lexer: у рядку ', self.numLine, ' очікувався символ =, а не ' + self.char)
            exit(102)

    def is_initial_state(self, state):
        return state in self.states["initial"]

    def is_final_state(self, state):
        return state in self.states["final"]

    def next_state(self, state, class_ch):
        result = None
        for t in class_ch:
            step = (state, t)
            if step in self.stf:
                result = self.stf[step]
        if result is None:
            result = self.stf[(state, 'other')]
        return result

    def next_char(self):
        char = self.sourceCode[self.numChar]
        self.numChar += 1
        return char

    @staticmethod
    def put_char_back(num_char):
        return num_char - 1

    def class_of_char(self, char):
        result = []
        for key, value in self.classes.items():
            if char in value:
                if key == "Operators":
                    result.append(char)
                else:
                    result.append(key)
        return result

    def get_token(self, state, lexeme):
        try:
            return self.tableOfLanguageTokens[lexeme]
        except KeyError:
            return self.tableIdentFloatInt[state]

    def index_id_const(self, state, lexeme):
        index = 0
        if state == 2:
            index = self.tableOfId.get(lexeme)
            #		token=getToken(state,lexeme)
            if index is None:
                index = len(self.tableOfId) + 1
                self.tableOfId[lexeme] = index
        if state == 6:
            index = self.tableOfConst.get(lexeme)
            if index is None:
                index = len(self.tableOfConst) + 1
                self.tableOfConst[lexeme] = index
        if state == 9:
            index = self.tableOfConst.get(lexeme)
            if index is None:
                index = len(self.tableOfConst) + 1
                self.tableOfConst[lexeme] = index
        return index
