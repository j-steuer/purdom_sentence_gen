from helpers import *
import math
import re

INFINITE = math.inf
READY = -2
UNSURE = -3
FINISHED = -4

#Example grammars are included at the end of the file
class PurdomSentenceGenerator:
    def __init__(self, cf_grammar, starting_symbol="<start>"):
        self.grammar = self.convert_grammar(cf_grammar)
        self.cf_grammar_symbols = in_symbols(cf_grammar)

        self.slen, self.short, self.rlen, self.dlen = (dict() for _ in range(4))
        self.prev, self.mark, self.once, self.onst = (dict() for _ in range(4))

        self.symbols = set(concat_lists(self.cf_grammar_symbols.values()))
        self.symbols.add(starting_symbol)
        self.nonterminal_symbols = set([symbol for symbol in self.symbols if is_nonterminal(symbol)])
        self.terminal_symbols = self.symbols - self.nonterminal_symbols
        self.productions = list(self.grammar.keys())
        
        self.starting_symbol = starting_symbol
        
        self.stack = []
        
        self.result = ""
        self.sentences = []

    def init_shortest_terminal_string(self):
        if not self.slen or not self.short or not self.rlen:
            self.shortest_terminal_string()

    def init_shortest_derivation(self):
        if not self.dlen or self.prev:
            self.shortest_derivation()

    def convert_grammar(self, grammar):
        i = 0
        d = dict()
        for key, r in grammar.items():
            for option in r:
                d[i] = (key, [symbol for symbol in re.split(RE_NONTERMINAL, option) if symbol])
                if not d[i]:
                    d[i] = [""]
                i += 1
        return d

    def print_sentences(self):
        if not self.sentences:
            self.generate_sentences()
        for sentence in self.sentences:
            print(sentence)
        
    def shortest_terminal_string(self):
        def init():
            for terminal in self.terminal_symbols:
                self.slen[terminal] = len(terminal)
            for nonterminal in self.nonterminal_symbols:
                self.slen[nonterminal] = INFINITE
                self.short[nonterminal] = -1
            for production in self.productions:
                self.rlen[production] = INFINITE

        init()
        change = True
        while change:
            change = False
            for production in self.productions:
                lside, rside = self.grammar[production]
                length = 1
                too_big = False
                for element in rside:
                    if self.slen[element] == INFINITE:
                        too_big = True
                        break
                    else:
                        length += self.slen[element]
                if not too_big and length < self.rlen[production]:
                    self.rlen[production] = length
                    if length < self.slen[lside]:
                        self.short[lside] = production
                        self.slen[lside] = length
                        change = True


        
    def shortest_derivation(self):
        def init():
            self.init_shortest_terminal_string()
            for nonterminal in self.nonterminal_symbols:
                self.dlen[nonterminal] = INFINITE
                self.prev[nonterminal] = -1
            self.dlen[self.starting_symbol] = self.slen[self.starting_symbol]

        init()
        change = True
        while change:
            change = False
            for production in self.productions:
                lside, rside = self.grammar[production]
                if self.rlen[production] == INFINITE:
                    continue
                if self.dlen[lside] == INFINITE:
                    continue
                if self.slen[lside] == INFINITE:
                    continue
                length = self.dlen[lside] + self.rlen[production] - self.slen[lside]
                for nonterminal in [nonterminal for nonterminal in rside if is_nonterminal(nonterminal)]:
                    if length < self.dlen[nonterminal]:
                        change = True
                        self.dlen[nonterminal] = length
                        self.prev[nonterminal] = production
                        
                        
    def generate_sentences(self):

        def lhs(p):
            return self.grammar[p][0]
        
        def rhs(p):
            return self.grammar[p][1]

        def init():
            self.init_shortest_derivation()
            for n in self.nonterminal_symbols:
                self.once[n] = READY
                self.onst[n] = 0
            for p in self.productions:
                self.mark[p] = False

        def short(nt):
            prod_no = self.short[nt]
            self.mark[prod_no] = True
            if self.once[nt] != FINISHED:
                self.once[nt] = READY
            return prod_no
        
        def load_once():
            for p in self.productions:
                if not self.mark[p]:
                    j = self.once[lhs(p)]
                    if j == READY or j == UNSURE:
                        self.once[lhs(p)] = p
                        self.mark[p] = True
        
        def process_stack():
            nonlocal nt, prod_no, do_sentence
            self.onst[nt] -= 1
            for e in tuple(reversed(rhs(prod_no))):
                self.stack.append(e)
                if is_nonterminal(e):
                    self.onst[e] += 1
            
            done = False
            while not done:
                if len(self.stack) == 0:
                    do_sentence = False
                    break
                else:
                    nt = self.stack.pop()
                    if not is_nonterminal(nt):
                        self.result += nt
                    else:
                        done = True
        
        init()
        done = False
        prod_no = None
        while not done:
            if self.once[self.starting_symbol] == FINISHED:
                break
            self.onst[self.starting_symbol] = 1
            if self.result:
                self.sentences.append(self.result)
                self.result = ""
            nt = self.starting_symbol
            do_sentence = True
            while do_sentence:
                once_nt = self.once[nt]
                if nt == self.starting_symbol and once_nt == FINISHED:
                    done = True
                    break
                elif once_nt == FINISHED:
                    prod_no = short(nt)
                elif once_nt >= 0:
                    prod_no = once_nt
                    self.once[nt] = READY
                else:
                    load_once()
                    for i in self.nonterminal_symbols:
                        if i != self.starting_symbol and self.once[i] >= 0:
                            j = i
                            k = self.prev[j]
                            while k >= 0:
                                j = lhs(k)
                                if self.once[j] >= 0:
                                    break
                                else:
                                    if self.onst[i] == 0:
                                        self.once[j] = k
                                        self.mark[k] = True
                                    else:
                                        self.once[j] = UNSURE
                                k = self.prev[j]
                    for n in self.nonterminal_symbols:
                        if self.once[n] == READY:
                            self.once[n] = FINISHED
                    if nt == self.starting_symbol and self.once[nt] < 0 and self.onst[self.starting_symbol] == 0:
                        break
                    elif self.once[nt] < 0:
                        prod_no = short(nt)
                    elif self.once[nt] >= 0:
                        prod_no = self.once[nt]
                        self.once[nt] = READY
                process_stack()
        
        return self.sentences

                
if __name__ == "__main__":
    purdom_grammar = {"<start>": ["<E>"], 
                      "<E>": ["<E>+<T>", "<T>"],
                      "<T>": ["<P>*<T>", "<P>"],
                      "<P>": ["(<E>)", "i"]}
    
    lang_grammar = {"<start>": ["<stmt>"],
                   "<stmt>": ["<assgn>", "<assgn>; <stmt>"],
                   "<assgn>": ["<var> := <rhs>"],
                   "<rhs>": ["<var>", "<digit>"],
                   "<var>": ["x", "y", "z"],
                   "<digit>": [str(i) for i in range(10)]}
    
    generator = PurdomSentenceGenerator(lang_grammar)
    generator.print_sentences()