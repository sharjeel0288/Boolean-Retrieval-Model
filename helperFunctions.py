import nltk
from stemmer import stem
from collections import Counter


def stopWordList(filename="Stopword-List.txt"):
    stop_words = []
    with open(filename, 'r') as file:
        text = file.read()
        stop_words = text.split()
    return stop_words


def preprocess(text, stop_words):

    tokens = nltk.word_tokenize(text.lower())

    tokens = [token for token in tokens if token.isalpha() and (',') not in token
              and token not in stop_words]
    tokens = [stem(token) for token in tokens]
    return tokens


def get_document_extracts(n):
    extracts = []
    for i in range(1, n+1):
        filename = f"Dataset/{i}.txt"
        with open(filename, 'r') as file:
            document = file.read()
            words = document.split()
            extract_words = words[:10]
            extract = ' '.join(extract_words)
            if len(words) > 10:
                extract += '...'
            extracts.append(extract)
    return extracts


def documentTokenizer(n, stopWords):
    docs_tokens = []
    for i in range(1, n+1):
        with open(f"Dataset/{i}.txt", "r") as file:
            text = file.read()
            table = str.maketrans('', '', '-.\':[,](),')
            text = text.translate(table)

            tokens = preprocess(text, stopWords)
            doc_tokens = {"doc_id": i, "tokens": tokens}
            docs_tokens.append(doc_tokens)
    return docs_tokens


def invertedIndex(docs_tokens):
    inverted_index = {}
    for doc in docs_tokens:
        doc_id = doc['doc_id']
        for pos, token in enumerate(doc['tokens']):
            if token not in inverted_index:
                inverted_index[token] = []
            inverted_index[token].append((doc_id, pos))
    sorted_index = dict(sorted(inverted_index.items()))
    return inverted_index


def parse_query(query_string):
    stop_words = stopWordList()
    proximity = None
    table = str.maketrans('', '', '-.\':[,](),')
    query_string = query_string.translate(table)
    if 'and' not in query_string and 'not' not in query_string and 'or'not in query_string:
        terms = nltk.word_tokenize(query_string.lower())
        wordList = []
        for term in terms:
            if term not in stop_words and term.isalpha():
                wordList.append(stem(term))
        return wordList, [], [], 1

    def queryProcessing(word):
        if (word.isalpha()) and word not in stop_words:
            word = stem(word)
            return word

    and_topics = []
    or_topics = []
    not_topics = []

    # Split the query string into individual terms
    terms = nltk.word_tokenize(query_string.lower())
    for word in terms:
        if '/' in word:
            proximity = word.replace('/', '')

    # Loop through each term and categorize based on operator
    # print(terms)
    for i in range(0, len(terms)):
        word = terms[i]
        if (word == 'and'):
            and_topics.append(queryProcessing(terms[i-1]))
            and_topics.append(queryProcessing(terms[i+1]))
            i += 1
            continue
        elif word == 'or':
            or_topics.append(queryProcessing(terms[i-1]))
            or_topics.append(queryProcessing(terms[i+1]))
            i += 1
            continue
        elif word == 'not':
            not_topics.append(queryProcessing(terms[i+1]))
            i += 1
            continue
    for word in and_topics:
        if word in or_topics:
            or_topics.remove(word)
    return list(filter(lambda x: x is not None, and_topics)), list(filter(lambda x: x is not None, or_topics)), list(filter(lambda x: x is not None, not_topics)), proximity


def proximity_query(index, andTerms, orTerms, notTerms, k):
    # First, we'll create a set of all the documents that contain any of the terms in orTerms.
    orDocs = set()
    for term in orTerms:
        if term in index:
            orDocs |= set(index[term])

    # Next, we'll create a set of all the documents that contain all of the terms in andTerms.
    andDocs = set()
    for term in andTerms:
        if term in index:
            if len(andDocs) == 0:
                andDocs = set(index[term])
            else:
                andDocs &= set(index[term])

    # Finally, we'll subtract the set of documents that contain any of the terms in notTerms from the set of documents that contain all of the terms in andTerms.
    notDocs = set()
    for term in notTerms:
        if term in index:
            notDocs |= set(index[term])
    andDocs -= notDocs

    # Now we'll loop through each document in the andDocs set and see if any of the terms in orTerms appear within k words of each other.
    results = set()
    if '' in index:
        for doc in andDocs:
            docTerms = index[''][doc]
            for i, term in enumerate(docTerms):
                if term in orTerms:
                    for j in range(i+1, min(len(docTerms), i+k+1)):
                        if docTerms[j] in orTerms:
                            results.add(doc)
                            break

    return results



