""" Contains resources that bind django ORMs or to file resources
"""
from itertools import izip

from django.conf.urls.defaults import url
from django.http import HttpResponse
from django.db.models import Q
from tastypie.resources import (Resource, ModelResource,
                                DeclarativeMetaclass, ResourceOptions,
                                ModelDeclarativeMetaclass)

from utils import parse_das_segment, add_das_headers
import serializers
from serializers import (feature_serializer, 
        stylesheet_serializer, DASSerializer)
from tastypie.utils.mime import determine_format


FILETYPES = {
        'bam': 'bam_query',
        'bed': 'bed_query',
        'bb': 'bigbed_query',
        'bw': 'bigwig_query',
        'gff': 'gff_query',
        'vcf': 'vcf_query',
        'fa': 'fa_query',
        }

class DasResourceOptions(ResourceOptions):
    """ Provides Human defaults for the metadata.  User really needs to set
    these however.
    """
    serializer = DASSerializer()

    capability = "feature"
    chr_type = "Chromosome"
    authority = "GRCh"
    version = 37
    method = 'Default'
    ftype = 'Default'

    filename = 'placeholder.bed'
    queryfunc = ''
    ref_prefix = ''
    # :TODO Make it easy to specify a custom query function
    filetype = None


class DasFileMetaclass(DeclarativeMetaclass):
    FILETYPES = {
            'bam': 'bam_query',
            'bed': 'bed_query',
            'bb': 'bigbed_query',
            'bw': 'bigwig_query',
            'gff': 'gff_query',
            'vcf': 'vcf_query',
            'fa': 'fa_query',
            }

    def __new__(cls, name, bases, attrs):
        """ This gets called both on resource class and on the user generated
        inherited classes.  Unfortunately that means that filetype is set
        before that.  Should a check be implemented here?
        """
        new_class = super(DasFileMetaclass, cls).__new__(cls, name, bases,
                attrs)
        opts = getattr(new_class, 'Meta', None)
        new_class._meta = DasResourceOptions(opts)
        # Note that ResourceOptions and DasResourceOptions both get called.
        filename = getattr(new_class._meta, "filename")
        filetype = getattr(new_class._meta, "filetype", None)

        if not filetype or filetype == '' and name != 'DasResource':
            global FILETYPES
            try:
                extension = filename.split(".")[1]
                if extension in FILETYPES:
                    filetype = extension
                    setattr(new_class._meta, "filetype", filetype)
                else:
                    raise KeyError("Bleg No extension of filename found")

            except IndexError:
                raise KeyError("No extension of filename found")
        else:
            # Check if it is a valid filetype
            pass
        print('end')
        return new_class


class DasModelMetaclass(ModelDeclarativeMetaclass):
    def __new__(cls, name, bases, attrs):

        new_class = super(DasModelMetaclass, cls).__new__(cls, name, bases,
                attrs)

        # Overide previous meta with das defaults
        opts = getattr(new_class, 'Meta', None)
        new_class._meta = DasResourceOptions(opts)
        return new_class


