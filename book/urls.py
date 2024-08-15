from rest_framework.routers import DefaultRouter

from book.views import BookViewSet

app_name = "books"

router = DefaultRouter()
router.register("", BookViewSet, basename="books")

urlpatterns = router.urls