def boolean_query_search(inverted_index, and_list=[], or_list=[], not_list=[]):
    # Get the postings for each term in the AND list
    and_postings = [inverted_index.get(term, []) for term in and_list]

    # Get the postings for each term in the OR list
    or_postings = [inverted_index.get(term, []) for term in or_list]

    # Get the postings for each term in the NOT list
    not_postings = [inverted_index.get(term, []) for term in not_list]

    # Get the set of documents containing all terms in the AND list
    and_docs = set()
    if and_postings:
        and_docs = set.intersection(
            *[set([doc_pos[0] for doc_pos in posting]) for posting in and_postings])

    # Get the set of documents containing any terms in the OR list
    or_docs = set()
    if or_postings:
        or_docs = set.union(
            *[set([doc_pos[0] for doc_pos in posting]) for posting in or_postings])

    # Get the set of documents containing none of the terms in the NOT list
    not_docs = set()
    if not_postings:
        not_docs = set.union(
            *[set([doc_pos[0] for doc_pos in posting]) for posting in not_postings])

    # Get the set of documents that pass the AND and NOT conditions
    # Get the set of documents that pass the AND and NOT conditions
    result = and_docs.difference(not_docs)

    # If there are any OR conditions, add them to the result set
    if or_docs:
        result = result.union(or_docs.difference(not_docs))

    return list(result)


def phrase_query(index, phrase):
    # Split the phrase into individual terms
    terms, _, _, _ = parse_query(phrase)

    # Find candidate documents that contain the first term
    try:
        candidate_docs = set(index[terms[0]])
    except:
        return set()

    for i in range(1, len(terms)):
        term = terms[i]
        try:
            term_docs = set(index[term])
        except:
            continue
        prev_term = terms[i-1]

        # Find the set of documents that contain both terms
        common_docs = [(doc_id, pos) for (doc_id, pos)
                       in candidate_docs if (doc_id, pos+1) in term_docs]

        new_phrase_docs = set()
        # Iterate over the common documents and check if the terms appear in the correct order
        for doc_id, pos in common_docs:
            prev_doc_positions = [posting[1]
                                  for posting in index[prev_term] if posting[0] == doc_id]
            term_doc_positions = [posting[1]
                                  for posting in index[term] if posting[0] == doc_id]
            if pos in prev_doc_positions and pos+1 in term_doc_positions:
                new_phrase_docs.add((doc_id, pos+1))

        candidate_docs = new_phrase_docs

        if not candidate_docs:
            return set()
    candidate_docs = list(candidate_docs)
    result = []
    for candidate_doc, pos in candidate_docs:
        result.append(candidate_doc)
    freq = Counter(result)
    result = sorted(result, key=lambda x: freq[x])
    result = [x for i, x in enumerate(result) if x not in result[:i]]
    result.reverse()
    return result

def intersect(postings1, postings2, postings3):
    return set(postings1) & set(postings2) & set(postings3)

def merge(postings):
    return set().union(*postings)

def advance_search(inverted_index, and_list, or_list=[], not_list=[], k=1):
    # Get the postings for each term in the AND list
    and_postings = [inverted_index.get(term, []) for term in and_list]

    # Get the postings for each term in the OR list
    or_postings = [inverted_index.get(term, []) for term in or_list]

    # Get the postings for each term in the NOT list
    not_postings = [inverted_index.get(term, []) for term in not_list]

    # Merge the AND postings using the merge function
    and_merged_postings = merge(and_postings)

    # Merge the OR postings using the merge function
    or_merged_postings = merge(or_postings)

    # Merge the NOT postings using the merge function
    not_merged_postings = merge(not_postings)

    # Perform the Boolean query using the intersect function
    results = intersect(and_merged_postings,
                        or_merged_postings, not_merged_postings)

    # Perform the proximity query using the proximity_query function
    proximity_results = proximity_query(
        inverted_index, and_list, or_list, not_list, k)

    # Combine the Boolean results and the proximity results
    final_results = results & proximity_results

    # Get the qualified documents
    qualified_docs = [doc_id for doc_id in final_results]

    return qualified_docs


def search(invertedIndex, query):
    query = query.lower()
    result = []
    terms = nltk.word_tokenize(query.lower())
    print(terms)
    print(len(terms))
    if(len(terms)==1):
        result = []
        for candidate_doc, pos in invertedIndex[terms[0]]:
            result.append(candidate_doc)
        freq = Counter(result)
        result = sorted(result, key=lambda x: freq[x])
        result = [x for i, x in enumerate(result) if x not in result[:i]]
        result.reverse()
        print(result)
        return result
    if 'and' not in query and 'or' not in query and 'not'not in query and ' ' in query and '/' not in query:
        print("phraseeeeeeeeeeeeeee")
        result = phrase_query(invertedIndex, query)
    if ('/') in query and ' ' in query:
        print("proximityyyyyyyyyyyyyyyy")
        andt, ort, nott, k = (parse_query(query))
        print(invertedIndex[andt[0]])
        print(parse_query(query))
        result = proximity_query(invertedIndex, andt, ort, nott, int(k))
    if 'and' in query or 'or' in query or 'not' in query or ' ' not in query and '/' not in query:
        print("boooolean")
        andt, ort, nott, k = (parse_query(query))
        print(parse_query(query))
        result = (boolean_query_search(invertedIndex, andt, ort, nott))
    if result:
        return result
    else:
        andt, ort, nott, k = (parse_query(query))
        result=advance_search(invertedIndex,andt, ort, nott, k)
        return []
