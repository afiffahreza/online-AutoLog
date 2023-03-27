import numpy as np

# === (iii-learned) ===
def weight_baseline(baseline: list):
    # Compute a numeric score for the chunk based on the occurrences of the terms using log entropy

    # Global Weighting
    # xtj: number of occurrences of term t in chunk j
    # Nt: total number of occurrences of term t in all chunks
    # Ptj: fraction of occurrences of term t in all chunks
    # Ptj = xtj / Nt
    # et: entropy of term t in all chunks
    # M: total number of chunks, including the current chunk
    # et = 1 + ( sum(ptj * log2(ptj)) / log2(M))

    Nt = {}
    terms = []

    for term_count in baseline:
        for term, count in term_count.items():
            if term in Nt:
                Nt[term] += count
            else:
                Nt[term] = count
                terms.append(term)
    
    print("===== Terms =====")
    print(terms)
    print("===== Nt =====")
    print(Nt)

    M = len(baseline)
    term_entropy = {}

    # Entropy for each term
    for term in terms:
        # Get the total number of occurrences of term t in all chunks
        current_Nt = Nt[term]

        # Compute the log entropy of term t in all chunks
        sum_Ptj_log2_Ptj = 0
        for term_count in baseline:
            # Get the number of occurrences of term t in chunk j
            if term in term_count:
                xtj = term_count[term]
            else:
                xtj = 0
            # Compute the fraction of occurrences of term t in all chunks
            Ptj = xtj / current_Nt
            # Compute the sum of the product of Ptj and log2(Ptj)
            sum_Ptj_log2_Ptj += Ptj * np.log2(Ptj)

        et = 1 + (sum_Ptj_log2_Ptj / np.log2(M))
        # Save et to term_entropy
        term_entropy[term] = et

    print("===== Term Entropy =====")
    print(term_entropy)

    # Local Weighting
    # xt: number of occurrences of term t
    # wt: weight of term t
    # wt = log2(1+xt)
    scores = []
    for term_count in baseline:
        score = 0
        for term, count in term_count.items():
            # Get the number of occurrences of term t
            xt = count
            # Compute the weight of term t
            wt = np.log2(1+xt)
            term_score = wt * term_entropy[term]
            term_score = score * score
            score += term_score
        scores.append(np.sqrt(score))

    # Output the score of the chunk
    print(scores)
    return scores

# === (iii-learned) ===
def weight(baseline: list, current: dict):
    # Compute a numeric score for the chunk based on the occurrences of the terms using log entropy

    # Global Weighting
    # xtj: number of occurrences of term t in chunk j
    # Nt: total number of occurrences of term t in all chunks
    # Ptj: fraction of occurrences of term t in all chunks
    # Ptj = xtj / Nt
    # et: entropy of term t in all chunks
    # M: total number of chunks, including the current chunk
    # et = 1 + ( sum(ptj * log2(ptj)) / log2(M))

    Nt = {}

    for term_count in baseline:
        for term, count in term_count.items():
            if term in Nt:
                Nt[term] += count
            else:
                Nt[term] = count
    
    M = len(baseline) + 1
    term_entropy = {}

    for word, count in current.items():
        # Get the total number of occurrences of term t in all chunks
        current_Nt = Nt[word]
        current_Nt += count

        # Compute the log entropy of term t in all chunks
        sum_Ptj_log2_Ptj = 0
        for i in range(M):
            # Get the number of occurrences of term t in chunk j
            xtj = 0 # TODO: get from db
            # Compute the fraction of occurrences of term t in all chunks
            Ptj = xtj / Nt
            # Compute the sum of the product of Ptj and log2(Ptj)
            sum_Ptj_log2_Ptj += Ptj * np.log2(Ptj)
        et = 1 + (sum_Ptj_log2_Ptj / np.log2(M))
        # Save et to term_entropy
        if word in term_entropy:
            term_entropy[word] += et
        else:
            term_entropy[word] = et

    # Local Weighting
    # xt: number of occurrences of term t
    # wt: weight of term t
    # wt = log2(1+xt)
    local_weight = []
    for word, count in current.items():
        # Get the number of occurrences of term t
        xt = word.count
        # Compute the weight of term t
        wt = np.log2(1+xt)
        # Save wt to term_entropy
        local_weight.append({"word": word.word, "score": wt})

    # Final chunk score
    # s: score of the chunk
    # s = root(sum(square(et log2(1+xt))))
    score = 0
    for i in range(len(term_entropy)):
        score += term_entropy[i].score * local_weight[i].score
        score = score * score
    score = np.sqrt(score)

    # Output the score of the chunk
    print(score)
    return score

    # for term_count in baseline:
    #     score = {}
    #     current_score = weight(baseline, term_count)
    #     score['score'] = current_score
    #     score['app'] = app
    #     score['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     store_normal_score(db, score)

    # score = {}
    # current_score = weight(baseline, wordCounts)
    # score['score'] = current_score
    # score['app'] = app
    # score['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # store_normal_score(db, score)
    # store_normal_terms(db, app, wordCounts)
