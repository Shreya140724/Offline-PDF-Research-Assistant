import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

PDF_DIR = "data"
VECTOR_DIR = "vectorstore"

def extract_meta(text):
    lines = text.split("\n")[:40]
    title = lines[0].strip()

    authors = ""
    for l in lines:
        if "," in l and len(l) < 120:
            authors = l.strip()
            break

    return title, authors

def main():
    docs = []

    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_DIR, file)
            loader = PyPDFLoader(path)
            pages = loader.load()

            title, authors = extract_meta(pages[0].page_content)

            for p in pages:
                p.metadata["source"] = file
                p.metadata["title"] = title
                p.metadata["authors"] = authors

            docs.extend(pages)

    print("Loaded pages:", len(docs))

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    print("Chunks:", len(chunks))

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_DIR, exist_ok=True)
    db.save_local(VECTOR_DIR)

    print("Vectorstore created.")

if __name__ == "__main__":
    main()
