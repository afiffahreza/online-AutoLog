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
            if Ptj != 0:
                sum_Ptj_log2_Ptj += (Ptj * np.log2(Ptj))

        et = 1 + (sum_Ptj_log2_Ptj / np.log2(M))
        # Save et to term_entropy
        term_entropy[term] = et

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
            term_score = term_score * term_score
            score += term_score
        scores.append(np.sqrt(score))

    # Return the score of the chunk
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
    terms = []

    for term_count in baseline:
        for term, count in term_count.items():
            if term in Nt:
                Nt[term] += count
            else:
                Nt[term] = count
                terms.append(term)

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
            if Ptj != 0:
                sum_Ptj_log2_Ptj += (Ptj * np.log2(Ptj))

        et = 1 + (sum_Ptj_log2_Ptj / np.log2(M))
        # Save et to term_entropy
        term_entropy[term] = et

    # Local Weighting
    # xt: number of occurrences of term t
    # wt: weight of term t
    # wt = log2(1+xt)
    score = 0
    for term, count in current.items():
        # Get the number of occurrences of term t
        xt = count
        # Compute the weight of term t
        wt = np.log2(1+xt)
        term_score = wt * term_entropy[term]
        term_score = term_score * term_score
        score += term_score
    
    # Return the score of the chunk
    return score
