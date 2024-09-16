import json
import os
import sys
from datetime import datetime
from openai import OpenAI

# Load API key from config.json
with open('config.json', 'r') as f:
    config = json.load(f)
api_choice = config.get('api_choice', 'openai').lower()

if api_choice == 'openai':
    client = OpenAI(api_key=config['api_key'])
elif api_choice == 'claude':
    # Assuming you have a similar client setup for Claude
    from anthropic import Claude
    client = Claude(api_key=config['api_key'])
else:
    raise ValueError("Invalid API choice in config.json. Choose 'openai' or 'claude'.")

class Expert:
    def __init__(self, name, expertise, personality):
        self.name = name
        self.expertise = expertise
        self.personality = personality

    def __str__(self):
        return f"{self.name} (Expertise: {self.expertise}, Personality: {self.personality})"

class ExpertCouncil:
    def __init__(self):
        self.experts = []
        self.history = []
        self.current_turn = None

    def add_expert(self, name, expertise, personality):
        expert = Expert(name, expertise, personality)
        self.experts.append(expert)
        print(f"\033[92mAdded expert:\033[0m {expert}")

    def start_discussion(self):
        print("\033[94mWelcome to the Expert Council Simulation!\033[0m")
        print("\033[94mType your first message or add AI experts using the /add command.\033[0m")
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() == "/add":
                self.add_expert_flow()
            else:
                self.handle_user_message(user_input)

    def add_expert_flow(self):
        name = input("Enter a unique name for the expert: ")
        expertise = input("Enter the area of expertise: ")
        personality = input("Enter personality traits: ")
        self.add_expert(name, expertise, personality)

    def load_experts_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        name, rest = line.split(" (Expertise: ")
                        expertise, personality = rest.split(", Personality: ")
                        personality = personality.rstrip(")")
                        self.add_expert(name.strip(), expertise.strip(), personality.strip())
            print(f"Experts loaded from {filename}")
        else:
            print(f"File {filename} not found.")
    def handle_user_message(self, message):
        if message.strip().lower().startswith("/add "):
            filename = message.strip()[5:]
            self.load_experts_from_file(filename)
        else:
            self.history.append({"Live Person": message})
            self.prompt_expert_response()
            # Remove the last user message and the expert's response from history
            self.history.pop()
            self.history.pop()

    def prompt_expert_response(self):
        print("\033[93mWho should reply? Options: A (All), N (None), or expert number.\033[0m")
        for idx, expert in enumerate(self.experts):
            print(f"{idx}: {expert}")
        choice = input("\033[93mYour choice:\033[0m ").strip().upper()
        if choice == "A":
            for expert in self.experts:
                self.expert_reply(expert)
        elif choice == "N":
            return
        else:
            try:
                expert_idx = int(choice)
                if 0 <= expert_idx < len(self.experts):
                    self.expert_reply(self.experts[expert_idx])
            except ValueError:
                print("Invalid choice. Please try again.")

    def expert_reply(self, expert):
        try:
            expert_descriptions = "\n".join([f"{exp.name}: Expertise in {exp.expertise}, Personality: {exp.personality}" for exp in self.experts if exp != expert])

            if api_choice == 'openai':
                messages = [{"role": "system", "content": f"""
                You are {expert.name}, an expert in {expert.expertise} with a {expert.personality} personality. 
                Here are the other experts:\n{expert_descriptions}. \n\n 
                Keep it conversational. Don't jump to conclusions and don't start with solutions. Minimize bullet points.
                Do not answer for other experts. Only answer for yourself.
                Don't focus on the points already made.
                Focus on your unique strengths and experiences, don't try to give generic, well-rounded advice"""}]

                for entry in self.history:
                    for role, content in entry.items():
                        if role == expert.name:
                            messages.append({"role": "assistant", "content": content})
                        elif role == "Live Person":
                            messages.append({"role": "user", "content": f"Live Person: {content}"})
                            messages.append({"role": "user", "content": content})
                response = client.chat.completions.create(model="gpt-4o", messages=messages)
                response_text = response.choices[0].message.content.strip()

            elif api_choice == 'claude':
                # Assuming Claude API has a similar interface
                prompt = f"""
                You are {expert.name}, an expert in {expert.expertise} with a {expert.personality} personality. 
                Here are the other experts:\n{expert_descriptions}. \n\n 
                Keep it conversational. Don't jump to conclusions and don't start with solutions. Minimize bullet points.
                Do not answer for other experts. Only answer for yourself.
                Don't focus on the points already made.
                Focus on your unique strengths and experiences, don't try to give generic, well-rounded advice
                """
                response = client.completions.create(prompt=prompt, history=self.history)
                response_text = response['completion'].strip()
        except Exception as e:
            response_text = f"Error in generating response: {str(e)}"
        print(f"\033[96m{expert.name}:\033[0m {response_text}")
        self.history.append({expert.name: response_text})
        self.save_state()

    def save_state(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"council_state_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump({
                "experts": [vars(expert) for expert in self.experts],
                "history": self.history,
                "current_turn": self.current_turn
            }, f, indent=4)
        print(f"State saved to {filename}")

    def load_state(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.experts = [Expert(**exp) for exp in data["experts"]]
                self.history = data["history"]
                self.current_turn = data["current_turn"]
            print(f"State loaded from {filename}")
        else:
            print(f"File {filename} not found.")

def main():
    council = ExpertCouncil()
    if len(sys.argv) > 1:
        council.load_state(sys.argv[1])
    council.start_discussion()

if __name__ == "__main__":
    main()
