""" Contains serializers.
"""

from lxml.etree import Element, tostring
import json

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
            in zip(['id','label'], [feat_id, label])\
            if value) 
    return(attr_dict)


def top_level_serializer(resources, options=None):
    """ Serializes the top-level query
    """
    
    if options:
        print(options)
    
    sources = Element('SOURCES')
    for name, resource in resources.items():
        source = Element('SOURCE', uri = name)
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


def feature_serializer(request, bundle, json=False, **kwargs):
    """ Serialize a list of features.  
    """
    if json == False:
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
        return json.dump(bundle)
