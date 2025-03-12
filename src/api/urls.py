from django.urls import path
from api import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from api.views.test_views import (
    TestMineralsAgentView,
    TestAgentChatView,
    TestMineralQueryView
)

urlpatterns = [
    path('', views.test_connection, name='index'),
    path('test/connection/', views.test_connection, name='test-connection'),
    path('test-minerals/', TestMineralsAgentView.as_view(), name='test-minerals-agent'),
    path('test/minerals/', TestMineralsAgentView.as_view(), name='test-minerals'),
    path('test/chat/', TestAgentChatView.as_view(), name='test-agent-chat'),
    path('test/query/', TestMineralQueryView.as_view(), name='test-mineral-query'),
    
    #v1 API
    #path('v1/', views.example, name='example'),
    
    #API docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
]