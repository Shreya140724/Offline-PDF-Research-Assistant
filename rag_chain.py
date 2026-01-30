from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

VECTOR_DIR = "vectorstore"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = FAISS.load_local(VECTOR_DIR, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_kwargs={"k": 6})

llm = OllamaLLM(model="llama3")

PROMPT = ChatPromptTemplate.from_template("""
You are a research assistant.

Answer ONLY from provided context.

Rules:
- Never invent papers.
- Never add authors not in metadata.
- If info is missing, say: Not present in uploaded PDFs.

If multiple PDFs:
Answer per paper.

Context:
{context}

Question:
{question}

Answer:
""")

def ask(question):
    docs = retriever.invoke(question)

    context = ""
    for d in docs:
        context += f"""
SOURCE: {d.metadata.get('source')}
TITLE: {d.metadata.get('title')}
AUTHORS: {d.metadata.get('authors')}

{d.page_content}

"""

    chain = PROMPT | llm
    return chain.invoke({"context": context, "question": question})
