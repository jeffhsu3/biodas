***********
Basics
***********

django-biodas uses django-tastypie as the basis for generating a xml 
response that follows the biodas specification.  

Adding a Django Model
~~~~~~~~~~~~~~~~~~~~~

If you already have a django ORM for biological data, it is straigtforward to generate a biodas compliant api using django-biodas.

1. Add tastypie and biodas to your ''INSTALLED_APPS''.
2. Create an api diretory in your app with an empty '__init__.py''.
3. In the api directory, create a ''<my_app>/api/resource.py'' file and place
   the following in it::
    
    from biodas import DasModelResource
    from yourapp.models import YourModel

    class YourResource(DasModelResource):
        class Meta:
            resource_name ='yourdata'
            queryset = YourModel.objects.all()

            version = '36'
            authority = 'NCBI'

4. Register the resource with the DAS api in ''urls.py'' ::
   
    from biodas import DAS
    from api.resource import YourResource
    
    api = DAS()
    api.register(YourResource())

    urlpatterns = patterns('',
      (r'^api/', include(api.urls)),
      )

Doing so generates a api that is accessible from this url:::
   
   /api/yourdata

Querying over features:::

   /api/yourdata/features?segment=chr1:20,60



Generating a resource from a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally django-biodas makes it really easy to generate an api from a file
such as a BAM, BIGWIG, VCF, BED, GFF or BIGBED file::

   from biodas import DasFileResource

   class FileResource(DasFileResource):
       class Meta:
           filename = 'my.gff'
           resource_name = 'mygff'
            

biodas attempts to intelligently parse the file format.  You can manually set
the file format using:::

   class Meta:
       filetype = 'gff'


Note unindexed files such as BEDFiles will have long query times.


You can also generate a reference server in addition to a feature server.  

JSON based responses
~~~~~~~~~~~~~~~~~~~~
Although the xml response is the default response for biodas servers, biodas
has the option to return JSON responses.  To serialize features in json, simply
set json to True in the meta file.  The specification for the JSON response can
be found :TODO 


Registering the server with the DAS registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Not yet implemented
