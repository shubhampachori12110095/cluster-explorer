from django.test import TestCase
from django.test.client import RequestFactory
from views import _get_step, _get_cluster, _get_doc

class ViewTest(TestCase):
    def setUp(self):
        request = RequestFactory()
    
    def test_get_step(self):
        response = _get_step()
        self.assertNotEqual(response['step'], False)
    
    def test_get_cluster(self):
        response = _get_cluster(0,0)
        self.assertNotEqual(response['cluster'], False)
    
    def test_get_doc(self):
        response = _get_cluster(0,0)
        self.assertNotEqual(response['doc'], False)