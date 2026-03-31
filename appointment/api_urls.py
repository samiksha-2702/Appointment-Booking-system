from rest_framework import routers
from .views import DoctorViewSet, AppointmentViewSet

router = routers.DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = router.urls