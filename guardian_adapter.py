from chatterbot.conversation import Statement
from chatterbot.logic import LogicAdapter, BestMatch
from multiprocessing import Process
from news_task import NewsTask
from theguardian import theguardian_content
import re


class MyLogicAdapter(BestMatch):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.categories = {
            'sport': 'sports article',
            'culture': 'culture article',
            'news': 'latest news',
            'environment': 'article on environment',
            'music': 'music article',
            'science': 'science article'
        }
        self.editions = ['us', 'uk', 'au', 'default']
        self.key_words = ['turn off', 'search', 'change', 'edition', 'cyclic']
        self.key_words += self.categories.keys()
        self.edition = 'us'
        self.news_task = NewsTask(chatbot=chatbot, active_edition=self.edition, active_category="")
        self.news_thread = None

    def find_article_keyword(self, keyword):
        # create content
        headers = {"q": keyword}
        content = theguardian_content.Content(api='68427e29-0cd0-4ba4-a7c9-92350224c80f', **headers)

        # get all results of a page
        json_content = content.get_content_response()
        results = content.get_results(json_content)

        return self.news_task.get_article_title(results[0]['apiUrl']), results[0]['webUrl']

    def can_process(self, statement):
        return True

    def process(self, input_statement, additional_response_selection_parameters=None):
        text = input_statement.text
        statement = Statement(text="")
        statement.confidence = 1
        if 'change' in text and 'edition' in text:
            last_word = str(text).split(" ")[-1]
            if last_word in self.editions:
                self.edition = last_word  # if the given edition is wrong, it will always default
                statement.text = f'Your new edition is {self.edition}'
                return statement
            else:
                statement.text = f'Try choosing an edition from {self.editions}'
                return statement

        if 'cyclic' in text:
            for category in self.categories.keys():
                if category in text:
                    self.news_task.active_category = category
                    self.news_thread = Process(target=self.news_task.news_bot)
                    self.news_thread.start()
                    statement.text = f'Cyclic {category} news feed turned on'
                    return statement

        if self.news_thread and 'turn off' in text:
            self.news_thread.terminate()
            statement.text = f'Cyclic news feed turned off'
            return statement

        if 'search' in text:
            regex = re.compile('search(?:\sfor)?\s([\w\s]+)$', re.IGNORECASE)
            search_terms = regex.search(text).group(1)
            title, link = self.find_article_keyword(search_terms)
            statement.text = f'Here is an article about {search_terms}. Title: {title}. Link: {link}'
            return statement

        title = None
        link = None

        statement = BestMatch.process(self, input_statement=input_statement)
        for category, val in self.categories.items():
            if val in statement.text:
                title, link = self.news_task.get_article(category)

        if link is not None:
            statement.text += f' Title: {title}. Link: {link}'

        return statement
