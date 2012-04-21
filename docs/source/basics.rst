***********
Basics
***********

django-biodas uses django-tastypie as the basis for generating an api like
response that fits the biodas specification.  

Adding a Django Model
~~~~~~~~~~~~~~~~~~~~~

If you already have a django ORM for biological data, it is straigtforward to generate a biodas compliant api using django-biodas.

1. Add tastypie and biodas to your ''INSTALLED_APPS''.
2. Create an api diretory in your app with an empty '__init__.py''.
3. In the api directory, create a ''<my_app>/api/resource.py'' file and place
   the following in it::
    
    from biodas import DASModelResource
    from yourapp.models import YourModel

    class YourResource(DASModelResource):
        class Meta:
        resource_name ='bed'
        queryset = YourModel.objects.all()

4. Register the resource with the DAS api in ''urls.py'' ::
   
    from api.resource import YourResource
    
    api = DAS()
    api.register(YourResource())

    urlpatterns = patterns('',
      (r'^api/', include(api.urls)),
      )


Generating a resource from a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally django-biodas makes it really easy to generate an api from a file
such as a BAM, BIGWIG, VCF, or BIGBED file.
