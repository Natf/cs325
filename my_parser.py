import shlex
import re
import copy

name = re.compile('(?![0-9])(\w)+$')
number = re.compile('[0-9]$')
savederrors = []
errors = []
lexer = shlex.shlex()
reservedTokens = ['and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 'return', 'then', 'true', 'until', 'while', '(', ')', '[', ']']
get_next_stat = 0

def tokenize(inputfile):
    lexer = shlex.shlex(inputfile)
    return lexer




def copyLexer(target, src):
    # empty our target
    for token in target:
        continue

    # first have to get a reversed stack
    srcreversered = copy.deepcopy(target)
    for token in src:
        srcreversered.push_token(token)

    # dump our reversed src into our target
    for token in srcreversered:
        target.push_token(token)


def checkTokenOptional(lexer, optional):
    if (optional == -1):
        return -1

    token = lexer.get_token()
    currentCheck = token

    while (token != lexer.eof):
        if (currentCheck == optional):
            return lexer
        token = lexer.get_token()
        currentCheck = currentCheck + token

    return -1


def parseWord(lexer, word, optional = 0):
   #print('>>> WORD ' + word)
    token = lexer.get_token()
    if (word == token):
        return token
    elif optional == 1:
        lexer.push_token(token)
        return ''
    else:
        global errors
        errors.append('exact character not found')
        return ''


def parseString(lexer):
    #print(">>> STRING")
    token = lexer.get_token()
    if(token == '\''):
        lexercp = copy.deepcopy(lexer)
        token = lexercp.get_token()
        if (lexercp.get_token() == '\''):
            copyLexer(lexer, lexercp)
            return '\'' + token + '\''
    elif(token == '"'):
        lexercp = copy.deepcopy(lexer)
        token = lexercp.get_token()
        if (lexercp.get_token() == '"'):
            copyLexer(lexer, lexercp)
            return '"' + token + '"'

    global errors
    errors.append('invalid string')
    return ''


def parseUnop(lexer):
   #print('>>> UNOP')
    token = lexer.get_token()

    if (token in ['-', 'not', '#']):
        return token
    else:
        global errros
        errors.append('unop not found')
        return ''


def parseFieldsep(lexer, optional = 0):
   #print('>>> FIELDSEP')
    token = lexer.get_token()

    if token in [',', ';']:
        return token
    elif optional == 1:
        lexer.push_token(token)
        return ''
    else:
        global errors
        errors.append('fieldsep not found')
        return ''


def parseName(lexer):
   #print('>>> NAME')
    token = lexer.get_token()
    if (name.match(token) and token not in ['and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 'return', 'then', 'true', 'until', 'while', '(', ')', '[', ']']):
        return token
    else:
        global errors
        errors.append('expected name, name not found')
        return ''


def parseNamelist(lexer, optional):
    global errors
    optional = checkTokenOptional(lexer, optional)
    if (optional != -1):
        return optional

    token = lexer.get_token()
    if (name.match(token) and token not in ['and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 'return', 'then', 'true', 'until', 'while', ',', '=']):
        lexercp = copy.deepcopy(lexer)
        if (lexercp.get_token() == ','):
            errors = []
            result = parseNamelist(lexercp, -1)
            if(len(errors) == 0):
                copyLexer(lexer, lexercp)
                return token + ',' + result
            else:
                errors = []

        return token
    else:
        errors.append('not name')
        return ''


def parseField(lexer):
   #print('>>> FIELD')
    options = 0
    result = ''
    global errors
    while (options < 2):
        errors = []
        lexercp = lexer
        if options == 0:
            result = parseWord(lexercp, '[') + parseExp(lexercp) + parseWord(lexercp, ']') + parseWord(lexercp, '=') + parseExp(lexercp)
        elif options == 1:
            result = parseName(lexercp) + parseWord(lexer, '=') + parseExp(lexercp)
        elif options == 2:
            result = parseExp(lexercp)

        if (len(errors) == 0):
            return result

    errors.append('parseField error field not found')
    return ''


def parseFieldsepfield(lexer):
   #print('>>> FIELDSEPFIELD')
    return parseFieldsep(lexer) + parseField(lexer)


def parseFieldlist(lexer):
   #print('>>> FIELDLIST')
    return parseField(lexer) + parseFieldsepfield(lexer, 1) + parseFieldsep(lexer, 1)


def parseTableconstructor(lexer):
   #print('>>> TABLE CONSTRUCTOR')
    token = lexer.get_token()
    if (token in ['{', '}']):
        return token
    else:
        return parseFieldlist(lexer)


def parseDo(lexer):
   #print('>>> DO')
    return parseBlock(lexer) + parseEnd(lexer)


def parseWhile(lexer):
   #print('>>> WHILE')
    return parseExp(lexer) + parseDo(lexer)


def parseRepeat(lexer):
   #print('>>> REPEAT')
    return parseBlock(lexer) + parseWord(lexer, 'until') + parseEnd(lexer)


def parseIf(lexer):
   #print('>>> IF')
    return parseExp(lexer) + parseWord(lexer, 'then') + parseBlock(lexer)


def parseFor(lexer):
   #print('>>> FOR')
    return parseExp(lexer) + parseWord(lexer, ',') + parseExplist(lexer) + parseWord(lexer, 'do') + parseDo(lexer)


def parseForin(lexer):
   #print('>>> FORIN')
    return parseWord(lexer, 'in') + parseExplist(lexer) + parseWord(lexer, 'do') + parseDo(lexer)


def parseElseif(lexer):
    global errors
    errors = []
    lexercp = copy.deepcopy(lexer)
    token = lexercp.get_token()
    if (token == 'elseif'):
        result = token + parseExp(lexercp) + parseWord(lexercp, 'then') + parseBlock(lexercp) + parseElseif(lexercp)
    else:
        return ''

    if (len(errors) == 0):
        copyLexer(lexer, lexercp)
        return result
    else:
        errors.append('expected end of elseif')
        return ''


def parseElse(lexer):
    global errors
    errors = []
    lexercp = copy.deepcopy(lexer)
    token = lexercp.get_token()
    if (token == 'else'):
        result = token + parseBlock(lexercp)
    else:
        return ''

    if (len(errors) == 0):
        copyLexer(lexer, lexercp)
        return result
    else:
        errors.append('expected end of else')
        return ''


def parseExp(lexer):
   #print(">>> EXP")
    token = lexer.get_token()

    if (token in [';', 'end', 'then', 'else', 'elseif']):
        lexer.push_token(token)
        return ''
    elif token in ['nil', 'false', 'true']:
        return token
    elif token == 'function':
        return token + parseFuncbody(lexer)
    elif token == '.':
        lexercp = copy.deepcopy(lexer)
        if (lexercp.get_token() == '.' and lexercp.get_token() == '.'):
            copyLexer(lexer, lexercp)
            return '...'
    elif (number.match(token)):
        return token

    lexer.push_token(token)
    theseoptions = 0
    result = ''
    global errors
    while (theseoptions < 5):
        errors = []
        lexercp = copy.deepcopy(lexer)
        if theseoptions == 0:
            result = parseString(lexercp)
        elif theseoptions == 1:
            result = parsePrefixexp(lexercp)
            if len(errors) == 0:
                lexercptest = copy.deepcopy(lexercp)
                result2 = parseBinop(lexercptest)
                if len(errors) == 0:
                    result3 = parseExp(lexercptest)
                    if len(errors) == 0:
                        copyLexer(lexercp, lexercptest)
                        result = result + result2 + result3
                errors = []
        elif theseoptions == 2:
            result = parseTableconstructor(lexercp)
        elif theseoptions == 3:
            result = parseExp(lexercp) + parseBinop(lexercp) + parseExp(lexercp)
        elif theseoptions == 4:
            result = parseUnop(lexercp) + parseExp(lexercp)

        if (len(errors) == 0):
            copyLexer(lexer, lexercp)
            return result
        else:
            theseoptions = theseoptions + 1

    return ''


def parseExplist(lexer, optional = 0):
   #print(">>> EXPLIST")
    global errors
    errors = []
    lexercp = copy.deepcopy(lexer)
    result = parseExp(lexercp)

    if (len(errors) == 0):
        copyLexer(lexer, lexercp)
        token = lexer.get_token()
        if (token == ','):
            return result + token + parseExplist(lexer)
        else:
            lexer.push_token(token)
            return result
    elif optional == 1:
        errors = []
        return ''

    errors.append('no explist found')
    return result


def parseArgs(lexer):
   #print(">>> ARGS")
    options = 0
    result = ''
    global errors
    while (options < 2):
        errors = []
        lexercp = copy.deepcopy(lexer)
        if options == 0:
            result = parseWord(lexercp, '(') + parseExplist(lexercp) + parseWord(lexercp, ')')
        elif options == 1:
            result = parseTableconstructor(lexercp)
        elif options == 2:
            result = parseString(lexercp)

        if (len(errors) == 0):
            copyLexer(lexer, lexercp)
            return result

        options += 1

    errors.append('args not found')
    return ''


def parseLocalfunction(lexer):
   #print('>>> LOCAL FUNCTION')
    return parseWord(lexer, 'function') + parseName(lexer) + parseFuncbody(lexer)


def parseFunctioncall(lexer):
   #print(">>> FUNCTION CALL")
    token = lexer.get_token()
    lexer.push_token(token)
    lexercp = copy.deepcopy(lexer)
    global errors
    errors = []
    result = parsePrefixexp(lexercp) + parseArgs(lexercp)

    if (len(errors) == 0):
        copyLexer(lexer, lexercp)
        return result

    lexercp = copy.deepcopy(lexer)
    errors = []
    result = parsePrefixexp(lexercp) + parseWord(lexercp, ':') + parseName(lexercp) + parseArgs(lexercp)

    if (len(errors) == 0):
        copyLexer(lexer, lexercp)
        return result
    else:
        errors.append('function call not found')
        return ''


def parsePrefixexp(lexer):
   #print('>>> PREFIXEXP')
    token = lexer.get_token()

    if token == '(':
        return token + parseExp(lexer) + parseWord(lexer, ')')
    else:
        lexer.push_token(token)

    options = 0
    result = ''
    while (options < 1):
        errors = []
        lexercp = copy.deepcopy(lexer)
        if options == 0:
            result = parseVar(lexercp)
        elif options == 1:
            result = parseFunctioncall(lexercp)

        if(len(errors) == 0):
            copyLexer(lexer, lexercp)
            return result

    errors.append('parsePrefixexp error not found prefixexp')
    return ''


def parseEnd(lexer):
    ##print('>>> END')
    token = lexer.get_token()
    if (token == 'end'):
        return token
    else:
        global errors
        global get_next_stat
        get_next_stat = 1
        errors.append('Error in parseEnd expected \'end\' got \''+ token + '\'')
        print_errors()
        return 'end'


def parseVar(lexer):
    global errors
    global get_next_stat
    if (len(errors) != 0):
        return ''
   #print('>>> VAR')
    token = lexer.get_token()

    if (token in ['end']):
        errors.append('no var found')
        lexer.push_token(token)
        return ''
    elif number.match(token):
        get_next_stat = 1
        errors.append('Error in parseVar: expected one of type var got \'' + token + '\'')
        print_errors()
        return ''

    lexer.push_token(token)
    options = 0
    while (options < 2):
        lexercp = copy.deepcopy(lexer)
        errors = []
        result = ''
        if (options == 0):
            result = parseName(lexercp)
        elif(options == 1):
            result = parsePrefixexp(lexercp) + parseWord(lexercp, '[') + parseExp(lexercp) + parseWord(lexercp, ']')
        elif(options == 2):
            result = parsePrefixexp(lexercp) + parseWord(lexercp, '.') + parseName(lexercp)

        if(len(errors) == 0):
            copyLexer(lexer, lexercp)
            return result

        options = options + 1

    errors.append('no var found')
    return lexer.get_token()


def parseVarlist(lexer):
   #print(">>> VARLIST")
    global errors
    errors = []
    lexercp = copy.deepcopy(lexer)
    result = parseVar(lexercp)

    if len(errors) == 0:
        copyLexer(lexer, lexercp)
        token = lexer.get_token()
        if (token == ','):
            result += ',' + parseVarlist(lexer)
        elif (token == '('):
            errors.append('not varlist')
            lexer.push_token(token)
            return ''
        else:
            lexer.push_token(token)
        return result
    else:
        print('error in varlist')
        return ''


def parseParlist(lexer):
   #print('>>> PARLIST')
    token = lexer.get_token()
    global errors

    if (token == '.'):
        lexercp = copy.deepcopy(lexer)
        if (lexercp.get_token() == '.' and lexercp.get_token() == '.'):
            copyLexer(lexer, lexercp)
            return '...'
        else:
            errors.append('expecting ...')
            lexer.push_token(token)
            return ''
    elif (token == ','):
        lexercp = copy.deepcopy(lexer)
        if (lexercp.get_token() != ','):
            return token + parseParlist(lexer)
        else:
            lexer.push_token(token)
            errors.append('expecting param rather than ,')
            return ''
    elif (token == ')'):
        lexer.push_token(token)
        return ''
    else:
        lexer.push_token(token)
        return parseNamelist(lexer, -1) + parseParlist(lexer)



def parseFuncbody(lexer):
   #print('>>> FUNCBODY')
    return parseWord(lexer, '(') + parseParlist(lexer) + parseWord(lexer, ')') + parseBlock(lexer) + parseEnd(lexer)


def parseFuncname(lexer):
   #print('>>> FUNCNAME')

    token = lexer.get_token()
    if (name.match(token)):
        return token + parseFuncname(lexer)
    elif (token == '.'):
        token = lexer.get_token()
        if (name.match(token)):
            return '.' + token + parseFuncname(lexer)
        else:
            return token
    elif (token == ':'):
        token = lexer.get_token()
        if (name.match(token)):
            return ':' + token + parseFuncname(lexer)
        else:
            return token
    else:
        lexer.push_token(token)
        return ''


def parseFunction(lexer):
   #print(">>> FUNCTION")
    token = lexer.get_token()
    if (token == 'function'):
        return token + parseFuncbody(lexer)
    else:
        global errors
        errors.append('function not found')
        return ''


def parseStat(lexer, recur = 0):
   #print(">>> STAT")
    global errors
    global get_next_stat
    token = lexer.get_token()
    if(token in ['end'] or token == lexer.eof or token == ''):
        lexer.push_token(token)
        errors.append('end of text error')
        return ''
    if token == 'do':
        return token + parseBlock(lexer) + parseWord(lexer, 'end')
    elif token == 'while':
        return token + parseWhile(lexer)
    elif token == 'repeat':
        return token + parseRepeat(lexer)
    elif token == 'if':
        return token + parseIf(lexer) + parseElseif(lexer) + parseElse(lexer) + parseEnd(lexer)
    elif token == 'for':
        lexercp = copy.deepcopy(lexer)
        result = parseName(lexercp)
        nexttoken = lexercp.get_token()
        if (len(errors) == 0 and nexttoken == '='):
            copyLexer(lexer, lexercp)
            return token + result + '=' + parseFor(lexer)
        else:
            lexer.push_token(nexttoken)
            return token + parseNamelist(lexer, -1) + parseForin(lexer)
    elif token == 'function':
        return token + parseFuncname(lexer) + parseFuncbody(lexer)
    elif token == 'local':
        lexercp = copy.deepcopy(lexer)
        if (lexercp.get_token() == 'function'):
            return token + parseLocalfunction(lexer)
        else:
            lexercp = copy.deepcopy(lexer)
            result = token + parseNamelist(lexercp, -1)
            if len(errors) == 0:
                copyLexer(lexer, lexercp)
                token = lexer.get_token()
                if (token == '='):
                    lexercp = copy.deepcopy(lexer)
                    result2 = parseExplist(lexercp)
                    if len(errors) == 0:
                        copyLexer(lexer, lexercp)
                        return result + '=' + result2
                    else:
                        errors.append('expected an explist')
                else:
                    lexer.push_token(token)
                return result
            else:
                errors.append('expected a parsename list')
                lexer.push_token(token)
                return ''
    elif token in reservedTokens:
        return ''
    else:
        lexer.push_token(token)

    lexercp = copy.deepcopy(lexer)
    errors = []
    result = parseVarlist(lexercp)
    if len(errors) == 0:
        copyLexer(lexer, lexercp)
        return result + parseWord(lexer, '=') + parseExplist(lexer)
    elif get_next_stat == 1:
        get_next_stat = 0
        print_errors()
        token = lexer.get_token()
        print('the token responsible is: ' + token)
        errors = []
        return parseStat(lexer)
    else:
        errors = []

    lexercp = copy.deepcopy(lexer)
    result = parseFunctioncall(lexercp)
    if len(errors) == 0:
        copyLexer(lexer, lexercp)
        return result

    errors.append('no stat found')
    return ''


def parseChunk(lexer):
   #print('>>> CHUNK')
    global errors
    errors = []

    token = lexer.get_token()
    if (token == lexer.eof or token == ''):
        return ''
    elif token == 'return':
        errors = []
        lexercp = copy.deepcopy(lexer)
        result = parseExplist(lexercp)
        if len(errors) == 0:
            copyLexer(lexer, lexercp)
            token2 = lexer.get_token()
            lexer.push_token(token2)
            return token + result
        else:
            errors = []
            return token
    elif token == 'break':
        return token
    lexer.push_token(token)

    lexercp = copy.deepcopy(lexer)
    result = parseStat(lexercp)
    if (len(errors) == 0):
        copyLexer(lexer, lexercp)
        token = lexer.get_token()
        if token == ';':
            temp = result + token + parseChunk(lexer)
            return temp
        lexer.push_token(token)
        temp = result + parseChunk(lexer)
        return temp
    else:
        copyLexer(lexer, lexercp)
        errors = []
        return result


def parseBlock(lexer):
   #print('>>> BLOCK')
    return parseChunk(lexer)


def parseBinop(lexer):
    token = lexer.get_token()
    if (token in ['+', '-', '*', '/', '^', '%', '.', '<', '>' , '=', '~', 'and', 'or']):
        return token

    else:
        global errors
        errors.append('no binop found')
        lexer.push_token(token)
        return ''


def print_errors():
    global errors
    for error in errors:
        print(error)
    errors = []

def parse(filename):
    inputfile = open(filename, 'rt').read()
    lexer = tokenize(inputfile)
    return parseBlock(lexer)

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])