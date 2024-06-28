import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

COLOR = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "ENDC": "\033[0m",
}

from dataformer.llms.openllm import OpenLLM
from dataformer.components.evol_quality.base import EvolQuality
from datasets import load_dataset

from dotenv import load_dotenv

load_dotenv()

dataset = load_dataset("dataformer/self-knowledge")
datasetsub = dataset["train"].select(range(2))
instructions = [example["question"] for example in datasetsub]

llm = OpenLLM(
    model="mixtral-8x7b-32768", api_provider="groq"
)  # Make sure you have set "GROQ_API_KEY" in .env file.

# Generating answers for the question first
request_list = [
    {"messages": [{"role": "user", "content": prompt}]} for prompt in instructions
]
answers = llm.generate(request_list)
answers = [answer[2]["choices"][0]["message"]["content"] for answer in answers]

# Formatting in required format for EvolQuality
inputs = [
    {"instruction": instruction, "response": response}
    for instruction, response in zip(instructions, answers)
]

evol_quality = EvolQuality(
    llm=llm,
    num_evolutions=1,  # Number of times to evolve each response
    store_evolutions=True,  # Store all evolutions, if False only final evolution is shown.
    include_original_response=False,  # Include the original response in evolved_responses
)
results = evol_quality.generate(inputs)

print("\n\n")
for result in results:
    print(f"{COLOR['BLUE']}Instruction: {result['instruction']}{COLOR['ENDC']}")
    print(f"{COLOR['GREEN']}Response: {result['response']}{COLOR['ENDC']}")
    evolved_responses = result["evolved_responses"]
    for evolved_response in evolved_responses:
        print(f"{COLOR['PURPLE']}Evolved Response: {evolved_response}{COLOR['ENDC']}")
    print("\n")
