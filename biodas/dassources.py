""" Contains resources that bind django ORMs or to file resources
"""
from itertools import izip

from django.conf.urls.defaults import url
#from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.http import HttpResponse
from django.db.models import Q
from tastypie.resources import Resource, ModelResource

from utils import parse_das_segment, add_das_headers
import serializers 
from serializers import feature_serializer


class DASBaseResource(Resource):
    """ A Base Class for DAS resources.  Use DASModelResource or
    DASFileResource.
    """

    capability = "feature"
    chr_tyep = "Chromosome"
    authority = "GRCh"
    version = 37

class DASModelResource(ModelResource):
    """  For resources that are already from the django ORM.

    Requires there to be a chrom, start, end at the very least.
    This should probably inherit from a generic DASResources class.
    """
    # :TODO Need to check that the django model has some required fields
    # upon initialization
    # Need to somehow place this in the meta information easily
    capability = "features"
    chr_type = "Chromosome"
    authority = "GRCh"
    version = 37
    organism = "homo sapiens"
    # label = source_name

    class Meta:
        # Why isn't this working?
        default_format = 'application/xml'


    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/features" %
                (self._meta.resource_name), self.wrap_view('get_features'),
                name = 'api_get_features'),
        ]

    # Views

    def get_list(self, request, **kwargs):
        """ Replaces the standard resource response with the sources one.
        """
        # :TODO modify top_level_serializer or pass a list with self as
        # argument?
        registry = {getattr(self._meta , 'resource_name'): self}
        content = serializers.top_level_serializer(registry)
        response = HttpResponse(
            content = content,
            content_type = 'application/xml')
        response = add_das_headers(response)
        return response


    def get_features(self, request, **kwargs):
        """ Returns a DAS GFF xml.  

        Calls ''obj_get'' to fetch only the objects requested.  This method
        only responds to HTTP GET.  

        Similar to obj_get_list in ModelResource with modifications.  Need to
        make this a factory so that specific fields and be mapped to the
        segment and start end.  
        """
        if hasattr(request, 'GET'):
            reference, start, stop = parse_das_segment(request)
        query_seg = {'id': reference, 'start':start, 'stop':stop}
        # Attempts to be smart about field mapping
        # :TODO implement this
        if 'chrom' in self.fields:
            pass
        # :TODO Need to implement type, category, feature_id and maxbins
        # :TODO Check if model has a Kent bin.  Also benchmark using this overa
        # standard index.
        reference = int(reference)
        self.is_authenticated(request)
        try:
            if start:
                base_object_list = self.get_object_list(request).filter(
                        Q(start__range=(start,stop)) |\
                        Q(end__range=(start,stop)), 
                        chrom__exact = reference)
            else:
                base_object_list = self.get_object_list(request).filter(
                        chrom__exact = reference)
            # :TODO authorization check
        except ValueError:
            raise BadRequest('Invalid Request')
        # Do I need to convert to a bundle, or too much.  
        '''
        bundles = [self.build_bundle(obj=obj, request=request) for obj in\
                base_object_list]
        to_be_serialized = [self.full_dehydrate(bundle) for bundle in bundles]
        '''
        content = feature_serializer(request, base_object_list, **query_seg)
        response = HttpResponse(content = content,
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response


class BaseResult(object):
    """ Construct an object similar to Django's ORM for universal input into
    the serializer.  
    """

    def __init__(self, *initial_data, **kwargs):
        print('creating base result')
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
            for key in kwargs:
                setattr(self, key, kwargs[key])


def generate_bed_dict(line, bed_header):
    """ Generate a dictionar with the default bed header labels as keys and
    attributes as values.  
    """
    print('attempting to generate bed dict')
    out_dict = dict((key, value) for key, value in izip(bed_header, line))
    print(out_dict)
    return(out_dict)


class DASResource(Resource):
    """ A class to handle file formats
    """
    capability = "features"
    chr_type = "Chromosome"
    authority = "Gr"
    version = "37"
    organism = "homo sapiens"
    filename = ''

    
    class Meta:
        default_format = 'application/xml'

    def get_list(self, request, **kwargs):
        registry = {getattr(self._meta , 'resource_name'): self}
        content = serializers.top_level_serializer(registry)
        response = HttpResponse(
            content = content,
            content_type = 'application/xml')
        response = add_das_headers(response)
        return response
    
    
    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/features" %
                (self._meta.resource_name), self.wrap_view('get_features'),
                name = 'api_get_features'),
        ]
    
    
    def get_features(self, request, **kwargs):
        """ Returns a DAS GFF xml.  

        Calls ''obj_get'' to fetch only the objects requested.  This method
        only responds to HTTP GET.  

        Similar to obj_get_list in ModelResource with modifications.  Need to
        make this a factory so that specific fields and be mapped to the
        segment and start end.  
        """
        try:
            import pysam
        except ImportError:
            raise ImportError('Handling of bam files requires pysam')
        try:
            fh = open(self.filename, 'rU')
        except ValueError:
            print("can't find file")
        print(self.filename)
        if hasattr(request, 'GET'):
            reference, start, stop = parse_das_segment(request)

        BED_HEADERS = ['reference', 'start', 'end', 'name', 'score',
        'strand','thickstart', 'thickend', 'itemRgb', 'blockcount',
        'blocksizes', 'blockstarts']

        print('generating hits')

        hits = []
        # Just a test        
        # Maybe offer a suggestion for non-indexed files?
        #fh.seek(position)
        for line in fh:
            line = line.rstrip("\n").split("\t")
            if line[0] == str(reference):
                print(line)
                if start < int(line[1]) < stop or\
                        start < int(line[2]) < stop:
                    print('yes')
                    hmm = generate_bed_dict(line, BED_HEADERS)
                    print(hmm)
                    hits.append(BaseResult(hmm))

                    print(hits)
                else:
                    print('no')
            else: pass 
        print(hits)
        content = feature_serializer(request, hits) 
        response = HttpResponse(content = content,
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response

