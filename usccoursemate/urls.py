from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# 简单的根路径视图函数
def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'USCCoursemate API is running',
        'api_version': '1.0',
        'endpoints': {
            'auth': '/api/auth/',
            'groups': '/api/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),  # 添加根路径处理
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('groups.urls')),
]

# 在开发环境中提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)