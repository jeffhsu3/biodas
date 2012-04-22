""" Contains serializers.
"""

from lxml.etree import Element, tostring


def get_label(feat_obj):
    """ Attempt to be intelligent about getting the label/name
    of a feature.
    """
    pos_labels = ['name', 'label', 'gene']
    for name in pos_labels:
        label = getattr(feat_obj, name, None)
        if label:
            break
    return(label)


def get_type(feat_obj):
    """ Attemt to get the type of a feature if it exists.
    """
    pass

def feature_attributes(label, pk):
    """ Generate a dictionary for the feature attributes
    """
    pass


def top_level_serializer(resources, options=None):
    """ Serializes the top-level query
    """
    
    if options:
        print(options)
    sources = Element('SOURCES')
    for name, resource in resources.items():
        source = Element('SOURCE', uri = name)
        sources.append(source)

        email = getattr(source, 'email', 'NA')

        source.append(Element('MAINTAINER', email = email))
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
    """ Serialize a list of feature.  
    """
    #print('beginning serialization')
    dasgff = Element('DASGFF')
    das = Element('GFF', href = request.path + '?' +\
            request.META['QUERY_STRING'])
    dasgff.append(das)
    seg_query = dict(((key, str(value)) for key, value in kwargs.items() if\
            value))
    segment = Element('SEGMENT', seg_query)
    das.append(segment)
    #print('first part done')


    for i in bundle:
        print(i)
        # Attempt to be intelligent about the gene/label name
        # How to handle Nones?
        feature = Element("FEATURE", id = str(i.pk), label = i.gene) 
        segment.append(feature)
        f_type = Element("TYPE", id = "900", category = "Don't get", 
                cvID = "SO:1234")
        f_type.text = 'Read'
        feature.append(f_type)
        method = Element("METHOD")
        method.text = 'HTS'
        feature.append(method)
        #print('Required Sections done')

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
        #print('opts done')
        
    return(tostring(dasgff, xml_declaration = True, encoding ='utf-8',
        pretty_print=True))
