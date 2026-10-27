from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = [
    "lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10,
)

chunks = splitter.split_text(
    "\n".join(docs)
)

print(len(chunks))  # Output: 2