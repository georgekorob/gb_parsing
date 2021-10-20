import pymongo
from pprint import pprint


if __name__ == "__main__":
    users = pymongo.MongoClient('localhost', 27017).instabase.users
    user_id = '45042324274'
    len_view = 10
    for type in ['followers','following']:
        for user in users.find(
                {'$and':
                    [
                        {'type': type},
                        {'parent': user_id}
                    ]
                })[:len_view]:
            pprint(user)
