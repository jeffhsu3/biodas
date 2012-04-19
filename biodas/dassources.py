from tastypie.resources import Resource, ModelResource

class DASModelResource(ModelResource):
    """  For resources that are already from the django ORM.

    Requires there to be a chrom, start, end at the very least
    """
    DAS_VERSION = '1.6'

    class Meta:
        default_format = 'application/xml'

    def override_urls(self):

        return []

class DASResource(Resource):
    """
    """
    DAS_VERSION = '1.6'
    pass
