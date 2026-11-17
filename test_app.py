"""
Comprehensive Unit & Integration Test Suite for Rent Finder Pakistan
Tests all endpoints, database queries, authentication, AI chatbot, and templates.
"""

import unittest
import json
from app import app
import database as db
import ai_service

class TestRentFinderPakistan(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'RentFinder', response.data)
        self.assertIn(b'FIND YOUR', response.data)
        self.assertIn(b'PERFECT RENTAL HOME', response.data)
        print("✓ Homepage test passed")

    def test_02_property_search(self):
        # Search Karachi flats
        response = self.client.get('/properties?city=Karachi&type=Flat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Clifton', response.data)
        print("✓ Property search filter test passed")

    def test_03_property_details(self):
        response = self.client.get('/properties/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Clifton', response.data)
        self.assertIn(b'Monthly Rent', response.data)
        self.assertIn(b'Book a Viewing Appointment', response.data)
        print("✓ Property details page test passed")

    def test_04_compare_properties(self):
        response = self.client.get('/compare?ids=1,2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Compare Rental Properties', response.data)
        self.assertIn(b'Monthly Rent', response.data)
        print("✓ Compare properties test passed")

    def test_05_pricing_monetization(self):
        response = self.client.get('/pricing')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Silver Landlord', response.data)
        self.assertIn(b'Easypaisa', response.data)
        self.assertIn(b'JazzCash', response.data)
        print("✓ Pricing & Monetization test passed")

    def test_06_ai_chatbot_property_search(self):
        # Test property assistant capability
        payload = {'message': 'Show me flats in Karachi', 'sessionId': 'test_session_1'}
        response = self.client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['properties']), 0)
        print(f"✓ AI Chatbot Property Assistant test passed (Matched {len(data['properties'])} properties)")

    def test_07_ai_chatbot_global_assistant(self):
        # Test general ChatGPT capability
        payload = {'message': 'Explain how rent agreements work under Pakistani law', 'sessionId': 'test_session_2'}
        response = self.client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('Rent', data['response'])
        print("✓ AI Chatbot Global Knowledge test passed")

    def test_08_admin_auth_protection(self):
        # Unauthorized access to /admin should redirect to home/login
        response = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        print("✓ Admin authorization guard test passed")

    def test_09_admin_login_and_access(self):
        # Login with demo admin
        login_resp = self.client.post('/login', data={'email': 'admin@rentfinder.pk', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Command Center', login_resp.data)

        # Access admin properties
        admin_props = self.client.get('/admin/properties')
        self.assertEqual(admin_props.status_code, 200)
        self.assertIn(b'All Property Listings', admin_props.data)
        print("✓ Admin login and dashboard operations test passed")

if __name__ == '__main__':
    unittest.main()
