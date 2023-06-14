def stem(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    step1a_suffixes = ['sses', 'ies', 'ss', 's']
    step1b_suffixes = ['eed', 'eedly', 'ed', 'edly', 'ing', 'ingly']
    step2_suffixes = ['ational', 'ate', 'ation', 'ator', 'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize', 'ise']
    step3_suffixes = ['ational', 'tional', 'alize', 'icate', 'iciti', 'ical', 'ful', 'ness']
    step4_suffixes = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize', 'ise']
    step5a_suffixes = ['e']
    step5b_suffixes = ['ll']
    step2_ending = ''
    
    # Step 1a
    for suffix in step1a_suffixes:
        if word.endswith(suffix):
            word = word[:-len(suffix)]
            break
    
    # Step 1b
    for suffix in step1b_suffixes:
        if word.endswith(suffix):
            if suffix in ['eed', 'eedly']:
                if word[-len(suffix)-1] in vowels:
                    word = word[:-len(suffix)] + 'ee'
            else:
                step2_ending = suffix
                word = word[:-len(suffix)]
            break
    
    # Step 2
    for suffix in step2_suffixes:
        if word.endswith(suffix):
            step2_ending = suffix
            word = word[:-len(suffix)]
            break
    
    # Step 3
    for suffix in step3_suffixes:
        if word.endswith(suffix):
            if suffix in ['icate', 'ative', 'alize']:
                word = word[:-len(suffix)] + 'e'
            elif suffix in ['iciti', 'ical', 'ful', 'ness']:
                pass
            else:
                word = word[:-len(suffix)]
            break
    
    # Step 4
    for suffix in step4_suffixes:
        if word.endswith(suffix):
            if suffix in ['ion']:
                if word[-len(suffix)-1] in ['s', 't']:
                    word = word[:-len(suffix)]
            else:
                word = word[:-len(suffix)]
            break
    
    # Step 5a
    for suffix in step5a_suffixes:
        if word.endswith(suffix):
            if len(word[:-len(suffix)]) >= 2:
                word = word[:-len(suffix)]
            else:
                word += 'e'
            break
    
    # Step 5b
    if word.endswith(tuple(step5b_suffixes)) and len(word) > 4 and word[-2] == word[-1]:
        word = word[:-1]
    
    # Append step 2 suffix, if present
    word += step2_ending
    
    return word
