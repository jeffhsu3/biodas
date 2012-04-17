from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from biodas import DAS
from tastypie.exceptions import NotRegistered, BadRequest
from core.models import BedEntry, QTLEntry
from tastypie.resources import Resource, ModelResource



class BedResource(ModelResource):
    class Meta:
        resource_name = 'bed'
        queryset = BedEntry.objects.all()


class QTLResource(ModelResource):
    class Meta:
        resource_name = 'qtl'
        queryset = QTLEntry.objects.all()

class ApiTestCase(TestCase):
    urls = 'core.tests.api_urls'
    fixtures = ['QTL_testdata.json']

    def test_register(self):
        api = DAS()
        self.assertEqual(len(api._registry), 0)

        api.register(BedResource())
        self.assertEqual(len(api._registry), 1)

        api.register(QTLResource())
        self.assertEqual(len(api._registry), 2)

    def test_top_level(self):
        api = DAS()
        api.register(BedResource())
        api.register(QTLResource())

        request = HttpRequest()

        resp = api.top_level(request)
        self.assertEqual(resp.status_code, 200)
        print(resp.content)


class ApiCalls(TestCase):
    """ Test actual get responses
    """
    urls = 'core.tests.api_urls'
    fixtures = ['QTL_testdata.json']

    def test_top_level(self):
        """ Test top level discovery query
        """
        resp = self.client.get('/api/das/')
        print(resp)



