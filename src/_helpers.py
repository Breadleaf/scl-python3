import string
import enum

class SCLTokenType(enum.Enum):
    SEPERATOR = enum.auto()
    ASSIGNMENT = enum.auto()
    ITERATOR = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
    IDENTIFIER = enum.auto()


def load_helper_tokenize(text: str) -> list:
    tokens = []

    for line in text.split("\n"):
        line_gen = (character for character in line)

        for character in line_gen:

            # Parse Syntax Elements

            if character == '#':
                tokens.append((SCLTokenType.SEPERATOR,))
                break

            if character in string.whitespace:
                if character == '\n':
                    tokens.append((SCLTokenType.SEPERATOR,))
                continue

            if character == '=':
                tokens.append((SCLTokenType.ASSIGNMENT,))
                continue

            if character == '_':
                tokens.append((SCLTokenType.ITERATOR,))
                continue

            # Parse Strings

            identifier = ''
            in_quotes = False
            if character == '"':
                in_quotes = True
                character = next(line_gen, None)
                while character != '"' and character is not None:
                    identifier += character
                    character = next(line_gen, None)
                tokens.append((SCLTokenType.STRING, identifier))
                # eat the last quote
                character = next(line_gen, None)
                if character == None: # reached end of line
                    tokens.append((SCLTokenType.SEPERATOR,))
                continue

            # Parse Numbers

            identifier = ''
            in_decimal = False
            in_negative = False
            if character in string.digits + '-.':
                if character == '-':
                    in_negative = True
                    character = next(line_gen, None)
                    if character not in string.digits:
                        print("Invalid number: negative sign without number")
                        break

                while character in string.digits or character == '.':
                    if character == '.':
                        if in_decimal:
                            print("Invalid number: multiple decimal points")
                            break
                        in_decimal = True
                    identifier += character
                    character = next(line_gen, " ")
                    if character in string.whitespace:
                        character = None # end of line; hacky way to break the loop FIX THIS 
                        break
                tokens.append((SCLTokenType.NUMBER, float(identifier)))
                if character == None:
                    tokens.append((SCLTokenType.SEPERATOR,))
                continue

            # Parse Identifiers

            identifier = ''
            if character in string.ascii_letters:
                while character in string.ascii_letters:
                    identifier += character
                    character = next(line_gen, " ")
                    if character in string.whitespace:
                        break
                tokens.append((SCLTokenType.IDENTIFIER, identifier))
                if character == "\n":
                    tokens.append((SCLTokenType.SEPERATOR,))
                continue

    # Remove sequential seperators

    final_tokens = []
    for token in tokens:
        if token[0] == SCLTokenType.SEPERATOR:
            if final_tokens and final_tokens[-1][0] == SCLTokenType.SEPERATOR:
                continue

        final_tokens.append(token)

    # Remove leading seperator and ending seperator if present

    if final_tokens and final_tokens[0][0] == SCLTokenType.SEPERATOR:
        final_tokens.pop(0)

    if final_tokens and final_tokens[-1][0] == SCLTokenType.SEPERATOR:
        final_tokens.pop(-1)

    # Append a seperator to the end of the list

    final_tokens.append((SCLTokenType.SEPERATOR,))

    return final_tokens


def load_helper_parse(tokens: list) -> dict:
    expressions = []
    temp_expression = []

    for token in tokens:
        if token[0] != SCLTokenType.SEPERATOR:
            temp_expression.append(token)
        else:
            expressions.append(temp_expression)
            temp_expression = []

    # Validate the expressions and convert them into a dictionary

    config = {}

    for expression in expressions:
        # find where the first ASSIGNMENT is and split into right and left

        assignment_index = None
        for index, token in enumerate(expression):
            if token[0] == SCLTokenType.ASSIGNMENT:
                assignment_index = index
                break

        if assignment_index is None:
            print("Invalid expression, no assignment found")
            continue

        left = expression[:assignment_index]
        right = expression[assignment_index + 1:]

        # if the len of right is not 1, it is invalid
        if len(right) != 1:
            #print("left: ", left)
            #print("right: ", right)
            print("Invalid expression, right side of assignment is invalid")
            continue

        # if there is an assignment in the right, it is invalid
        for token in right:
            if token[0] == SCLTokenType.ASSIGNMENT:
                print("Invalid expression, duplicate assignment found")
                break

        # make sure the right is a valid type: number or string or etc
        if right[0][0] not in [SCLTokenType.STRING, SCLTokenType.NUMBER]:

            print("Invalid expression, right side of assignment is invalid")
            continue
            
        # if there is anything other than an identifier in the left, it is invalid
        iterator_count = 0
        for token in left:
            if token[0] not in [SCLTokenType.IDENTIFIER, SCLTokenType.ITERATOR]:
                print("Invalid expression, invalid token found in left side of assignment")
                break

            if token[0] == SCLTokenType.ITERATOR:
                iterator_count += 1

        # iterator can only be the last token
        if iterator_count == 1 and left[-1][0] != SCLTokenType.ITERATOR:
            print("Invalid expression, invalid iterator found in left side of assignment")
            continue

        # there can only be one iterator
        if iterator_count > 1:
            print("Invalid expression, multiple iterators found in left side of assignment")
            continue

        # update the config dictionary

        current_level = config
        for idx, token in enumerate(left):
            if idx < len(left) - 1:
                if left[idx + 1][0] == SCLTokenType.ITERATOR:
                    current_level = current_level.setdefault(token[1], [])
                else:
                    current_level = current_level.setdefault(token[1], {})
            else:
                if token[0] == SCLTokenType.ITERATOR:
                    if not isinstance(current_level, list):
                        print("Invalid expression, iterator found in non-list")
                        break
                    else:
                        current_level.append(right[0][1])
                else:
                    current_level[token[1]] = right[0][1]

    return config


def load_helper(text: str) -> dict:
    return load_helper_parse(load_helper_tokenize(text))


def dump_helper(data: dict) -> str:
    # TODO: Implement this
    pass
