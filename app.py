from flask import Flask, render_template, jsonify, request
import requests
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# ----------------------------
# Tech News (RSS)
# ----------------------------
TECH_NEWS_RSS = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"

def fetch_tech_news():
    try:
        resp = requests.get(TECH_NEWS_RSS)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        news_list = []
        for item in root.findall(".//item")[:10]:
            news_list.append({
                'title': item.find('title').text,
                'summary': item.find('description').text,
                'url': item.find('link').text
            })
        return news_list
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ----------------------------
# Tech Jobs (Jobicy API)
# ----------------------------
JOBS_API = "https://jobicy.com/api/v2/remote-jobs?count=20"

def fetch_tech_jobs():
    try:
        response = requests.get(JOBS_API)
        response.raise_for_status()
        data = response.json()
        jobs_raw = data.get('jobs', [])
        jobs_list = []
        for job in jobs_raw[:10]:
            title    = job.get('jobTitle')
            url      = job.get('url')
            company  = job.get('companyName', 'Unknown Company')
            location = job.get('jobGeo', 'Remote')
            if title and url:
                jobs_list.append({
                    'title':    title,
                    'company':  company,
                    'location': location,
                    'url':      url
                })
        return jobs_list
    except Exception as e:
        print(f"Error fetching tech jobs: {e}")
        return []

# ----------------------------
# Likes store (in-memory)
# ----------------------------
likes_count = {}  # {url: total_likes}

@app.route('/')
def index():
    news = fetch_tech_news()
    jobs = fetch_tech_jobs()

    for item in news:
        item['likes'] = likes_count.get(item['url'], 0)
    for job in jobs:
        job['likes'] = likes_count.get(job['url'], 0)

    return render_template('index.html', news=news, jobs=jobs)

@app.route('/like-toggle', methods=['POST'])
def like_toggle():
    data = request.get_json()
    url = data.get('url')
    action = data.get('action')  # 'like' or 'unlike'

    if url and action in ['like', 'unlike']:
        if action == 'like':
            likes_count[url] = likes_count.get(url, 0) + 1
        else:
            likes_count[url] = max(likes_count.get(url, 0) - 1, 0)
        return jsonify({'success': True, 'likes': likes_count[url]})
    return jsonify({'success': False}), 400

# 🔹 Render requires host=0.0.0.0 and port from env
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
