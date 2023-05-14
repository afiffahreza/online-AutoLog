import pickle
import numpy as np

class Scoring:   
    
    def __init__(self):
        self.chunks_num = 0
        self.chunks = []
        self.terms = {}
        self.entropies = {}
    
    def load(self, path):
        with open(path, 'rb') as f:
            self.chunks_num = pickle.load(f)
            self.chunks = pickle.load(f)
            self.terms = pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.chunks_num, f)
            pickle.dump(self.chunks, f)
            pickle.dump(self.terms, f)
    
    def tokenize(self, lines):
        terms = [line.split() for line in lines]
        terms = [term for line in terms for term in line]
        chunk = {}
        for term in terms:
            if term not in chunk:
                chunk[term] = 0
            chunk[term] += 1
        return chunk

    def add_lines(self, lines):
        current_chunk = self.tokenize(lines)
        self.chunks_num += 1
        self.chunks.append(current_chunk)
        for term in current_chunk:
            if term not in self.terms:
                self.terms[term] = current_chunk[term]
            else:
                self.terms[term] += current_chunk[term]

    def calculate_baseline_entropies(self):
        for term in self.terms:
            total_P = 0
            for chunk in self.chunks:
                if term in chunk:
                    global_occurrences = self.terms[term]
                    local_occurrences = chunk[term]
                    P = local_occurrences / global_occurrences
                    total_P += P * np.log2(P)  
            self.entropies[term] = 1 + (total_P / np.log2(self.chunks_num))
    
    def calculate_baseline_score(self):
        self.calculate_baseline_entropies()
        scores = []
        for chunk in self.chunks:
            current_score = 0
            current_terms = {}
            for term in chunk:
                if term not in current_terms:
                    current_terms[term] = 0
                current_terms[term] += chunk[term]
            for term, count in current_terms.items():
                local_weight = np.log2(1 + count)
                current_score += np.square(local_weight * self.entropies[term])
            scores.append(np.sqrt(current_score))
        return scores
    
    def calculate_new_entropy(self, term, count):
        total_P = 0
        entropy = 0
        if term not in self.terms:
            global_occurrences = 0
        else:
            global_occurrences = self.terms[term]
        global_occurrences += count
        for chunk in self.chunks:
            if term in chunk:
                local_occurrences = chunk[term]
                P = local_occurrences / global_occurrences
                total_P += P * np.log2(P)
        total_P += (count / global_occurrences) * np.log2(count / global_occurrences)
        entropy = 1 + (total_P / np.log2(self.chunks_num + 1))
        return entropy
    
    def calculate_score(self, lines):
        current_chunk = self.tokenize(lines)
        current_score = 0
        current_terms = {}
        for term in current_chunk:
            if term not in current_terms:
                current_terms[term] = 0
            current_terms[term] += current_chunk[term]
        for term, count in current_terms.items():
            local_weight = np.log2(1 + count)
            current_score += np.square(local_weight * self.calculate_new_entropy(term, count))
        return np.sqrt(current_score)

# Test
if __name__ == '__main__':
    scoring = Scoring()
    scoring.add_lines(['this is just an example is just an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is an hehe haha hehe i am just an example', 'this is just an example is just an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is just an example is just i am just an example'])
    scoring.add_lines(['this is an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is just an example is just an hehe haha', 'hehe i am just an example'])
    scoring.add_lines(['this is an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is just an example is just an hehe haha hehe i am just an example', 'this is an hehe haha hehe i am just an example'])
    scoring.add_lines(['this this this this this this this this this'])
    scoring.add_lines(['is just an example is just an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is just an example is just an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is just an example is just an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is an hehe haha hehe i am just an example'])
    scoring.add_lines(['this is just an example is just an hehe haha hehe i am just an example'])
    scoring.add_lines(['what'])

    # save
    scoring.save('scoring.pkl')

    print(scoring.calculate_baseline_score())
    print(scoring.calculate_score(['what']))

    # load
    scoring_load = Scoring()
    scoring_load.load('scoring.pkl')

    print(scoring_load.calculate_baseline_score())
    print(scoring_load.calculate_score(['what']))
