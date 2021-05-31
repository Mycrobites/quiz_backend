"""quiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import HomeView
from api.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view()),
    path('api/', include('api.urls')),
    path('api/auth/', include('authentication.api.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('questionbank',getBank,name="bank"),
    path("questionbank/<slug:qid>/change/",editBank),
    path('addquestionnew',newaddquestion),
    path('editquestion/<slug:qid>',editquestion),
    path("progressiveminds/questionbank",lmsBank),
    path("exportquestions",importQuestion),
    path("addquestion",bank),
    path("tagquestion",tagquestion),
    path("addTags",Addtags),
    path("deleteSelected",deleteQuestions),
    path("uploadimages",upload_image)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)