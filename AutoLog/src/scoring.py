import pickle, re, json
import numpy as np
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

class Scoring:   
    
    def __init__(self):
        self.chunks_num = 0
        self.chunks = []
        self.terms = {}
        self.entropies = {}

        config = TemplateMinerConfig()
        config.load("drain3.ini")
        config.profiling_enabled = False

        self.templates = TemplateMiner(config=config)
    
    def load(self, path):
        with open(path, 'rb') as f:
            self.chunks_num = pickle.load(f)
            self.chunks = pickle.load(f)
            self.terms = pickle.load(f)
            self.templates = pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.chunks_num, f)
            pickle.dump(self.chunks, f)
            pickle.dump(self.terms, f)
            pickle.dump(self.templates, f)

    def preprocess(self, lines):
        lines = [re.sub('<:.+?:>', '', line) for line in lines]
        lines = [re.sub('[^a-zA-Z0-9\s]', '', line) for line in lines]
        lines = [re.sub('\s+', ' ', line) for line in lines]
        lines = [line.strip() for line in lines]
        lines = [line.lower() for line in lines]
        return lines

    def tokenize(self, lines):
        terms = [line.split() for line in lines]
        terms = [term for line in terms for term in line]
        chunk = {}
        for term in terms:
            if term not in chunk:
                chunk[term] = 0
            chunk[term] += 1
        return chunk
    
    def is_json(self, line):
        try:
            json.loads(line)
        except ValueError as e:
            return False
        return True
    
    def stringify_json(self, line):
        data = json.loads(line)
        return ' '.join([f'{key} {value}' for key, value in data.items()])

    def add_lines(self, lines):
        for line in lines:
            if self.is_json(line):
                line = self.stringify_json(line)
            self.templates.add_log_message(line)
        template_lines = []
        for line in lines:
            if self.is_json(line):
                line = self.stringify_json(line)
            result = self.templates.match(line)
            template_lines.append(result.get_template())
        lines = self.preprocess(template_lines)
        del template_lines
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
        template_lines = []
        for line in lines:
            if self.is_json(line):
                line = self.stringify_json(line)
            result = self.templates.match(line)
            if not result:
                self.templates.add_log_message(line)
            result = self.templates.match(line)
            template_lines.append(result.get_template())
        lines = self.preprocess(template_lines)
        del template_lines
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
