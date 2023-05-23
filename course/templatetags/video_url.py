import re
from django import template

register = template.Library()


@register.filter(name="embed_youtube_video")
def embed_youtube_video(url):
    video_id = re.findall(r"v=(\w+)", url)
    return f"https://www.youtube.com/embed/{video_id[0]}"
