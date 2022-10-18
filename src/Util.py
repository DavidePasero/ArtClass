'''
Module that should contain pleny of useful functions, it actually contains only one function
'''

# Returns the index inside line where the inline string starting with start_index ends
# We first have to specify the symbol that is used for the string (because some languages have several symbols
# to indicate strings f.e. javascript has both ' and ")
def index_ending_inline_string(lang, symbol: str, line: str, start_index: int) -> int:
    for idx, c in enumerate(line):
        # if idx != index_quotes (they're not the same double quotes) and it is not in an escape sequence
        if c == symbol and idx > start_index and line[idx - 1] != lang.escape_symbol:
            return idx
    
    # If we've explored the whole line and we haven't found a closing quote, then that quote at index index_quotes
    # was a single independent quote like \"
    return -1
