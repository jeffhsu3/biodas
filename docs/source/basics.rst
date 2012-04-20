***********
Basics
***********

Adding a Django Model
~~~~~~~~~~~~~~~~~~~~~

If you already have a django ORM for biological data.  It is
fairly straigtforward to generate a biodas compliant api using django-biodas.
In a resource.py within your app have somthing like the following:  
::

    from biodas import DASModelResource
    from yourapp.models import YourModel
    class YourResource(DASModelResource):
        class Meta:
        resource_name ='bed'
        queryset = YourModel.objects.all()



Generating a resource from a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
