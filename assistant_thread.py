import uuid

class AssistantThread:
    def __init__(self):
        self.thread_id = str(uuid.uuid4())
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful and friendly assistant for a resort booking system. "
                    "When responding to users, always format your responses in a clear, human-readable way with:\n"
                    "- Use emojis and formatting to make responses visually appealing\n"
                    "- Structure information with bullet points, numbered lists, or sections\n"
                    "- Use bold text (**text**) for important information like resort names, dates, prices\n"
                    "- Present booking information in an organized, easy-to-read format\n"
                    "- Be conversational and helpful in your tone\n"
                    "- When showing multiple items, use clear numbering or bullet points\n"
                    "- Include relevant details but keep responses concise and scannable\n"
                    "Use the available functions to fetch real-time data from the database and always "
                    "present the information in a beautiful, formatted way that's easy for humans to read."
                )
            }
        ]

    def add_user_message(self, user_message: str):
        self.messages.append({"role": "user", "content": user_message})

    def add_assistant_message(self, assistant_message: dict):
        self.messages.append(assistant_message)

    def get_history(self):
        return self.messages