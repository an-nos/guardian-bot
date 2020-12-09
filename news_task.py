from theguardian import theguardian_section, theguardian_content
import time


def get_article_title(apiUrl):
    content = theguardian_content.Content(api='test', url=apiUrl).get_content_response()
    response = content['response']
    return response['content']['webTitle']


class NewsTask:
    def __init__(self, chatbot, active_category, active_edition):
        self.chatbot = chatbot
        self.active_category = active_category
        self.active_edition = active_edition
        self.newest_title, self.newest_url = None, None

    def get_article_title(self, apiUrl):
        content = theguardian_content.Content(api='test', url=apiUrl).get_content_response()
        response = content['response']
        return response['content']['webTitle']

    def get_article(self, category):
        self.active_category = category
        return self.get_current_news()

    def get_current_news(self):
        headers = {"q": self.active_category}  # q=query parameter/search parameter
        section = theguardian_section.Section(api='test', **headers)

        section_content = section.get_content_response()
        results = section.get_results(section_content)

        editions = results[0]['editions']
        articles = [edi["apiUrl"] for edi in editions if
                    self.active_category in edi['id'] and self.active_edition == edi['code']]

        if not articles:
            articles = editions[0]["apiUrl"]  # there was only a default edition or categories weren't found
        else:
            articles = articles[0]

        content = theguardian_content.Content(api='test', url=articles)

        content_response = content.get_content_response()
        results = content_response['response']['results']
        newest_result = results[0]
        title = get_article_title(newest_result['apiUrl'])
        return title, newest_result['webUrl']

    def news_bot(self):
        while True:
            new_title, new_url = self.get_current_news()
            if new_url != self.newest_url:
                self.newest_url = new_url
                self.newest_title = new_title
            print(f'{self.chatbot.get_response(self.active_category)}')
            time.sleep(10)

