from app.services.hello_service import get_hello_message

class HelloController:
    @staticmethod
    def root():
        return get_hello_message()

    @staticmethod
    def health():
        return {"status": "ok"}
