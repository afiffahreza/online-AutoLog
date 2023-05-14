from gensim.models import LogEntropyModel
from gensim.test.utils import common_texts
from gensim.corpora import Dictionary

print(common_texts)
dct = Dictionary(common_texts)  # fit dictionary
print(dct)
corpus = [dct.doc2bow(row) for row in common_texts]  # convert to BoW format
print(corpus)
model = LogEntropyModel(corpus)  # fit model
vector = model[corpus[1]]  # apply model to document
print(vector)

testphrase = "the amount of response time is 20ms"
testphrase = testphrase.split()
dct.add_documents([testphrase])
print(dct)
corpus.append(dct.doc2bow(testphrase))
model = LogEntropyModel(corpus)
result = model[corpus[-1]]
print(result)
