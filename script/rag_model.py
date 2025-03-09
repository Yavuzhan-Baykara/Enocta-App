import json
import torch
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import os

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="rag_log.log",
    filemode="w"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

# Model ve Tokenizer'ı yükle
MODEL_PATH = "models/Meta-Llama-3-8B-Instruct"
logging.info("Model ve tokenizer yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, torch_dtype=torch.float16, device_map="auto"
)
logging.info("Model başarıyla yüklendi.")

def load_json(file_path):
    logging.info(f"JSON dosyası yükleniyor: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logging.info(f"JSON dosyası yüklendi. Toplam {len(data)} transkript bulundu.")
    return data

def chunk_transcript(text, title, max_tokens=1000):
    logging.info(f"Transkript uzunluğu: {len(text)} karakter. Chunking işlemi başlatılıyor.")
    tokens = tokenizer.encode(text, truncation=False)
    chunks = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    decoded_chunks = [f"Başlık: {title}\n{tokenizer.decode(chunk)}" for chunk in chunks]
    logging.info(f"Transkript {len(decoded_chunks)} parçaya bölündü.")
    return decoded_chunks

def create_bm25_index(transcripts):
    logging.info("BM25 için indeks oluşturuluyor...")
    corpus = [chunk for transcript in transcripts for chunk in transcript["chunks"]]
    tokenized_corpus = [chunk.split() for chunk in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    logging.info(f"BM25 indeksi oluşturuldu. Toplam {len(corpus)} chunk indekslendi.")
    return bm25, corpus

def search_bm25(query, bm25, corpus, top_n=3):
    logging.info(f"Kullanıcı sorgusu alındı: {query}")
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    best_chunks = [corpus[i] for i in top_indices]
    max_score = scores[top_indices[0]] if top_indices else 0
    logging.info(f"En iyi {top_n} chunk belirlendi. Seçilen indeksler: {top_indices}, max score: {max_score}")
    return best_chunks, max_score

def format_prompt(prompt, retrieved_documents, k=1):
    """Retrieve edilen dökümanları modele uygun formatta sunar"""
    formatted_prompt = f"Soru: {prompt}\nBağlam:\n"
    for idx in range(min(k, len(retrieved_documents))):
        formatted_prompt += f"{retrieved_documents[idx]}\n"
    return formatted_prompt

def generate(formatted_prompt, rag_context=None):
    # Bellek aşımını önlemek için prompt'u sınırla
    formatted_prompt = formatted_prompt[:2000]

    # Eğer RAG bağlamı varsa, bunu yan bilgi olarak kullan; doğrudan kopyalamayın.
    if rag_context:
        analysis_instruction = (
            "Aşağıda verilen yan bilgiyi referans olarak kullan, ancak bu bilgiyi doğrudan kopyalama. "
            "Bu yan bilgiyi analiz et, özümse ve kendi bilgilerinle harmanlayarak soruya özgün, profesyonel bir cevap oluştur. "
            "Yan bilgi, sana ilave bir perspektif kazandırmak için sağlanmıştır; ana cevap senin kendi analiz ve bilgilerin üzerine olsun. \n\nYan Bilgi:\n" + rag_context
        )
    else:
        analysis_instruction = "Doğrudan konuya odaklanarak cevap ver. Selamlama veya kişisel ifadeler ekleme."

    messages = [
        {
            "role": "system",
            "content": (
                "Sen bir liderlik koçu ve akıllı bir asistansın. "
                "Sorulara detaylı, içgörülü ve analitik Türkçe cevaplar ver. "
                "Cevabını, verilen yan bilgiyi referans olarak kullanarak, kendi analiz ve bilgilerinle oluştur. "
                "Lütfen selamlama veya kişisel hitap ekleme."
                "Sadece Türkçe cevap ver"
            )
        },
        {
            "role": "user",
            "content": f"{analysis_instruction}\n\nSoru: {formatted_prompt}"
        }
    ]

    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        input_ids,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.6,
        top_p=0.90
    )

    response_tokens = outputs[0][input_ids.shape[-1]:]
    response = tokenizer.decode(response_tokens, skip_special_tokens=True)
    logging.info(f"Model yanıt üretti: {response[:200]}...")
    return response



# Global initialization: JSON verisini yükle, transkriptleri chunk'lara böl ve BM25 indeksini oluştur.
logging.info("Global initialization başlatılıyor...")
json_path = "leader.json"
data = load_json(json_path)
for item in tqdm(data, desc="Chunking transcripts"):
    item["chunks"] = chunk_transcript(item["transcript"], item["title"])
bm25, corpus = create_bm25_index(data)
logging.info("Global initialization tamamlandı.")

def process_instruction(instruction):
    """
    Gelen sorguyu kullanarak BM25 üzerinden ilgili chunk'ları alır.
    Eğer BM25 skoru 0.3'ün altındaysa yalnızca web araması yapar,
    0.3'ün üzerindeyse BM25 bağlamı ile web araması sonucunu birleştirir.
    Ayrıca, web araması sonucu kullanılan kaynaklar (title ve link) referans olarak çıkışa eklenir.
    """
    best_chunks, max_score = search_bm25(instruction, bm25, corpus)
    threshold = 0.3

    # Web araması için DuckDuckGoSearchResults aracını kullan (çıktıyı liste olarak almak için output_format="list")
    try:
        from langchain_community.tools import DuckDuckGoSearchResults
        search_tool = DuckDuckGoSearchResults(output_format="list")
        web_results = search_tool.run(instruction)
        logging.info("Web araması başarılı.")
    except Exception as e:
        logging.error(f"Web araması sırasında hata: {e}")
        web_results = []

    # Kaynak referanslarını oluştur
    references = []
    if isinstance(web_results, list):
        for res in web_results:
            ref = f"{res.get('title', 'No Title')} - {res.get('link', 'No Link')}"
            references.append(ref)

    if max_score < 0.25:
        logging.info("BM25 skoru 0.25'in altında, sadece web araması sonucu kullanılacak.")
        web_context = "\n".join([res.get("snippet", "") for res in web_results]) if web_results else ""
        context = web_context

    elif 0.25 <= max_score < 0.50:
        logging.info("BM25 skoru 0.25 ile 0.50 arasında, BM25 bağlamı ve web araması sonucu birleştirilecek.")
        bm25_context = "\n".join(best_chunks)
        web_context = "\n".join([res.get("snippet", "") for res in web_results]) if web_results else ""
        context = bm25_context + "\n" + web_context
    
    else:  # 0.50 <= max_score <= 1.00
        logging.info("BM25 skoru 0.50'nin üzerinde, sadece RAG bağlamı kullanılacak.")
        context = "\n".join(best_chunks)


    formatted_prompt = format_prompt(instruction, [context], k=1)
    answer = generate(formatted_prompt)
    return answer, references
