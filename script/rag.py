import json
import torch
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers.util import cos_sim

# JSON dosyasını yükle
with open("leader.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Yeni embedding modeli (Trendyol TYBERT)
embeddings = HuggingFaceEmbeddings(model_name="Trendyol/tybert")

# Metni daha iyi bölmek için RecursiveCharacterTextSplitter kullanıyoruz
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)

documents = []
for entry in data:
    video_id = entry["video_id"]
    title = entry["title"]
    transcript = entry["transcript"]
    
    # Metni böl
    split_texts = text_splitter.split_text(transcript)
    
    for chunk in split_texts:
        documents.append({"video_id": video_id, "title": title, "transcript": chunk})

# Tüm parçaları vektörlere dönüştür
document_embeddings = embeddings.embed_documents([doc["transcript"] for doc in documents])

def retrieve_relevant_passage(query, top_k=2):
    """
    Kullanıcının sorgusuna en uygun transkript bölümlerini döndürür.
    - HuggingFaceEmbeddings kullanarak vektör karşılaştırma yapıyoruz.
    """
    query_embedding = embeddings.embed_query(query)
    
    # Similarity hesapla
    similarities = [cos_sim(torch.tensor(query_embedding), torch.tensor(doc_emb)) for doc_emb in document_embeddings]

    # En yüksek skorlu dokümanları al
    sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]

    relevant_texts = []
    for idx in sorted_indices:
        relevant_texts.append({
            "title": documents[idx]["title"],
            "transcript": documents[idx]["transcript"][:500],  # Bağlamı daha kısa tut (maks. 500 karakter)
            "score": similarities[idx].item()
        })

    return relevant_texts
