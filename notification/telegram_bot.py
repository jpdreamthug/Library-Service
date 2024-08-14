import requests


class TelegramBot:
    def __init__(self, token):
        self.token = token

    def send_message_to_chat(self, chat_id: str, message: str):
        return requests.post(
            url=f"https://api.telegram.org/bot{self.token}/sendMessage",
            data={"chat_id": chat_id, "text": message},
        )
