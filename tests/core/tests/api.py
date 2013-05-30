import os, subprocess
import lxml
import json
import pysam

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from tastypie.exceptions import NotRegistered, BadRequest
from core.models import BedEntry, QTLEntry

from biodas import DAS, DasModelResource, DasResource 


class BedResource(DasModelResource):
    class Meta:
        resource_name = 'bed'
        queryset = BedEntry.objects.all()


class QTLResource(DasModelResource):
    class Meta:
        version = 36 
        resource_name = 'qtl'
        queryset = QTLEntry.objects.all()


class FileBedResource(DasResource):
    """ An example of a BED file used as a resource.  

    NOTE: This is not recommended for use for large bed files.
    """
    filename = os.path.join(os.path.dirname(__file__), 'test.bed')
    class Meta:
        resource_name = 'testbed'
        filename = os.path.join(os.path.dirname(__file__), 'test.bed')



class FileBamResource(DasResource):
    """ An example of a BAM file used as a resource
    """
    class Meta:
        resource_name = 'testbam'
        filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                'fixtures/AKR_brain_test.bam')


class FileBamJsonResource(DasResource):
    """ An example of a BAM file used as a resource
    """
    class Meta:
        resource_name = 'testjsonbam'
        json = True
        filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                'fixtures/AKR_brain_test.bam')


class ApiTestCase(TestCase):
    urls = 'core.tests.api_urls'

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

        # Check queries
        resp = self.client.get('/api/das/sources?version=36')
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)

        #resp = self.client.get('/api/das/sources?version=36?capabilit=1.5')

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


class DasFileSourcesTest(TestCase):
    def setUp(self):
        self.fh = pysam.Samfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                'fixtures/AKR_brain_test.bam'))

    def test_resource_top_level(self):
        """ Test the top level response for a file resource
        """
        resp = self.client.get('/api/das/testbed/')
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)
        # Add more checks to this

        # BAM file check
        resp = self.client.get('/api/das/testbam/')
        root = lxml.etree.fromstring(resp.content)
        self.assertEqual(len(root), 1)


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

    
    def test_bam_feature_queries(self):
        """ Test BAM feature queries
        """
        resp =\
                self.client.get(
                        '/api/das/testbam/features?segment=chr7:3299628,3300000')
        segments = lxml.etree.fromstring(resp.content)[0][0]
        counter = 0
        reads = self.fh.fetch('chr7', 3299628, 3300000)
        for i in reads:
            counter += 1
        self.assertEqual(len(segments), counter)
        
        

    def test_json_feature_queries(self):
        """ Test json feature queries
        """
        
        resp =\
                self.client.get(
                        '/api/das/testjsonbam/features?segment=chr7:3299628,3300000')
        self.assertEqual(len(json.loads(resp.content)), 3)



