import runpod
import time
from llm_service import process_instruction

def handler(event):
    input_data = event.get('input', {})
    instruction = input_data.get('instruction', "default instruction")
    seconds = input_data.get('seconds', 0)

    time.sleep(seconds)

    result = process_instruction(instruction)
    return result

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
