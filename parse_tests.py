import shlex
import my_parser as parser

def checkTest(actual, expected):
    try:
        if (actual != expected):
            print('Fail-\nGot \'' + actual + '\' was expecting \'' + expected + '\'')
            raise Exception
    except Exception:
        raise

def demoTest():
    print('Demo test of \'sample.lua\': ', end='')
    expected = open('sample.lua', 'rt').read()
    expected = "".join(expected.split())
    actual = parser.parse('sample.lua')
    checkTest(actual, expected)
    print('okay')


def copyLexerTest():
    print('Copy lexer test: ', end='')
    lexertarget = shlex.shlex(open('test/blank.lua', 'rt').read())
    lexersrc = shlex.shlex(open('test/blank.lua', 'rt').read())

    lexertarget.push_token('something')
    lexersrc.push_token('d')
    lexersrc.push_token('c')
    lexersrc.push_token('b')
    lexersrc.push_token('a')
    parser.copyLexer(lexertarget, lexersrc)

    stringtarget = ''
    stringsrc = ''

    for token in lexertarget:
        stringtarget = stringtarget + token

    for token in lexersrc:
        stringsrc = stringsrc + token

    checkTest(stringtarget, 'abcdsomeotherdata')
    print('okay')

def wordTest():
    print('Word test: ', end="")
    lexer = shlex.shlex()

    # test match
    lexer.push_token('test')
    checkTest(parser.parseWord(lexer, 'test'), 'test')

    # test no match
    lexer.push_token('test')
    checkTest(parser.parseWord(lexer, 'not'), '')
    print('okay')


def binopTest():
    print('Binop test: ', end="")
    lexer = shlex.shlex()

    # test match
    for token in ['+', '-', '*', '/', '^', '%', '.', '<', '>' , '=', '~', 'and', 'or']:
        lexer.push_token(token)
        checkTest(parser.parseBinop(lexer), token)

    # test no match
    for token in ['this', 'is', 'not', 'a', 'binop']:
        lexer.push_token(token)
        checkTest(parser.parseBinop(lexer), '')

    print('okay')

def unopTest():
    print('Unop test: ', end="")
    lexer = shlex.shlex()

    # test match
    for token in ['-', 'not', '#']:
        lexer.push_token(token)
        checkTest(parser.parseUnop(lexer), token)

    # test no match
    for token in ['this', 'is', 'definitelynot', 'a', 'unop']:
        lexer.push_token(token)
        checkTest(parser.parseUnop(lexer), '')

    print('okay')

def fieldsepTest():
    print('Fieldsep test: ', end="")
    lexer = shlex.shlex()

    # test match
    for token in [',', ';']:
        lexer.push_token(token)
        checkTest(parser.parseFieldsep(lexer), token)

    # test no match
    for token in ['this', 'is', 'definitelynot', 'a', 'fieldsep']:
        lexer.push_token(token)
        checkTest(parser.parseFieldsep(lexer), '')

    print('okay')

def fieldTest():
    print('Field test: ', end="")
    lexer = shlex.shlex(open('test/field-test.lua', 'rt').read())
    answer = shlex.shlex(open('test/field-test.lua', 'rt').read())
    checkTest(parser.parseField(lexer), answer)

    lexer.push_token('8thisisnotafield')
    checkTest(parser.parseField(lexer), '')

    print('okay')

def expTest():
    print('Exp test: ', end='')
    lexer = shlex.shlex(open('test/function-test.lua', 'rt').read())
    answer = open('test/function-test.lua', 'rt').read()
    checkTest(parser.parseExp(lexer), answer)

    lexer = shlex.shlex(open('test/tableconstructor-test.lua', 'rt').read())
    answer = open('test/tableconstructor-test.lua', 'rt').read()
    checkTest(parser.parseExp(lexer), answer)

    for token in ['nil', 'false', 'true']:
        checkTest(parser.parseExp(lexer), '')

    lexer.push_token('8thisisnotaexp')
    checkTest(parser.parseExp(lexer), '')

    print('okay')

def namelistTest():
    print('Namelist test: ', end='')
    inputfile = open('test/namelist-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)
    checkTest(parser.parseNamelist(lexer, -1), inputfile)

    lexer.push_token('asinglename')
    checkTest(parser.parseNamelist(lexer, -1), 'asinglename')

    trailingcommatest = open('test/namelistcomma-test.lua', 'rt').read()
    lexer = shlex.shlex(trailingcommatest)
    checkTest(parser.parseNamelist(lexer, -1), inputfile)

    lexer.push_token('end')
    checkTest(parser.parseNamelist(lexer, -1), '')

    print('okay')


def funcbodyTest():
    print('Funcbody test: ', end='')
    inputfile = open('test/functionbody-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)
    checkTest(parser.parseFuncbody(lexer), inputfile.replace(" ", ""))

    print('okay')

def argsTest():
    print('Args test: ', end='')
    inputfile = open('test/parseargs-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)
    checkTest(parser.parseArgs(lexer), inputfile.replace(" ", ""))

    print('okay')

def blockTest():
    print('Block test: ', end='')
    inputfile = open('test/function-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)
    checkTest(parser.parseBlock(lexer), inputfile.replace(" ", ""))

    print('okay')

def ifelseTest():
    print('Ifelse test: ', end='')
    inputfile = open('test/ifelse-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)
    checkTest(parser.parseBlock(lexer), inputfile.replace(" ", ""))

    print('okay')

def paramsTest():
    print('Params test: ', end='')
    inputfile = open('test/params-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)

    checkTest(parser.parseParlist(lexer), inputfile)

    print('okay')

def mathsTest():
    print('Math test: ', end='')
    inputfile = open('test/math-test.lua', 'rt').read()
    lexer = shlex.shlex(inputfile)

    checkTest(parser.parseStat(lexer), inputfile.replace(' ', ''))

    print('okay')

copyLexerTest()
wordTest()
binopTest()
unopTest()
fieldsepTest()
argsTest()
namelistTest()
funcbodyTest()
blockTest()
ifelseTest()
paramsTest()
mathsTest()

demoTest()