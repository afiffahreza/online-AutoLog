import pickle
import numpy as np

class ScoringV2:   
    
    def __init__(self):
        self.lines_num = 0
        self.lines = []
        self.terms_num = 0
        self.terms = {}
        self.entropies = {}
    
    def load(self, path):
        with open(path, 'rb') as f:
            self.lines_num = pickle.load(f)
            self.lines = pickle.load(f)
            self.terms_num = pickle.load(f)
            self.terms = pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.lines_num, f)
            pickle.dump(self.lines, f)
            pickle.dump(self.terms_num, f)
            pickle.dump(self.terms, f)

    def add_line(self, line):
        self.lines_num += 1
        self.lines.append(line)
        line = line.split()
        for term in line:
            if term not in self.terms:
                self.terms_num += 1
                self.terms[term] = 0
            self.terms[term] += 1

    def calculate_baseline_entropies(self):
        for term in self.terms:
            total_P = 0
            for line in self.lines:
                line = line.split()
                global_occurrences = self.terms[term]
                local_occurrences = line.count(term)
                P = local_occurrences / global_occurrences
                if P != 0:
                    total_P += P * np.log2(P)  
            self.entropies[term] = 1 + (total_P / np.log2(self.lines_num))
    
    def calculate_baseline_score(self):
        self.calculate_baseline_entropies()
        scores = []
        for line in self.lines:
            line = line.split()
            current_score = 0
            current_terms = {}
            for term in line:
                if term not in current_terms:
                    current_terms[term] = 0
                current_terms[term] += 1
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
        for line in self.lines:
            line = line.split()
            local_occurrences = line.count(term)
            P = local_occurrences / global_occurrences
            if P != 0:
                total_P += P * np.log2(P)
        total_P += (count / global_occurrences) * np.log2(count / global_occurrences)
        entropy = 1 + (total_P / np.log2(self.lines_num + 1))
        return entropy
    
    def calculate_score(self, line):
        line = line.split()
        current_score = 0
        current_terms = {}
        for term in line:
            if term not in current_terms:
                current_terms[term] = 0
            current_terms[term] += 1
        for term, count in current_terms.items():
            local_weight = np.log2(1 + count)
            current_score += np.square(local_weight * self.calculate_new_entropy(term, count))
        return np.sqrt(current_score)

# Test
if __name__ == '__main__':
    scoring = ScoringV2()
    scoring.add_line('this is just an example is just an hehe haha hehe i am just an example')
    scoring.add_line('this is an hehe haha hehe i am just an example')
    scoring.add_line('this is just an example is just i am just an example')
    scoring.add_line('this is an hehe haha hehe i am just an example')
    scoring.add_line('this is just an example is just an hehe haha')
    scoring.add_line('this is an hehe haha hehe i am just an example')
    scoring.add_line('this is just an example is just an hehe haha hehe i am just an example')
    scoring.add_line('this this this this this this this this this')
    scoring.add_line('is just an example is just an hehe haha hehe i am just an example')
    scoring.add_line('this is just an example is just an hehe haha hehe i am just an example')
    scoring.add_line('this is an hehe haha hehe i am just an example')
    scoring.add_line('this is just an example is just an hehe haha hehe i am just an example')
    scoring.add_line('this is an hehe haha hehe i am just an example')
    scoring.add_line('this is just an example is just an hehe haha hehe i am just an example')
    scoring.add_line('what')

    # save
    scoring.save('scoringv2.pkl')

    print(scoring.calculate_baseline_score())
    print(scoring.calculate_score('what'))

    # load
    scoring_load = ScoringV2()
    scoring_load.load('scoringv2.pkl')

    print(scoring_load.calculate_baseline_score())
    print(scoring_load.calculate_score('what'))