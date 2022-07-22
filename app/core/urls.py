from rest_framework.routers import DefaultRouter
from .views import LinkViewSet, LoginViewSet, RegisterViewSet, CreateViewEditLinkViewSet
from django.urls import path, include

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'register', RegisterViewSet,basename="register")
router.register(r'login', LoginViewSet,basename="login")
router.register(r'links', LinkViewSet,basename="links")
router.register(r'create', CreateViewEditLinkViewSet,basename="create")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
