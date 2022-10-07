from parsers.base import parse_site
from parsers.parsers import ConsultantRuParser
import requests
# debug tool
if __name__ == '__main__':
    resp = None
    news = parse_site(ConsultantRuParser, resp)
    with open('result.out', 'w') as f:
        print(news, file=f)
