import runpod
from rag_model import process_instruction
from elevenlabs_tts import text_to_speech_elevenlabs

def handler(event):
    input_data = event.get('input', {})
    instruction = input_data.get('text', "default instruction")
    
    # LLM yanıtını al
    answer, references = process_instruction(instruction)
    
    # ElevenLabs ile ses üret ve S3'e yükle
    try:
        voice_url = text_to_speech_elevenlabs(answer)
    except Exception as e:
        voice_url = str(e)

    return {
        "output": answer,
        "references": references,
        "voice_url": voice_url  # S3'teki erişim linkini döndür
    }

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
