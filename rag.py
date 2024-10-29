# -*- coding: utf-8 -*-
"""rag2.0

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15x4M0d-4UYQXP-JcEwH5n4sfdNqmtRW4
"""

!pip install cohere faiss-cpu pymupdf

# Step 1: Install required libraries


# Step 2: Import Libraries
import cohere
import faiss
import numpy as np
import fitz  # PyMuPDF

# Step 3: Set up Cohere API with your key
API_KEY = 'x'  # Replace with your Cohere API key
co = cohere.Client(API_KEY)

# Step 4: Define function to read a PDF document and split it into chunks
def load_pdf(filepath):
    """Extracts text from each page of a PDF file."""
    document_text = ""
    with fitz.open(filepath) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            document_text += page.get_text("text")
    return document_text

def chunk_text(text, max_chunk_size=500):
    """Splits text into chunks of max_chunk_size tokens."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i + max_chunk_size])
        chunks.append(chunk)
    return chunks

# Step 5: Embed chunks and store them in FAISS index
def create_faiss_index(chunks):
    # Generate embeddings for each chunk
    embeddings = co.embed(texts=chunks).embeddings
    embeddings = np.array(embeddings).astype("float32")

    # Initialize FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings

# Step 6: Search function to retrieve top-k chunks
def search_faiss_index(index, query, chunks, k=3):
    # Get the query embedding
    query_embedding = co.embed(texts=[query]).embeddings
    query_embedding = np.array(query_embedding).astype("float32")

    # Search the index for similar chunks
    _, indices = index.search(query_embedding, k)
    results = [chunks[i] for i in indices[0]]
    return " ".join(results)

# Step 7: Function to generate response using Cohere's model
def generate_response(context, query):
    prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
    response = co.generate(
        model='command-xlarge-nightly',  # You can change to other Cohere models
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
        stop_sequences=["\n"]
    )
    return response.generations[0].text.strip()

# Step 8: Putting it all together: Document Loading, Indexing, and Q&A

# Load and preprocess PDF document
filepath = '/content/Params_Resume_new_new (2).pdf'  # Replace with your document path
document = load_pdf(filepath)
chunks = chunk_text(document)

# Create FAISS index
index, embeddings = create_faiss_index(chunks)

# Query loop
print("Ask questions about the document (type 'exit' to quit):")
while True:
    query = input("Your Question: ")
    if query.lower() == 'exit':
        break

    # Retrieve relevant chunks and generate a response
    context = search_faiss_index(index, query, chunks, k=3)
    answer = generate_response(context, query)
    print(f"Answer: {answer}\n")