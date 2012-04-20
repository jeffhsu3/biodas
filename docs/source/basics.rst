***********
Basics
***********

django-biodas uses django-tastypie as the basis for generating an api like
response that fits the biodas specification.  

Adding a Django Model
~~~~~~~~~~~~~~~~~~~~~

If you already have a django ORM for biological data, it is straigtforward to generate a biodas compliant api using django-biodas.
In a resource.py within your app generate a resource from the model like the
following:  
::

    from biodas import DASModelResource
    from yourapp.models import YourModel
    
    class YourResource(DASModelResource):
        class Meta:
        resource_name ='bed'
        queryset = YourModel.objects.all()



Generating a resource from a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally django-biodas makes it really easy to generate an api from a file
such as a BAM, BIGWIG, or BIGBED file.
