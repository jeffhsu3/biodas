""" Contains serializers.
"""
import lxml
from lxml.etree import Element, tostring
import json
from tastypie.resources import Serializer
from tastypie.serializers import get_type_string, force_unicode
from tastypie.bundle import Bundle
#from tastypie.utils.mime import determine_format

from django.core.exceptions import ImproperlyConfigured


class DASSerializer(Serializer):
    """ Extends Tastypie's serializer
    """

    def to_xml(self, data, options=None):
        options = options or {}
        top = Element('DASSTYLE')
        gff = Element('GFF', href = options['request_path'] + '?' +\
                options['request_string'])
        if lxml is None:
            raise ImproperlyConfigured("Usage of the XML aspects\
                    requires lxml and defusedxml.")
        #print("REQUEST: " + options['request_path'] + options['request_string'])
        out = self.to_etree(data, options)
        top.append(gff)
        gff.append(out)
        segments = gff.xpath("SEGMENT")
        segments[0].set('id', str(options['query']['id']))
        if options['query']['start'] and options['query']['stop']:
            segments[0].set('start', str(options['query']['start']))
            segments[0].set('start', str(options['query']['stop']))
        else: pass
        features = gff.xpath("SEGMENT/FEATURE")
        for i in features:
            try:
                f_id = i.xpath("ID")
                i.set('id', f_id[0].text)
                i.remove(f_id[0])
                f_link = i.xpath("RESOURCE_URI")
                f_link[0].set('href', f_link[0].text)
            except AttributeError:
                print('Serialization Error')
            except IndexError:
                # Occurs for non Models since no id is guranteeded
                # Can't gurantee uniquess either
                f_id = i.xpath("NAME")
                i.set('id', f_id[0].text)
                i.remove(f_id[0])
            method = Element("METHOD")
            # :TODO make this a meta class option
            method.text = options['method']
            ftype = Element("TYPE")
            ftype.text = 'bleh'
            i.append(method)
            i.append(ftype)
        return (tostring(top, xml_declaration=True, encoding='utf-8',
            pretty_print=True))

    def to_etree(self, data, options = None, name = None, depth=0):
        """ Similar to 
        """
        if isinstance(data, (list, tuple)):
            element = Element(name or 'objects')
            if name:
                element = Element(name)
                element.set('type', 'list')
            else: 
                element = Element(name or 'SEGMENT')
                for item in data:
                    element.append(self.to_etree(item , 
                        options, depth=depth+1))
        
        elif isinstance(data, dict):
            if depth == 0:
                element = Element(name or 'response')
            else:
                element = Element(name or 'object')
                element.set('type', 'hash')
            for (key, value) in data.iteritems():
                element.append(self.to_etree(value, options,
                    name=key,depth=depth+1))

        elif isinstance(data, Bundle):
            element = Element(name or 'FEATURE')
            for field_name, field_object in data.data.items():
                element.append(self.to_etree(field_object, {},
                    name=field_name, depth=depth+1))
        else:
            element = Element(name.upper() or 'value')
            simple_data = self.to_simple(data, options)
            data_type = get_type_string(simple_data)
            """
            if data_type != 'string':
                element.set('type', get_type_string(simple_data))
            """

            if data_type != 'NULL':
                if isinstance(simple_data, unicode):
                    element.text = simple_data
                else:
                    element.text = force_unicode(simple_data)
        return element

    def serialize(self, bundle, format='application/json', options={}):
        desired_format = format
        serialized = getattr(self, "to_%s" % 'xml')(bundle, options)
        return serialized
        


def get_type(feat_obj):
    """ Attempt to get the type of a feature if it exists.
    """
    pass


def feature_attributes(feat_obj):
    """ Generate a dictionary for the feature attributes.
    """
    FEAT_LABELS = ['id', 'pk']
    pos_labels = ['name', 'label', 'gene']

    for pk in FEAT_LABELS:
        feat_id = getattr(feat_obj, pk, None)
        if feat_id:
            break

    for name in pos_labels:
        label = getattr(feat_obj, name, None)
        if label:
            break

    attr_dict = dict((key, str(value)) for key, value\
            in zip(['id','label'], [feat_id, label]) if value)
    return(attr_dict)


