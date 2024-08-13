from rest_framework.routers import DefaultRouter
from .views import BookViewSet

app_name = "book"

router = DefaultRouter()
router.register("", BookViewSet, basename="book")

urlpatterns = router.urls
