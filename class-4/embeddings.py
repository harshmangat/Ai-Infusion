from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

vectors = model.encode("A cat is sleeping on the sofa.")
print(vectors.shape)  # Output: (384, )
print(vectors[:5])  # Output: [0.123, -0.456, ..., 0.789]

# to compare two pieces of text -> encode both -> take cosine similarity

from numpy import dot
from numpy.linalg import norm

v1 = model.encode("A cat is sleeping on the sofa.")
v2 = model.encode("A dog is napping on the couch.")
similarity = dot(v1, v2) / (norm(v1) * norm(v2))
print(similarity)  # Output: 0.85 (or similar value, indicating high similarity)