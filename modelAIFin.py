from transformers import pipeline, set_seed ,AutoTokenizer, AutoModelForCausalLM
import json
import torch

# Load the data
with open("historical_events.json", "r") as file:
    events = json.load(file)

# Use a small text generation model
generator = pipeline("text-generation", model="gpt2")
set_seed(42)

# Function to generate people involved in the event
def generate_people(event_description):
    prompt = f"List some important people involved in the following historical event:\n{event_description}\nPeople involved:"
    result = generator(prompt, max_length=50, num_return_sequences=1)
    return result[0]['generated_text'].split("People involved:")[1].strip().split("\n")[0]

# Function to generate timeline of the event
def generate_timeline(event_description):
    prompt = f"List the timeline between which the event and its sub-events occurred:\n{event_description}\nTimeline:"
    result = generator(prompt, max_length=50, num_return_sequences=1)

    return result[0]['generated_text'].split("Timeline:")[1].strip().split("\n")[0]

# Enhance the dataset with generated people and timeline
for event in events:
    # Generate people and timeline for each event
    event["generated_people"] = generate_people(event["description"])
    event["generated_timeline"] = generate_timeline(event["description"])

# Save the enhanced file
output_path = "enhanced_historical_events.json"
with open(output_path, "w") as out_file:
    json.dump(events, out_file, indent=4)

print("File saved to:", output_path)

# Load event database;
with open("enhanced_historical_events.json", "r") as file:
    events = json.load(file)

# Load Falcon model
model_id = "tiiuae/falcon-rw-1b"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

# Set up generation pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Function to find event in database
def find_event(event_name):
    for event in events:
        if event["event_name"].lower() == event_name.lower():
            return event
    return None

# Function to generate a full summary using AI
def generate_summary_with_ai(event_name, max_tokens=200):
    prompt = (
        f"Provide a detailed summary of the historical event '{event_name}', "
        f"including a brief description, important people involved, timeline, factors that led to it, "
        f"and any sub-events that contributed to it."
    )
    response = generator(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=0.7)
    return response[0]["generated_text"].replace(prompt, "").strip()

# Function to generate summary from database or fallback to AI
def get_event_summary(event_name):
    found = find_event(event_name)
    if found:
        summary = f"📘 Event: {found['event_name']}\n\n"
        summary += f"📝 Description: {found['description']}\n\n"
        summary += f"📍 Timeline: {found.get('generated_timeline', 'Unknown')}\n\n"
        summary += f"👥 People Involved: {found.get('generated_people', 'Not available')}\n\n"
        summary += f"🔍 Factors: {found.get('factors', 'Not listed')}\n\n"
        summary += f"🧩 Sub-events: {found.get('sub_events', 'No sub-events listed')}\n"
        return summary
    else:
        return generate_summary_with_ai(event_name)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    event = input("🔍 Enter a historical event: ")
    result = get_event_summary(event)
    print("\n" + "="*40)
    print(result)
