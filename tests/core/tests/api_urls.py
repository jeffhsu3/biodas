from django.conf.urls.defaults import *
from core.tests.api import DAS, BedResource, QTLResource

api = DAS()
api.register(BedResource())
api.register(QTLResource())

urlpatterns = patterns('',
    (r'^api/', include(api.urls)),
                      )
