from django.contrib import admin
from django.urls import path, include
from tathastucrystal.views import home
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # Django built-in auth urls (password reset etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # App URLs with namespace
    path('crystal/', include(('crystal.urls', 'crystal'), namespace='crystal')),
    path('worship/', include(('worship.urls', 'worship'), namespace='worship')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('order/', include(('order.urls', 'order'), namespace='order')),
    path('account/', include(('account.urls', 'account'), namespace='account')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('payment/', include('payment.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
