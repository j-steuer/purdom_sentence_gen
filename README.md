# Purdom Sentence Generator

A generator for a small set of short sentences from a context-free grammar based on Paul Purdom's 'A sentence generator for testing parsers'.
This Python implementation closely follows the interpretation of the algorithm as detailed in 'An Interpretation of Purdom's Algorithm for Automatic Generation of Test Cases' by Brian A. Malloy and James F. Power.

# Usage

Specify a context-free grammar as shown in the examples in the main file.
Use this grammar to initialize a new PurdomSentenceGenerator object (make sure the starting symbol of your grammar is either the default one or specify your own when initializing the object).
To get a list of generated sentences, simply take the result of the generate_sentences() method.
To simply print out the sentences, you can run print_sentences() instead.

# Credit
Paul Purdom for the original algorithm

Brian A. Malloy and James F. Power for the new interpretation of the algorithm

The Fuzzing Book for the canonical and is_nonterminal methods
