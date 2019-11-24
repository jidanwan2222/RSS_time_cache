from flask import Flask, render_template
import feedparser
import re
from flask_cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

#get source type: jpg, gif, mp4
def post_Type(summary):
    imgType = 'src="(.+?\.jpg)"'
    gifType = 'src="(.+?\.gif)"'
    mp4Type = 'src="(.+?\.mp4)"'
    imgre = re.compile(imgType)
    gifre = re.compile(gifType)
    mp4re = re.compile(mp4Type)
    imglist = re.findall(imgre, summary)
    giflist = re.findall(gifre, summary)
    mp4list = re.findall(mp4re, summary)
    if imglist != []:
        return 'img', imglist[0]
    elif giflist != []:
        return 'gif', giflist[0]
    elif mp4list != []:
        return 'mp4', mp4list[0]
    else:
        return 'other type', 'other type'

#parse the xml
def get_Parse(url):
    rss = feedparser.parse(url)
    data = []
    Ind = 0
    for post in rss.entries:
        postType, postContent = post_Type(post.summary)
        data.append((post.title, post.link, postContent, postType))
        Ind += 1
    return rss['feed']['title'], len(rss['entries']), data


@app.route('/')
def welcome():
    rssList = []
    lenList = []
    for rss_url in xml_url:
        rssList.append(feedparser.parse(rss_url)['feed']['title'])
        lenList.append(len(feedparser.parse(rss_url)['entries']))
    return render_template('welcome.html', Title=rssList, lenList=lenList)



@app.route('/tag<tag_id>/')
@cache.cached(timeout=120, key_prefix='view_%s', unless=None) #update cache every 2 minutes
def returnTag(tag_id):
    tag = 'tag{}'.format(tag_id)
    rss_title, rss_len, rawData = get_Parse(xml_url[int(tag_id)-1])

    context = {
        'tag': tag,
        'rss_title': rss_title,
        'rawData': rawData
    }
    return render_template('tag.html', context=context)

if __name__ == '__main__':
    xml_url = ['https://9gag-rss.com/api/rss/get?code=9GAGComic&format=2',
               'https://9gag-rss.com/api/rss/get?code=9GAGFresh&format=2',
               'https://9gag-rss.com/api/rss/get?code=9GAGFunny&format=2',
               'https://9gag-rss.com/api/rss/get?code=9GAGGIF&format=2']
    app.run(debug=True)