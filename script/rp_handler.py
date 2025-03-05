import json
import runpod
import time
from llm_service import process_instruction

def handler(event):
    input_data = event.get('input', {})
    instruction = input_data.get('text', "default instruction")
    max_tokens = input_data.get('max_tokens', 100)

    result = process_instruction(instruction, max_tokens)

    return {"output": result}

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
