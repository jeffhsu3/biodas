from django.conf.urls.defaults import url
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.http import HttpResponse
from django.db.models import Q
from tastypie.resources import Resource, ModelResource

from utils import parse_das_segment, add_das_headers
import serializers 
from serializers import feature_serializer


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
            #base_object_list = 
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



class DASResource(Resource):
    """
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
        print('overide urls')

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
        print('get_features called') 
        try:
            import pysam
        except ImportError:
            raise ImportError('handling of bam files requires pysam')
        try:
            fh = open(self.filename, 'rU')
        except ValueError:
            print("can't find file")
        print(self.filename)
        if hasattr(request, 'GET'):
            reference, start, stop = parse_das_segment(request)
        
        #fh.seek(position)
        for line in fh:
            line = line.rstrip("\n").split("\t")
            if line[0] == str(reference):
                print("yes")
        
        response = HttpResponse(content = 'hi',
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response

