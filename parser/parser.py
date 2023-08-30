import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> N V | N VP | NP VP | N VP Conj N V | NP VP NP | N VP Conj N VP 

NP -> N | Det N | Det NP | NP NP | P N | Adj N | Det NP | P NP | Adj NP

VP -> V N | V NP | Adv V | VP NP | V Adv | VP Conj VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # Download the Punkt tokenizer
    nltk.download('punkt')

    # Convert sentence to a list of words
    tokens = nltk.tokenize.word_tokenize(sentence)

    # Return a list of lowercased words that contain at least one alphabetic character
    return [word.lower() for word in tokens if word.isalpha()]


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    npc_list = []

    # Iterate over all subtrees in the tree
    for subtree in tree.subtrees():
        # If the subtree is a noun phrase
        if subtree.label() == "NP":
            # If the subtree contains another noun phrase, then skip it
            if len([subsubtree for subsubtree in subtree.subtrees() if subsubtree.label() == "NP"]) > 1:
                continue

            npc_list.append(subtree)
    return npc_list


if __name__ == "__main__":
    main()
