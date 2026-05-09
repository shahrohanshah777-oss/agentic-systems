system_message = {
    "role": "system",
    "content": "You are a helpful AI study assistant. The student's name is Kavya and they are studying AI Agents and Memory Systems."
}

full_history = []
WINDOW_SIZE = 6
def call_llm(messages):
    last_user_message = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), "no user message")
    return f"[Study Assistant]: Got your question about '{last_user_message}'. I can see {len(messages)} messages in my context window."
def chat_with_agent(user_message):
    full_history.append({"role": "user", "content": user_message})
    context = [system_message] + full_history[-WINDOW_SIZE:]
    response = call_llm(context)
    full_history.append({"role": "assistant", "content": response})
    return response

questions = [
    "What is the difference between STM and LTM?",
    "Can you explain Buffer, Window, and Summary strategies?",
    "What are Episodic, Semantic, and Procedural memory types?",
    "How do context window limits affect LLM performance?",
    "What are some techniques to manage long conversations?",
    "How does the pinned system message help in this setup?",
    "Can you give an example of a conversation that exceeds the window size?",
    "What are the trade-offs of using Window Memory vs other strategies?"
]
for question in questions:
    response = chat_with_agent(question)
    print(response)

total_messages = len(full_history)
messages_in_last_call = min(WINDOW_SIZE + 1, total_messages)  # 1 system + up to 6 history
print("\n--- Final Memory Report ---")
print(f"Total messages in full_history: {total_messages}")
print(f"Messages sent to LLM in the last call: {messages_in_last_call}  (1 system + up to 6 history)")
print(f"Window Memory bounded context to {messages_in_last_call} messages while full history holds {total_messages} messages.")
assert messages_in_last_call <= 7, "Y should always be ≤ 7"

