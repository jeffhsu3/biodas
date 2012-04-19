import lxml

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from tastypie.exceptions import NotRegistered, BadRequest
from core.models import BedEntry, QTLEntry
from tastypie.resources import Resource, ModelResource

from biodas import DAS, DASModelResource

class BedResource(DASModelResource):
    class Meta:
        resource_name = 'bed'
        queryset = BedEntry.objects.all()


class QTLResource(DASModelResource):
    DAS_VERSION = 1.5
    class Meta:
        das_version = 1.5
        resource_name = 'qtl'
        queryset = QTLEntry.objects.all()

class ApiTestCase(TestCase):
    urls = 'core.tests.api_urls'
    #fixtures = ['QTL_testdata.json']

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
        #print(resp.content)


class ApiCalls(TestCase):
    """ Test actual get responses
    """
    urls = 'core.tests.api_urls'
    #fixtures = ['testdata.json']

    def setUp(self):
        self.qtl = QTLEntry(chrom = 1, start = 2000, end = 2600,
                                 gene="Testgene", strand = True)
        self.bed = BedEntry(chrom = 1, start = 2000, end = 2600,
                                 gene="Testgene", strand = True)
        self.qtl.save()
        self.bed.save()

    def test_top_level(self):
        """ Test top level discovery query
        """
        resp = self.client.get('/api/das/sources/')
        self.assertEqual(resp.status_code, 200)
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(root.tag, 'SOURCES')
        self.assertEqual(len(root), 2)

        # Check queries
        resp = self.client.get('/api/das/sources?version=1.6')
        #print(resp)
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)


    def test_resource_queries(self):
        """
        """
        resp = self.client.get('/api/das/bed/')
        #print(resp)
        resp = self.client.get('/api/das/qtl/')
        #print(resp)




