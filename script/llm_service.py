from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from rag import retrieve_relevant_passage

# DeepSeek-R1 Modelini Yükleme
MODEL_PATH = "models/deepseek-r1-distill-qwen-7b"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16, device_map="auto")

def clean_response(response):
    """
    Model çıktısını temizler ve sadece gerçek yanıtı döndürür.
    - `</think>` ve gereksiz tekrarları kaldırır.
    """
    # `<think>` veya benzeri kelimelerden sonrası çıkarılmalı
    response = response.split("</think>")[-1].strip()

    # Gereksiz tekrarları engelle
    if "Yanıt:" in response:
        response = response.split("Yanıt:")[-1].strip()

    return response

def process_instruction(instruction, max_tokens=200):
    """
    Kullanıcının sorusuna en uygun yanıtı üretmek için LLM kullanır.
    - Bağlamdan özet çıkararak sonuç üretir.
    - Sonucu doğal bir dilde anlatır.
    - Çıktıyı temizler ve sadece mantıklı yanıt döndürür.
    """
    try:
        # En alakalı transkript parçalarını getir
        relevant_texts = retrieve_relevant_passage(instruction, top_k=2)

        # Bağlamı oluştur (maksimum 500 karakter ile sınırlandır)
        context = "\n\n".join([f"Başlık: {doc['title']}\n{doc['transcript'][:500]}" for doc in relevant_texts])

        # Model için daha iyi bir prompt oluştur
        prompt = (
            f"Kullanıcı Sorusu: {instruction}\n\n"
            f"Bağlam:\n{context}\n\n"
            f"Yanıt:\n"
            f"Bağlamdaki bilgileri analiz ederek {instruction} sorusuna detaylı ve mantıklı bir yanıt oluştur. "
            f"Sadece verilen bilgileri kullan, ancak gereksiz tekrar yapma. "
            f"Kısa ve öz bir şekilde anlat. Çıkarımlar yap ve özetleyici bir cevap oluştur."
        )

        # Tokenize et ve modele gönder
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)

        # Modeli çalıştır
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,  # max_length yerine max_new_tokens kullan
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )

        # Çıktıyı temizle ve döndür
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return clean_response(response)

    except Exception as e:
        return f"Hata oluştu: {str(e)}"
