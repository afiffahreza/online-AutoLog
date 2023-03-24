from pyspark.sql.functions import explode, split
# import numpy as np

# ==================== Term weighting ====================
# Given a chunk after parsing, term weighting is done by:
# (i) tokening the log lines of the chunk into terms,
# (ii) counting the occurrences of the terms within the chunk,
# (iii-baseline) storing the baseline terms to db.
# (iii-learned) compute a numeric score for the chunk based on the occurrences of the terms.

# === (i) & (ii) ===
def tokenize(lines):
    # Split the lines into words
    words = lines.select(
        explode(
            split(lines.value, " ")
        ).alias("word")
    )
    # Remove empty words
    words = words.filter(words.word != "")

    # Count the occurrences of the terms within the chunk
    wordCounts = words.groupBy("word").count()

    # Output the result to a json file, overwriting the existing file
    wordCounts.coalesce(1).write.mode("overwrite").json("output")

    return wordCounts

# === (iii-baseline) ===
def store(word_count_pairs: list):
    # Push the word counts to the database
    # TO DO connect uwu
    print(word_count_pairs)
    print(type(word_count_pairs))
    print(type(word_count_pairs[0]))

# === (iii-learned) ===
def weight(wordCounts: list):
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
    np = object()

    for word in wordCounts:
        # Get the total number of occurrences of term t in all chunks
        Nt = 0 # TODO: get from db
        Nt += word.count
        # Get the number of chunks
        M = 0 # TODO: get from db
        M += 1
        # Compute the log entropy of term t in all chunks
        M = 0 # TODO: get from db
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
    for word in wordCounts:
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
