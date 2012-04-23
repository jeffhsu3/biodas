import os
import lxml

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from tastypie.exceptions import NotRegistered, BadRequest
from core.models import BedEntry, QTLEntry

from biodas import DAS, DASModelResource, DASResource 

class BedResource(DASModelResource):
    class Meta:
        resource_name = 'bed'
        queryset = BedEntry.objects.all()


class QTLResource(DASModelResource):
    class Meta:
        version = 36 
        resource_name = 'qtl'
        queryset = QTLEntry.objects.all()


class FileBedResource(DASResource):
    """
    """
    filename = os.path.join(os.path.dirname(__file__), 'test.bed')
    class Meta:
        resource_name = 'testbed'
        filename = os.path.join(os.path.dirname(__file__), 'test.bed')


class BamResource(DASResource):
    """
    """
    pass


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


class DasModelCalls(TestCase):
    """ Test actual get responses
    """
    urls = 'core.tests.api_urls'
    #fixtures = ['testdata.json']
    # Fixtures aren't working

    def setUp(self):
        self.qtl = QTLEntry(chrom = 1, start = 27000, end = 29000,
                                 gene="outside_interval", strand = True,
                                 score = 20)
        self.qtl.save()
        self.qtl = QTLEntry(chrom = 1, start = 2000, end = 2600,
                                 gene="within_interval", strand = True,
                                 score = 50)
        self.qtl.save()
        self.qtl = QTLEntry(chrom = 2, start = 2000, end = 2600,
                                 gene="chr2_test", strand = True,
                                 score = 60)
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
        self.assertEqual(len(root), 3)

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
        segments = lxml.etree.fromstring(resp.content)[0][0]
        self.assertEqual(len(segments), 2)

        resp = self.client.get('/api/das/bed/features?segment=1')
        segments = lxml.etree.fromstring(resp.content)[0][0]
        self.assertEqual(len(segments), 1)


class DASFileSourcesTest(TestCase):
    def setUp(self):
        pass

    def test_resource_top_level(self):
        """
        """
        resp = self.client.get('/api/das/testbed/')
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)
        # Add more checks to this


    def test_feature_queries(self):
        """ Test region:start, end query on various file sources.
        """
        
        resp = self.client.get('/api/das/testbed/features?segment=chr1:60,200')
        segments = lxml.etree.fromstring(resp.content)[0][0]
        self.assertEqual(len(segments), 2)

    def test_whole_segment_query(self):
        """ Test that a whole segment query returns the whole segment
        """
        resp = self.client.get('/api/das/testbed/features?segment=chr1')
        segments = lxml.etree.fromstring(resp.content)[0][0]
        self.assertEqual(len(segments), 3)



