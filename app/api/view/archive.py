from time import strftime, localtime
from flask import jsonify
from .blueprint import api
from app.model.db import Post
from app.utils import generate_res


@api.route('/archive')
def archive_view():
    return jsonify({
        'status': 'success',
        'data': [
            {
                "date": "2019-1",
                "articles": [
                    {
                        "id": 1,
                        "title": "并发编程",
                        "date": "1"
                    },
                    {
                        "id": 2,
                        "title": "搜索引擎查询",
                        "date": "2"
                    },
                    {
                        "id": 4,
                        "title": "dns字典爆破",
                        "date": "3"
                    }
                ]
            },
            {
                "date": "2019-2",
                "articles": [
                    {
                        "id": 5,
                        "title": "sql学习笔记(day1)",
                        "date": "1"
                    },
                    {
                        "id": 6,
                        "title": "记录一些python小窍门",
                        "date": "1"
                    },
                    {
                        "id": 7,
                        "title": "绕过验证码爬取学校cms",
                        "date": "1"
                    }
                ]
            }
        ]})


#
# @api.route('/archive/<int:page>/')
# def archive(page):
#     # per_page 写入config
#     pagination = Post.query.order_by(Post.create_date.desc()).paginate(page=page, per_page=10, error_out=False)
#     posts = pagination.items
#     data = []
#     for post in posts:
#         timestamp = post.create_date / 1000
#         year, month, date = strftime('%Y-%m-%d', localtime(timestamp)).split("-")
#         article = {"id": post.id, "title": post.title, "date": date}
#         if len(data) == 0:
#             data.append({"date": f'{year}-{month}', "articles": [article]})
#             continue
#         for item in data:
#             if item.get('date') == f'{year}-{month}':
#                 item["articles"].append(article)
#             else:
#                 data.append({"date": f'{year}-{month}', "articles": [article]})
#     return generate_res("success", data=data)


"""
    {
        "data": [
            {
                "date": "2019-1",
                "articles": [
                    {
                        "id": 1,
                        "title": "title1",
                        "date": "1"
                    },
                    {
                        "id": 2,
                        "title": "title2",
                        "date": "2"
                    },
                    {
                        "id": 4,
                        "title": "title3",
                        "date": "3"
                    }
                ]
            },
            {
                "date": "2019-2",
                "articles": [
                    {
                        "id": 5,
                        "title": "title5",
                        "date": "1"
                    },
                    {
                        "id": 6,
                        "title": "title6",
                        "date": "1"
                    },
                    {
                        "id": 7,
                        "title": "title7",
                        "date": "1"
                    }
                ]
            }
        ]})
"""
