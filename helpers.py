import re

RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

def is_nonterminal(nt):
    return re.match(RE_NONTERMINAL, nt)

def canonical(grammar):
    def split(expansion):
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        return [token for token in re.split(
            RE_NONTERMINAL, expansion) if token]

    return {
        k: [split(expression) for expression in alternatives]
        for k, alternatives in grammar.items()
    }

def concat_lists(lists):
    return sum(lists, start=[])

def in_symbols(cf_grammar):
    return {key: concat_lists(value) for key, value in canonical(cf_grammar).items()}
