from app.utils import generate_res
from .blueprint import api
from app.model.view import QueryView
from app.model.db import Post
from app.model.baseDB import Visibility
from app.app_frontend.view_model import PostsView
from app.app_frontend.cache import cache


@api.route('/posts')
def posts_view():
    # print(f"\033[1;31m {cache.get('/view//api/posts')}\033[0m")
    query = QueryView(order_by=False)
    tid = query.filters.get('tid')
    visibility = Visibility.public.value
    posts = Post.paging_by_tid(
        tid, **query.search_parameter, visibility=visibility
    ) if tid else Post.paging_search(**query.search_parameter, visibility=visibility)
    return generate_res(data=PostsView(posts.items, query.page))
