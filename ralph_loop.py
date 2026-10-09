import os
import json
import re
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
    api_key=os.getenv("NEBIUS_API_KEY")
)

# Using Nemotron Super for the fast coding loop
MODEL_NAME = "nebius/nvidia/nemotron-3-super-120b-a12b" 
MAX_ITERATIONS = 5 

def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)

def run_loop():
    for i in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== Ralph Loop Iteration {i} ===")
        
        with open(".ralph/prd.json", "r") as f:
            prd = json.load(f)
            
        progress = read_file(".ralph/progress.txt")
        system_prompt = read_file("ralph_prompt.md")

        current_task = next((task for task in prd["stories"] if not task["passes"]), None)
        
        if not current_task:
            print("All tasks are complete! The loop is finished.")
            break

        print(f"Executing Task {current_task['id']}: {current_task['description']}")

        user_prompt = f"""
        Current Progress / Context:
        {progress}
        
        Your IMMEDIATE TASK: {current_task['description']}
        
        You MUST output your response in this EXACT format:
        
        FILEPATH: path/to/your/file.py
        ```python
        # your code here
        ```
        
        LEARNINGS:
        Write 1-2 sentences here about what you just built.
        """

        print("Querying Nebius Token Factory...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2 
        )
        
        reply = response.choices[0].message.content

        filepath_match = re.search(r"FILEPATH:\s*(.+)", reply)
        code_match = re.search(r"```(?:python)?\n(.*?)```", reply, re.DOTALL)
        learnings_match = re.search(r"LEARNINGS:\s*(.+)", reply, re.DOTALL)

        if filepath_match and code_match:
            filepath = filepath_match.group(1).strip()
            code = code_match.group(1).strip()
            
            write_file(filepath, code)
            print(f"Successfully wrote code to {filepath}")
            
            current_task["passes"] = True
            with open(".ralph/prd.json", "w") as f:
                json.dump(prd, f, indent=2)
                
            if learnings_match:
                learnings = learnings_match.group(1).strip()
                with open(".ralph/progress.txt", "a") as f:
                    f.write(f"\nTask {current_task['id']} completed: {learnings}\n")
            
            print("State files updated. Wiping memory and sleeping for 3 seconds...")
            time.sleep(3)
        else:
            print("AI failed format. Halting.")
            break

if __name__ == "__main__":
    run_loop()