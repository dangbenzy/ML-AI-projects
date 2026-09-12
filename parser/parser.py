import nltk
import sys
nltk.download('punkt_tab')

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
S -> NP VP | S Conj S
NP -> Det N | Det AdjP N | N | NP PP | NP Conj NP
VP -> V | V NP | V NP PP | V PP | VP Adv | Adv VP | VP PP | VP Conj VP | V VP
PP -> P NP | PP Conj PP
AdjP -> Adj | Adj AdjP
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
    word_list= nltk.tokenize.word_tokenize(sentence)
    for n in range(len(word_list)):
        word_list[n]= word_list[n].lower()

    for word in word_list.copy():
        if word.isalpha():
            continue
        else:
            if any(char.isalpha() for char in word):
                continue
            else:
                word_list.remove(word)

    return word_list

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunk= []
    for subtree in  tree.subtrees():
        if subtree.label() == 'NP':
            # Check if this NP contains no smaller NP inside it
            if not any( child.label() == 'NP' for child in subtree.subtrees(lambda t: t != subtree)):
                chunk.append(subtree)

    return chunk


if __name__ == "__main__":
    main()