class DasBaseResource(Resource):
    """ A Base Class for DAS resources.  Use DasModelResource or
    DasFileResource.
    """

    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/features" %
                (self._meta.resource_name), self.wrap_view('get_features'),
                name = 'api_get_features'),
            url(r"^(?P<resource_name>%s)/stylesheet" %
                (self._meta.resource_name), self.wrap_view('get_stylesheet'),
                name = 'api_get_stylesheet'),
            url(r"^(?P<resource_name>%s)/types" %
                (self._meta.resource_name), self.wrap_view('get_types'),
                name = 'api_get_types'),
        ]


    def get_stylesheet(self, request, **kwargs):
        registry = {getattr(self._meta , 'resource_name'): self}
        content = serializers.bam_stylesheet(request)
        response = HttpResponse(
                content = content,
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response

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

    def get_types(self, request, **kwargs):
        registry = {getattr(self._meta , 'resource_name'): self}
        content = serializers.type_serializer(request)
        response = HttpResponse(
                content = content,
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response

    # Views

    def get_features(self, request, **kwargs):
        """ Needs to be implemented at the user level or altered by a child
        class.
        """
        raise NotImplementedError()


class DasModelResource(ModelResource):
    """  For resources that are already from the django ORM.

    Requires there to be a chrom, start, end at the very least.
    This should probably inherit from a generic DASResources class.
    """
    # :TODO Need to check that the django model has some required fields
    # upon initialization
    __metaclass__ = DasModelMetaclass

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
        if 'chrom' in self.fields:
            pass
        try:
            reference = int(reference)
        except ValueError:
            reference = reference
        self.is_authenticated(request)
        # :TODO put this throught the regular filter
        try:
            if start:
                base_object_list = self.get_object_list(request).filter(
                        Q(start__range=(start, stop)) |\
                        Q(end__range=(start, stop)),
                        chrom__exact = reference)
            else:
                base_object_list = self.get_object_list(request).filter(
                        chrom__exact = reference)
            # :TODO authorization check
        except ValueError:
            raise ValueError('Invalid Request')
        bundles = [self.build_bundle(obj=obj, request=request) for obj in\
                base_object_list]
        to_be_serialized = [self.full_dehydrate(bundle) for bundle in bundles]
        # passing reqeust into options is, maybe I should pass in the whole
        # request? 
        options = {'query': query_seg, 
                'method': self._meta.method, 
                'request_string': request.META['QUERY_STRING'],
                'request_path': request.path,
        }
        content = self.serialize(request, to_be_serialized, 'xml',
                options=options)
        response = HttpResponse(content = content,
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response


class BaseResult(object):
    """ Construct an object similar to Django's ORM for universal input into
    the serializer.

    :TODO Probably too much overhead to make a python object.  However allows
    generalization.
    """

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
            for key in kwargs:
                setattr(self, key, kwargs[key])


def generate_bed_dict(line, bed_header):
    """ Generate a dictionary with the default bed header labels as keys and
    attributes as values.
    """
    out_dict = dict((key, value) for key, value in izip(bed_header, line))
    return(out_dict)


class DasResource(DasBaseResource):
    """ A class to handle file formats
    """
    __metaclass__ = DasFileMetaclass


    def get_features(self, request, **kwargs):
        """ Returns a DAS GFF xml.

        Calls ''obj_get'' to fetch only the objects requested.  This method
        only responds to HTTP GET.

        Similar to obj_get_list in ModelResource with modifications.  Need to
        make this a factory so that specific fields can be mapped to the
        segment and start end.
        """

        if hasattr(request, 'GET'):
            reference, start, stop = parse_das_segment(request)
        query_seg = {'id': self._meta.ref_prefix + reference, 'start':start, 'stop':stop}


        query_method = getattr(self, "%s_query" % self._meta.filetype,  None)
        if query_method:
            hits = query_method(**query_seg)
        else:
            raise NotImplementedError("No query function implemented for\
                    filetype %s" % self._meta.filetype)

        try:
            content = feature_serializer(request, hits, format_json = getattr(self._meta , 'json'), **query_seg) 
        except:
            content = feature_serializer(request, hits, **query_seg) 
        response = HttpResponse(content = content,
                content_type = 'application/xml')
        response = add_das_headers(response)
        return response


    def bed_query(self, **kwargs):
        ''' Returns a list of hits.

        This is for unindexed files, and should only be used if the BED file
        is very small.
        '''
        try:
            file_handle = open(self._meta.filename, 'rU')
        except ValueError:
            print("can't find file")
        hits = []
        BED_HEADERS = ['reference', 'start', 'end', 'name', 'score',
        'strand','thickstart', 'thickend', 'itemRgb', 'blockcount',
        'blocksizes', 'blockstarts']
        # :TODO deal with file comments

        for line in file_handle:
            line = line.rstrip("\n").split("\t")
            if line[0] == str(kwargs['id']):
                if not kwargs['start'] and not kwargs['stop']:
                    hit = generate_bed_dict(line, BED_HEADERS)
                    hits.append(BaseResult(hit))
                elif kwargs['start'] < int(line[1]) < kwargs['stop'] or\
                        kwargs['start'] < int(line[2]) < kwargs['stop']:
                    hit = generate_bed_dict(line, BED_HEADERS)
                    hits.append(BaseResult(hit))
                else: pass
            else: pass

        return hits


    def bam_query(self, **kwargs):
        """ :TODO implement a python only bam ready for pypy
        """
        BAM_HEADERS = [
                'query_id','flag', 'reference', 'start',
                'mapq', 'cigar', 'temp', 'temp1', 'temp2', 'seq',
                'bq'
                ]
        try:
            import pysam
        except ImportError:
            raise ImportError('Handling of bam files requires pysam')

        try:
            file_handle = pysam.Samfile(self._meta.filename, 'rb')
        except IOError:
            raise IOError('Could not find bam file')

        hits = []
        ref_id = str(kwargs['id'])

        reads = file_handle.fetch(
                ref_id , 
                int(kwargs['start']), 
                int(kwargs['stop']))
        
        for read in reads:
            hit = {
                    'reference': file_handle.getrname(read.tid),
                    'start': read.pos,
                    'end': read.pos + read.qlen,
                    'name': read.qname,
                    }
            hits.append(BaseResult(hit))

        return(hits)

    def fa_query(self, **kwargs):
        """ Handle 2-bit queries as well
        """
        try:
            import twobitreader 
        except ImportError:
            raise ImportError('Handling of bam files requires pysam')
        try:
            file_handle = twobitreader.TwoBitFile(self._meta.filename, 'rb')
        except IOError:
            raise IOError('Could not find bam file')


    def vcf_query(self, **kwargs):
        """ VCF file needs to be a tabix indexed file
        """
        try:
            import pysam
        except ImportError:
            print("Can't find pysam")
            raise ImportError('Handling of bam files requires pysam')

        try:
            file_handle = pysam.Tabix(self._meta.filename, 'rb')
        except IOError:
            raise IOError('Could not find bam file')

        reads = file_handle.fetch(
                kwargs['id'],
                kwargs['start'],
                kwargs['stop'])

        hits = dict(**reads)
        print("hits")

        raise NotImplementedError()


    def gff_query(self, **kwargs):
        raise NotImplementedError()


    def bw_query(self, **kwargs):
        """ Handler for bigwig files.
        """
        raise NotImplementedError()

    def bb_query(self, **kwargs):
        raise NotImplementedError()


    def tbx_query(self, **kwargs):
        raise NotImplementedError()
