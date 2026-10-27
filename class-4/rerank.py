from sentence_transformers import CrossEncoder


reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

question = "How long do I have to return shoes?"

# Sample candidates let you see CrossEncoder ranking without setting up Chroma.
candidates = [
    "Customers can return unused shoes within 30 days of purchase.",
    "Shoes are available in sizes 6 through 12.",
    "Refunds are issued to the original payment method after a return is approved.",
    "Shipping is free for orders above ₹999 across India.",
    "Items bought on sale can be exchanged within 14 days.",
    "Watches come with a one-year warranty.",
]

# Optional: replace the sample candidates above with Chroma results.
# candidates = [
#     doc.page_content
#     for doc in db.similarity_search(question, k=25)
# ]

pairs = [(question, candidate) for candidate in candidates]
scores = reranker.predict(pairs)
ranked = sorted(zip(scores, candidates), key=lambda item: item[0], reverse=True)

print(f"Question: {question}\n")
print("Top 3 results:")
for rank, (score, candidate) in enumerate(ranked[:3], start=1):
    print(f"{rank}. score={score:.3f} | {candidate}")
