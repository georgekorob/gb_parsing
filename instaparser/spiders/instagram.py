import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_username = 'Onliskill_udm'
    inst_enc_password = '#PWD_INSTAGRAM_BROWSER:10:1634627237:AalQADvB0Xcv5lreXHUZ5tFNCTrp1nB0tbeNHdWGC9PxRNwxCJQwetftChdIyYNiHF5cq7/W050nfOkYDmyQThaavyIAnv1zMvEgkdKmmvXo9Ck4A7t8VISYnI+y4ce/pxgKQcssw5925oDcNUPg'  # Qw123456789
    users_for_parse = ['circlecodesolution', 'the_vahid_ansari_', 'vbandari', 'jay_r_deore']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    followers_link = 'https://i.instagram.com/api/v1/friendships/{}/followers/'
    following_link = 'https://i.instagram.com/api/v1/friendships/{}/following/'
    user_info_link = 'https://i.instagram.com/api/v1/users/{}/info/'
    api_headers = {'user-agent': 'Instagram 155.0.0.37.107'}

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_username,
                                           'enc_password': self.inst_enc_password},
                                 headers={'x-csrftoken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user_p in self.users_for_parse[:2]:
                yield response.follow(f'/{user_p}',
                                      callback=self.parent_user_follows,
                                      cb_kwargs={'username': user_p})

    def parent_user_follows(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        yield response.follow(self.followers_link.format(user_id),
                              callback=self.parse_followers,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': {'count': 12, 'search_surface': 'follow_list_page'}},
                              headers=self.api_headers)
        yield response.follow(self.following_link.format(user_id),
                              callback=self.parse_following,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': {'count': 12}},
                              headers=self.api_headers)
        yield response.follow(self.user_info_link.format(user_id),
                              callback=self.parse_user,
                              cb_kwargs={'parent_user_id': None, 'type_user': 'parents'},
                              headers=self.api_headers)

    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        variables['max_id'] = j_data.get('next_max_id')
        if variables['max_id']:
            yield response.follow(self.followers_link.format(user_id),
                                  callback=self.parse_followers,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers=self.api_headers)
        for user in j_data.get('users')[:2]:
            yield response.follow(self.user_info_link.format(user.get('pk')),
                                  callback=self.parse_user,
                                  cb_kwargs={'parent_user_id': user_id, 'type_user': 'followers'},
                                  headers=self.api_headers)

    def parse_following(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        variables['max_id'] = j_data.get('next_max_id')
        if variables['max_id']:
            yield response.follow(self.following_link.format(user_id),
                                  callback=self.parse_following,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers=self.api_headers)
        for user in j_data.get('users')[:2]:
            yield response.follow(self.user_info_link.format(user.get('pk')),
                                  callback=self.parse_user,
                                  cb_kwargs={'parent_user_id': user_id, 'type_user': 'following'},
                                  headers=self.api_headers)

    def parse_user(self, response: HtmlResponse, parent_user_id, type_user):
        user = response.json().get('user')
        item = InstaparserItem(user_id=user.get('pk'),
                               username=user.get('username'),
                               full_name=user.get('full_name'),
                               profile_pic_url=user.get('hd_profile_pic_url_info').get('url'),
                               follower_count=user.get('follower_count'),
                               following_count=user.get('following_count'),
                               public_email=user.get('public_email'),
                               parent=parent_user_id,
                               type=type_user)
        yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            _ids = re.findall('\"id\":\"\\d+\"', text)
            _username = re.search('\"username\":\"%s\"' % username, text).group()
            index_un = text.index(_username)
            arr_to_sort = [[x, abs(index_un - text.index(x))] for x in _ids]
            return sorted(arr_to_sort, key=lambda x: x[1])[0][0].split('\":\"')[1][:-1]
        except Exception as e:
            print(e)
