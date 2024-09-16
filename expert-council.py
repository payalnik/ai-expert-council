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
    import anthropic
    client = anthropic.Anthropic(api_key=config['api_key'])
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
            elif user_input.strip().lower() == "/generate":
                self.generate_experts()
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

    def generate_experts(self):
        scenario = input("Describe the scenario for which you need experts: ")
        prompt = f"Generate a list of experts for the following scenario: {scenario}. Format each expert as 'Name (Expertise: expertise, Personality: personality)'."

        if api_choice == 'openai':
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            expert_list = response.choices[0].message.content.strip()

        elif api_choice == 'claude':
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            expert_list = response.content[0].text.strip()

        print("\033[92mGenerated Experts:\033[0m")
        print(expert_list)

        # Add generated experts to the chat
        for line in expert_list.splitlines():
            if line.strip() and " (Expertise: " in line and ", Personality: " in line:
                try:
                    name, rest = line.split(" (Expertise: ")
                    expertise, personality = rest.split(", Personality: ")
                    personality = personality.rstrip(")")
                    self.add_expert(name.strip(), expertise.strip(), personality.strip())
                except ValueError:
                    print(f"Skipping malformed line: {line}")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = os.path.join('chats', f"generated_experts_{timestamp}.txt")
        with open(filename, 'w') as f:
            f.write(expert_list)
        print(f"Generated experts saved to {filename}")


    def handle_user_message(self, message):
        self.history.append({"Live Person": message})
        self.prompt_expert_response()
        # Remove the last user message and the expert's response from history
        if len(self.history) >= 2:
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

                user_messages = []
                assistant_messages = []

                for entry in self.history:
                    for role, content in entry.items():
                        if role == expert.name:
                            assistant_messages.append(content)
                        elif role == "Live Person":
                            user_messages.append(content)

                if user_messages:
                    messages.append({"role": "user", "content": " ".join(user_messages)})
                if assistant_messages:
                    messages.append({"role": "assistant", "content": " ".join(assistant_messages)})
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
                messages = [{"role": "system", "content": prompt}]
                
                combined_user_message = ""
                for entry in self.history:
                    for role, content in entry.items():
                        if role == expert.name:
                            if combined_user_message:
                                messages.append({"role": "user", "content": combined_user_message.strip()})
                                combined_user_message = ""
                            messages.append({"role": "assistant", "content": content})
                        else:
                            combined_user_message += f"{role}: {content} "
                if combined_user_message:
                    messages.append({"role": "user", "content": combined_user_message.strip()})

                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,  # Adjust this value as needed
                    system=prompt,
                    messages=messages
                )
                response_text = response.content[0].text.strip()
        except Exception as e:
            response_text = f"Error in generating response: {str(e)}"
        print(f"\033[96m{expert.name}:\033[0m {response_text}")
        self.history.append({expert.name: response_text})
        self.save_state()

    def save_state(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        os.makedirs('chats', exist_ok=True)
        filename = os.path.join('chats', f"council_state_{timestamp}.json")
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
