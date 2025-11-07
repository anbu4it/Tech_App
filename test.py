import unittest
from unittest.mock import patch, MagicMock
import json
from app import app, likes_count

class TechDashboardTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True

        # Clear likes before each test
        likes_count.clear()

    # ----------------------------
    # Test index route
    # ----------------------------
    @patch('app.fetch_tech_news')
    @patch('app.fetch_tech_jobs')
    def test_index_route(self, mock_jobs, mock_news):
        # Mock data
        mock_news.return_value = [{'title':'News1','summary':'Summary1','url':'url1'}]
        mock_jobs.return_value = [{'title':'Job1','company':'Comp1','location':'Remote','url':'job1'}]

        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'News1', response.data)
        self.assertIn(b'Job1', response.data)

    # ----------------------------
    # Test like toggle: like action
    # ----------------------------
    def test_like_toggle_like(self):
        payload = {'url':'test-url','action':'like'}
        response = self.app.post('/like-toggle', data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['likes'], 1)
        self.assertEqual(likes_count['test-url'], 1)

    # ----------------------------
    # Test like toggle: unlike action
    # ----------------------------
    def test_like_toggle_unlike(self):
        # Pre-like first
        likes_count['test-url'] = 2

        payload = {'url':'test-url','action':'unlike'}
        response = self.app.post('/like-toggle', data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['likes'], 1)
        self.assertEqual(likes_count['test-url'], 1)

    # ----------------------------
    # Test like toggle: invalid request
    # ----------------------------
    def test_like_toggle_invalid(self):
        payload = {'url':'', 'action':'invalid'}
        response = self.app.post('/like-toggle', data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    # ----------------------------
    # Test fetch_tech_news function with mock requests
    # ----------------------------
    @patch('app.requests.get')
    def test_fetch_tech_news(self, mock_get):
        # Fake RSS XML
        fake_rss = '''<?xml version="1.0"?>
        <rss><channel>
            <item><title>Title1</title><description>Desc1</description><link>Link1</link></item>
            <item><title>Title2</title><description>Desc2</description><link>Link2</link></item>
        </channel></rss>'''
        mock_resp = MagicMock()
        mock_resp.content = fake_rss.encode('utf-8')
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        from app import fetch_tech_news
        news = fetch_tech_news()
        self.assertEqual(len(news), 2)
        self.assertEqual(news[0]['title'], 'Title1')
        self.assertEqual(news[1]['summary'], 'Desc2')

    # ----------------------------
    # Test fetch_tech_jobs function with mock requests
    # ----------------------------
    @patch('app.requests.get')
    def test_fetch_tech_jobs(self, mock_get):
        fake_jobs = {'jobs': [
            {'jobTitle':'Dev','url':'url1','companyName':'Comp1','jobGeo':'Remote'},
            {'jobTitle':'Tester','url':'url2','companyName':'Comp2','jobGeo':'NY'}
        ]}
        mock_resp = MagicMock()
        mock_resp.json.return_value = fake_jobs
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        from app import fetch_tech_jobs
        jobs = fetch_tech_jobs()
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['title'], 'Dev')
        self.assertEqual(jobs[1]['location'], 'NY')

if __name__ == '__main__':
    unittest.main()
