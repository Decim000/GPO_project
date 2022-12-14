from rest_framework import mixins, viewsets, permissions

from accounts.models import Profile
from accounts.permissions import IsOwnerOrReadOnly
from accounts.serializers import ProfileSerializer


class ProfileViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
