








def proximity_query(inverted_index, andterms, orterms, notterms, proximity):
    # Combine all query terms into a single list
    query_terms = andterms + orterms
    
    # Get the posting lists for each query term
    posting_lists = [inverted_index.get(term, []) for term in query_terms]
    
    # If any of the query terms are not in the index, return an empty result
    if any(not posting_list for posting_list in posting_lists):
        return []
    
    # Initialize variables for iterating through the posting lists
    num_terms = len(query_terms)
    iterators = [iter(posting_list) for posting_list in posting_lists]
    current_docs = [next(iterator)[0] for iterator in iterators]
    result = []
    
    # Iterate through the posting lists
    while True:
        # If all iterators have reached the end of their posting lists, we're done
        if all(current_doc is None for current_doc in current_docs):
            break
        
        # If any iterators have not yet reached the end of their posting list, find the minimum doc ID
        min_doc = min(current_doc for current_doc in current_docs if current_doc is not None)
        
        # Count the number of query terms that occur within proximity of the minimum doc ID
        num_matching_terms = 0
        for i in range(num_terms):
            if current_docs[i] == min_doc:
                num_matching_terms += 1
                if num_matching_terms == len(query_terms):
                    result.append(min_doc)
                    break
                
            # If the next doc ID for this term is within proximity, update the current doc ID
            while current_docs[i] is not None and current_docs[i] < min_doc:
                try:
                    current_docs[i] = next(iterators[i])[0]
                except StopIteration:
                    current_docs[i] = None
        
        # If we haven't found a match yet, check the next minimum doc ID
        for i in range(num_terms):
            while current_docs[i] is not None and current_docs[i] < min_doc + proximity:
                try:
                    current_docs[i] = next(iterators[i])[0]
                except StopIteration:
                    current_docs[i] = None
    
    # Exclude any documents that match the notterms list
    notterm_docs = set()
    for notterm in notterms:
        notterm_docs.update(set(posting[0] for posting in inverted_index.get(notterm, [])))
    result = [doc_id for doc_id in result if doc_id not in notterm_docs]
    
    return result






inverted_index = {
    'apple': [(1,2),(2,2)],
    'banana': [(1, 4)],
    'babar': [(2, 291), (2, 519)],
}
andterms=['apple', 'banana']
orterms=[]
notterms=[]
proximity = 0

result = proximity_query(inverted_index, andterms, orterms, notterms, proximity)
print(result)  # Output: [1]
