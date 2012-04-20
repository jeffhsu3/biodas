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
    version = 36 
    class Meta:
        resource_name = 'qtl'
        queryset = QTLEntry.objects.all()

class ApiTestCase(TestCase):
    urls = 'core.tests.api_urls'
    #fixtures = ['QTL_testdata.json']

    def test_register(self):
        """ Test basic registration of sources with the DAS server
        """
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

        # Testing Response Headers
        self.assertEqual(resp['X-DAS-Version'], 'DAS/1.6')


class ApiCalls(TestCase):
    """ Test actual get responses
    """
    urls = 'core.tests.api_urls'
    #fixtures = ['testdata.json']
    # Fixtures aren't working

    def setUp(self):
        self.qtl = QTLEntry(chrom = 1, start = 27000, end = 29000,
                                 gene="outside_interval", strand = True)
        self.qtl.save()
        self.qtl = QTLEntry(chrom = 1, start = 2000, end = 2600,
                                 gene="within_interval", strand = True)
        self.qtl.save()
        self.qtl = QTLEntry(chrom = 2, start = 2000, end = 2600,
                                 gene="chr2_test", strand = True)
        self.qtl.save()
        self.bed = BedEntry(chrom = 1, start = 2000, end = 2600,
                                 gene="Testgene", strand = True)
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
        resp = self.client.get('/api/das/sources?version=36')
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)

    def test_resource_top_level(self):
        """ Test the top level for the resources
        """
        resp = self.client.get('/api/das/bed/')
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)
        resp = self.client.get('/api/das/qtl/')
        self.assertEqual(len(root), 1)


    def test_resource_queries(self):
        """ Test segment queries on the resources
        """
        resp = self.client.get('/api/das/qtl/features?segment=1:100,20000')
        dasgff = lxml.etree.fromstring(resp.content)
        self.assertEqual(dasgff[0][0][0].get('label'), 'within_interval')


    def test_whole_segment_query(self):
        """ Test that a whole segment query returns the whole segment
        :TODO need to handle throttling
        """
        resp = self.client.get('/api/das/qtl/features?segment=1')
        segment = lxml.etree.fromstring(resp.content)[0][0]
        self.assertEqual(len(segment), 2)
        print(resp.content)


class DASFileSourcesTest(TestCase):
    def setUp(self):
        pass

    def test_registration(self):
        pass


