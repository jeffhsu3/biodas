""" Contains serializers.
"""

from lxml.etree import Element, tostring


def top_level_serializer(resources, options=None):
    """ Serializes the top-level query
    """
    
    #:TODO lots of fields to fix to reflect the resource
    if options:
        print(options)
    sources = Element('SOURCES')
    for name, resource in resources.items():
        source = Element('SOURCE', uri = name)
        sources.append(source)

        source.append(Element('MAINTAINER', email = 'jeffhsu3@gmail.com'))
        version = Element('VERSION', uri = name, created='now')
        source.append(version)
        coordinate = Element('COORDINATES', uri = 'uri', source ='data type',
                            authority = resource.authority, taxid = 'taxonomy',
                             version='version', test_range='id:start,stop')
        version.append(coordinate)
        version.append(Element('CAPABILITIES', type="das1:command", 
                              query_uri="URL"))
        version.append(Element('PROP', name='key', value="value"))


        coordinate.text = 'hg19'

    return(tostring(sources, xml_declaration = True, encoding ='utf-8',
                    pretty_print = True))


def feature_serializer(request, bundle, **kwargs):
    """ Serialize a feature bundle.  

    :TODO Need to make this more generic for both DAS model resources and File
    Resources.
    """
    dasgff = Element('DASGFF')
    req_href = request.path + '?' +\
            request.META['QUERY_STRING']
    das = Element('GFF', href = req_href)
    # :TODO How to handle types
    dasgff.append(das)
    # :TODO check to see if all segments are the same in the bundle
    seg_query = dict(((key,str(value)) for key, value in kwargs.items() if\
            value))
    segment = Element('SEGMENT', seg_query)
    das.append(segment)
    for i in bundle:
        feature = Element("FEATURE", id = str(i.pk), label = i.gene) 
        segment.append(feature)
        # :TODO How to handle types
        f_type = Element("TYPE", id = "900", category = "Don't get", cvID = "SO:1234")
        f_type.text = 'Read'
        feature.append(f_type)
        method = Element("METHOD")
        method.text = 'HTS'
        feature.append(method)
        start = Element("START")
        start.text = str(i.start)
        feature.append(start)
        end = Element("END")
        end.text = str(i.end)
        feature.append(end)
    return(tostring(dasgff, xml_declaration = True, encoding ='utf-8',
        pretty_print=True))