def top_level_serializer(resources, options=None):
    """ Serializes the top-level query
    """

    if options:
        pass

    sources = Element('SOURCES')
    for name, resource in resources.items():
        source = Element('SOURCE', uri = name, title="test",
                         description='test')
        sources.append(source)
        email = getattr(resource._meta, 'email', 'NA')
        source.append(Element('MAINTAINER', email = email))
        version = Element('VERSION', uri = name, created='now')
        source.append(version)

        # :TODO Coordinate uri needs to be gotton somehow easily and automatically 
        coordinate = Element('COORDINATES',
                uri = 'uri',
                source ='data type',
                authority = 'temp',
                taxid = 'taxonomy',
                version='version',
                test_range='id:start,stop'
                )

        version.append(coordinate)
        version.append(Element('CAPABILITIES', type="das1:command",
                              query_uri="URL"))
        version.append(Element('PROP', name='key', value="value"))
        coordinate.text = 'hg19'

    return(tostring(sources, xml_declaration = True, encoding ='utf-8',
                    pretty_print = True))


def stylesheet_serializer(request):
    dasstyle = Element("DASSTYLE")
    stylesheet = Element("STYLESHEET")
    dasstyle.append(stylesheet)
    category = Element("CATEGORY", id="default")
    dasttype = Element("TYPE", id="default")
    stylesheet.append(category)
    return(tostring(dasstyle, xml_declaration = True, encoding='utf-8',
        pretty_print=True))


def bam_stylesheet(request):
    """ Template this?
    """
    dasstyle = Element("DASSTYLE")
    stylesheet = Element("STYLESHEET")
    dasstyle.append(stylesheet)
    category = Element("CATEGORY", id="default")
    stylesheet.append(category)
    dasttype = Element("TYPE", id="default")
    glyph = Element("GLYPH", zoom='low')
    histogram = Element("HISTOGRAM")
    stylesheet.append(category)
    category.append(dasttype)
    dasttype.append(glyph)
    glyph.append(histogram)
    color1 = Element("COLOR1")
    color1.text = "black"
    color2 = Element("COLOR2")
    color2.text = "red"
    height = Element("HEIGHT")
    height.text = "30"
    glyph.append(color1)
    glyph.append(color2)
    glyph.append(height)
    #read = Element("CATEGORY", id="read")
    dasttype2 = Element("TYPE", id="default")
    category.append(dasttype2)
    glyph2 = Element("GLPYH", zoom='high')
    dasttype2.append(glyph2)
    boxglpyh = Element("BOX")
    glyph2.append(boxglpyh)
    fgcolor = Element('FGCOLOR')
    fgcolor.text = 'black'
    bgcolor = Element('BGCOLOR')
    bgcolor.text = 'blue'
    bump = Element('BUMP')
    bump.text = 'yes'
    zindex = Element('ZINDEX')
    zindex.text = '20'
    height2 = Element("HEIGHT")
    height2.text = '30'
    label = Element('LABEL')
    label.text = 'no'
    boxglpyh.append(height2)
    boxglpyh.append(fgcolor)
    boxglpyh.append(bgcolor)
    boxglpyh.append(zindex)
    boxglpyh.append(bump)
    boxglpyh.append(label)
    return(tostring(dasstyle, xml_declaration = True, encoding='utf-8',
        pretty_print=True))

def type_serializer(request):
    dastypes = Element("DASTYPES")
    gff = Element("GFF", url=request.path)
    # Defaults to over all regions if no id is povided
    segment = Element("SEGMENT")
    _type = Element("TYPE", id = str(0))
    dastypes.append(gff)
    gff.append(segment)
    segment.append(_type)
    return(tostring(dastypes, xml_declaration = True, encoding='utf-8',
        pretty_print=True))

def feature_serializer(request, bundle, format_json=False, **kwargs):
    """ Serialize a list of features.  
    """
    if format_json == False:
        # Remember all values for xml attributes must be strings!
        dasgff = Element('DASGFF')
        das = Element('GFF', href = request.path + '?' +\
                request.META['QUERY_STRING'])
        dasgff.append(das)
        seg_query = dict(((key, str(value)) for key, value in kwargs.items() if\
                value))
        segment = Element('SEGMENT', seg_query)
        das.append(segment)

        for i in bundle:
            # :TODO deal with feature types
            feat_dict  = feature_attributes(i)
            feature = Element("FEATURE", feat_dict) 
            segment.append( feature )
            f_type = Element("TYPE", id = "900", category = "Don't get", 
                    cvID = "SO:1234")
            f_type.text = 'Read'
            feature.append( f_type )
            
            # Hmm need to do something about methods
            method = Element("METHOD")
            method.text = 'HTS'
            feature.append(method)

            # Optional Elements
            opts = ["start", "end", "score", "orientation", "phase", "group",
            "parent", "target"]
            for opt in opts:
                value = getattr(i, opt, None)
                if value:
                    opt_element = Element(opt.upper())
                    opt_element.text = str(value)
                    feature.append(opt_element)
                else: pass
            
        return(tostring(dasgff, xml_declaration = True, encoding ='utf-8',
            pretty_print=True))
    else:
        return json.dumps([feature_attributes(b) for b in bundle])
