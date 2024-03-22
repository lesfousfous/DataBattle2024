from database import SolutionDB, CaseStudy, Reference, Secteur, Database
from gensim.corpora import Dictionary
import gensim
from gensim import similarities

# print(scores)
db = Database()
cursor = db.database_connection.cursor()

cursor.execute("SELECT numsolution from tblsolution")
solutions_ids = [x[0] for x in cursor.fetchall()]
solutions = [SolutionDB(id) for id in solutions_ids]
documents = [solution.title + " " +
             solution.description for solution in solutions]


# Tokenize the documents
tokenized_documents = [doc.lower().split() for doc in documents]

# Create a Gensim Dictionary
dictionary = Dictionary(tokenized_documents)

# Create a Corpus (Bag of Words representation of the documents)
corpus = [dictionary.doc2bow(doc) for doc in tokenized_documents]

# Using BM25
bm25 = gensim.models.LsiModel(corpus, id2word=dictionary, num_topics=150)

# Now, you can use bm25 to get scores for a given query.
query = "panneau solaire".lower().split()
query_bow = dictionary.doc2bow(query)
query_bm25 = bm25[query_bow]
index = similarities.MatrixSimilarity(bm25[corpus])
sims = index[query_bm25]

sims = sorted(enumerate(sims), key=lambda item: -item[1], reverse=True)
for doc_position, doc_score in sims:
    print(doc_score, documents[doc_position])
