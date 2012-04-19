import lxml
from lxml.etree import parse as parse_xml
from lxml.etree import Element, tostring
from tastypie.serializers import Serializer, get_type_string
from tastypie.bundle import Bundle

class DASType_serializer(Serializer):
    def to_etree(self, data, options=None, name=None, depth=0):
        pass

class DAS_serializer(Serializer):
    """
    Serializer DAS sources to format
    """

    def to_etree(self, data, options=None, name=None, depth=0):
        """
        Given some data, converts that data to an ''etree.Element'' for use in
        the XML output
        """

        if isinstance(data, (list, tuple)):
            element = Element(name or 'objects')
            if name:
                element = Element(name)
            else:
                element = Element('objects')
            for item in data:
                element.append(self.to_etree(item, options, depth=depth+1))
        elif isinstance(data, dict):
            if depth == 0:
                element = Element(name or 'response')
            else:
                element = Element(name or 'objects')
            for (key, value) in data.iteritems():
                element.append(self.to_etree(value, options, name = key,
                                             depth=depth+1))
        elif isinstance(data, Bundle):
            element = Element(name or 'object')
            for field_name, field_object in data.data.items():
                element.append(self.to_etree(field_object, options,
                                             name=field_name,
                                             depth = depth + 1))
        elif hasattr(data, 'dehydrated_type'):
            if getattr(data, 'dehydrated_type', None) == 'related' and\
               data.is_m2m == False:
                if data.full:
                    return self.to_etree(data.fk_resource, options, name,
                                         depth + 1)
                else:
                    return self.to_etree(data.value, options, name, depth + 1)
            elif gettattr(data, 'dehydrated_type', None) == 'related' and\
                    data.is_m2m == True:
                if data.full:
                    element = Element(name or 'objects')
                    for bundle in data.m2m_bundles:
                        element.append(self.to_etree(bundle, options,
                                                     bundle.resource_name,
                                                     depth+1))
                else:
                    element = Element(name or 'objects')
                    for value in data.value:
                        element.append(self.to_etree(value, options, name,
                                                     depth = depth+1))
            else:
                return self.to_etree(data.value, options, name)
        else:
            element = Element(name or 'value')
            simple_data = self.to_simple(data, options)
            data_type = get_type_string(simple_data)

            if data_type != 'string':
                element.set('type', get_type_string(simple_data))

            if data_type != 'null':
                if isinstance(simple_data, unicode):
                    element.text = simple_data
                else:
                    element.text = force_unicode(simple_data)


        return element


    def to_xml(self, data, options=None):
        options = options or {}
        print('before to_simple:')
        print(data)
        data = self.to_simple(data, options)
        print(data)

        if lxml is None:
            raise ImproperlyConfigured("django-das requires lxml.")

        etree = self.to_etree(data, options, name = 'SOURCES')
        return tostring(etree, xml_declaration=True,
                        encoding = 'utf-8', pretty_print=True)

    def from_xml(self, content):
        """
        Given some XML data, returns a Python dictionary
        """
        options = options or {}

        if lxml is None:
            raise ImproperlyConfigured("django-das requires lxml.")


def top_level_serializer(resources, options=None):
    """ Serializes the top-level query
    """
    sources = Element('SOURCES')
    for name in resources:
        source = Element('SOURCE', uri = name)
        sources.append(source)

        source.append(Element('MAINTAINER', email = 'jeffhsu3@gmail.com'))
        version = Element('VERSION', uri = name, created='now')
        source.append(version)

        coordinate = Element('COORDINATES', uri = 'uri', source ='data type',
                            authority = 'authority', taxid = 'taxonomy',
                             version='version', test_range='id:start,stop')
        version.append(coordinate)
        version.append(Element('CAPABILITIES', type="das1:command", 
                              query_uri="URL"))
        version.append(Element('PROP', name='key', value="value"))

        coordinate.text = 'hg19'

    return(tostring(sources, xml_declaration = True, encoding ='utf-8',
                    pretty_print = True))

