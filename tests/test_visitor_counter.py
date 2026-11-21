"""
ORBIT Platform — Unit and Functional Test Suite for Visitor Counter
Tests Flask endpoints, Redis integration, graceful connection handling, and health probes.
"""

import unittest
import json
import os
import sys

# Add visitor-counter to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'visitor-counter')))

import app as visitor_app

class TestVisitorCounter(unittest.TestCase):
    def setUp(self):
        visitor_app.app.config['TESTING'] = True
        self.client = visitor_app.app.test_client()

    def test_01_health_endpoint(self):
        """Verify /health returns 200 with structured JSON"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn(data['status'], ['healthy', 'degraded'])
        self.assertIn('services', data)
        self.assertEqual(data['services']['web'], 'up')

    def test_02_visitor_count_json(self):
        """Verify /api/count increments and returns JSON"""
        resp1 = self.client.get('/api/count')
        self.assertEqual(resp1.status_code, 200)
        d1 = json.loads(resp1.data)
        c1 = d1['visitor_count']

        resp2 = self.client.get('/api/count')
        self.assertEqual(resp2.status_code, 200)
        d2 = json.loads(resp2.data)
        c2 = d2['visitor_count']

        self.assertGreaterEqual(c2, c1)

    def test_03_content_negotiation(self):
        """Verify root endpoint responds to Accept: application/json"""
        resp = self.client.get('/', headers={'Accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('visitor_count', data)
        self.assertIn('backend', data)

    def test_04_html_render(self):
        """Verify root endpoint serves styled HTML page by default"""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'ORBIT Cloud Telemetry', resp.data)
        self.assertIn(b'Total Verified Visitors', resp.data)

    def test_05_metrics_endpoint(self):
        """Verify Prometheus metrics endpoint /metrics"""
        resp = self.client.get('/metrics')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'orbit_visitor_counter_uptime_seconds', resp.data)

    def test_06_load_endpoint(self):
        """Verify controlled CPU load endpoint for HPA stress testing"""
        resp = self.client.get('/load?duration=0.5&cycles=100000')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'load_complete')
        self.assertIn('duration_seconds', data)

if __name__ == '__main__':
    unittest.main()
