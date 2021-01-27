from store import views
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home.as_view(),name="home"),
    path('home/',views.home.as_view(),name='home'),
    path('category/',views.shopbybrand.as_view(),name="shopbybrand"),
    path('cart/',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('confirmation/',views.confirmation,name="confirmation"),
    path('contact/',views.contact,name="contact"),
    path('product/<slug>/',views.ProductDetailView.as_view(),name="product"),
    path('add-to-cart/<slug>/',views.add_to_cart,name="add-to-cart"),
    path('login/',views.login_view,name="login_view"),
    path('register/',views.register,name="register"),
    path('logout/',views.logout_view,name="logout_view"),
    path('profile/',views.Profile.as_view(),name="profile"),
    path('profile/editprofile/',views.Editprofile.as_view(),name="editprofile"),
    path('search/',views.SearchView.as_view(),name="search"),
    path('remove-from-cart/<slug>/',views.remove_from_cart,name="remove"),
    path('remove-single-item-from-cart/<slug>/',views.remove_single_item_from_cart,name="remove-single-item"),
    path('checkout/order_confirmation/',views.order_confirmation,name="order_confirmation"),

    #path('profile/',views.profile,name="profile"),
    #path('product/',views.product,name="product"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)