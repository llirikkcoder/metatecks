# from urlparse import urlparse, parse_qs


# def get_youtube_video_id(link):
#     query = urlparse(link)
#     video_id = 0
#     try:
#         if query.hostname == 'youtu.be':
#             video_id = query.path[1:]
#         if query.hostname in ('www.youtube.com', 'youtube.com'):
#             if query.path == '/watch':
#                 p = parse_qs(query.query)
#                 video_id = p['v'][0]
#             if query.path[:7] == '/embed/':
#                 video_id = query.path.split('/')[2]
#             if query.path[:3] == '/v/':
#                 video_id = query.path.split('/')[2]
#     except Exception as e:
#         pass
#     return video_id


# class MediaVideoAdminForm
