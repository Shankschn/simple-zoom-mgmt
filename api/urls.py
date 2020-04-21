from django.urls import path
from . import views

urlpatterns = [
        path('sqhys/', views.sqhys),
        # # path('cxhys/', views.cxhys),
        # path('krdadmin/', views.krdadmin),
        # path('addzoomadmin/', views.addzoomadmin),
        # path('cxzoomadmin/', views.cxzoomadmin),
        # path('fsyj/', views.fsyj),
        # path('cxhyszt/', views.cxhyszt),
        path('zfhys/', views.zfhys),
]