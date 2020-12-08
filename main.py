from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


def init_chatbot():
    chatbot = ChatBot(
        name="GuardianBot",
        logic_adapters=[
            {
                'import_path': 'guardian_adapter.GuardianAdapter',
                'statement_comparison_function': 'chatterbot.comparisons.jaccard_similarity',
                'default_response': "I don't know what you mean."
            },
        ]
    )
    trainer = ChatterBotCorpusTrainer(chatbot)

    chatbot.storage.drop()
    trainer.train("data.english")
    return chatbot


if __name__ == '__main__':
    chatbot = init_chatbot()

    while (True):
        line = input("Say something: ")
        response = chatbot.get_response(line)
        print(response)
