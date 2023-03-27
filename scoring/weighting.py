import numpy as np

# === (iii-learned) ===
def weight(word_count_pairs: dict, db, app):
    # Access db to get the total number of terms in all chunks

    # Compute a numeric score for the chunk based on the occurrences of the terms using log entropy

    # Global Weighting
    # xtj: number of occurrences of term t in chunk j
    # Nt: total number of occurrences of term t in all chunks
    # Ptj: fraction of occurrences of term t in all chunks
    # Ptj = xtj / Nt
    # et: entropy of term t in all chunks
    # M: total number of chunks, including the current chunk
    # et = 1 + ( sum(ptj * log2(ptj)) / log2(M))

    term_entropy = []
    # np = object()

    word_count_pairs_list = []
    for word, count in word_count_pairs.items():
        word_count_pairs_list.append({"word": word, "count": count})

    for word in word_count_pairs_list:
        # Get the total number of occurrences of term t in all chunks
        Nt = 0 # TODO: get from db
        Nt += word.count
        # Get the number of chunks
        M = 0 # TODO: get from db
        M += 1
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
        term_entropy.append({"word": word.word, "score": et})

    # Local Weighting
    # xt: number of occurrences of term t
    # wt: weight of term t
    # wt = log2(1+xt)
    local_weight = []
    for word in word_count_pairs_list:
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
