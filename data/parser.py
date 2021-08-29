from data import db_session
from data.news import News
from requests import get
from bs4 import BeautifulSoup


# парсер новостей
def parser(university_id):
    # получаем данные для парсера из БД
    parser_session = db_session.create_session()
    news = parser_session.query(News).get(university_id)

    try:
        # обращаемся к сайту, получаем данные, раскидываем по массивам и возвращаем всё
        r = get(news.url)
        soup = BeautifulSoup(r.text, 'html.parser')

        titles = []
        links = []
        texts = []
        dates = []
        images = []

        for block in soup.find_all(news.block.split()[0], class_=news.block.split()[1])[:5]:

            link = block.find(news.title.split()[0], class_=news.title.split()[1])
            titles.append(link.text.strip())

            if news.news_url.split()[0] == 'a':
                link = block.find(news.news_url.split()[0], class_=news.news_url.split()[1], href=True)
                link2 = link['href']
                if link2[0] != '/':
                    link2 = f'/{link2}'
                links.append(link2)
            else:
                link = block.find(news.news_url.split()[0], class_=news.news_url.split()[1])
                link2 = link.find('a', href=True)['href']
                if link2[0] != '/':
                    link2 = f'/{link2}'
                links.append(link2)

            if len(news.image.split()) == 3:
                link = block.find(news.image.split()[0], class_=news.image.split()[1], style=True)
                link2 = link['style'].split("url('")[1][:-2]
                images.append(link2)
            else:
                link = block.find(news.image.split()[0], class_=news.image.split()[1])
                link2 = link.find('img', src=True)['src']
                images.append(link2)

            link = block.find(news.date.split()[0], class_=news.date.split()[1])
            dates.append(' '.join(link.text.strip().split()))

            if news.text != '':
                link = block.find(news.text.split()[0], class_=news.text.split()[1])
                texts.append(link.text.strip())

        url = news.url.split('/')[:3]

        news_li = []

        if not texts:
            for i in range(5):
                dict1 = {'url': f"{url[0]}//{url[2]}", 'link': links[i], 'title': titles[i], 'image': images[i],
                         'text': '', 'date': dates[i]}
                news_li.append(dict1)
        else:
            for i in range(5):
                dict1 = {'url': f"{url[0]}//{url[2]}", 'link': links[i], 'title': titles[i], 'image': images[i],
                         'text': texts[i], 'date': dates[i]}
                news_li.append(dict1)

        return news_li

    # в случае возникновения неполадок, отправляем пустой массив
    except Exception:
        return []
