from djoser import serializers
from django.contrib.auth import get_user_model
from rest_framework.fields import ReadOnlyField, IntegerField, CharField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer

from accounts.models import Profile

User = get_user_model()


class UserCreateSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        depth = 1
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_superuser', 'is_staff', 'profile')


class ProfileSerializer(HyperlinkedModelSerializer):
    user_url = HyperlinkedIdentityField(view_name='customuser-detail', lookup_field='id')
    user = ReadOnlyField(source='user.id')
    username = CharField(source='user.username', read_only=True)
    email = CharField(source='user.email')
    first_name = CharField(source='user.first_name')
    last_name = CharField(source='user.last_name')

    class Meta:
        model = Profile
        depth = 1
        lookup_field = 'id'
        fields = ('url', 'username', 'email', 'first_name', 'last_name',
                  'about_you', 'user', 'user_url')

    def get_full_name(self, obj):
        request = self.context['request']
        return request.user.get_full_name()

    def update(self, instance, validated_data):
        # retrieve the User
        user_data = validated_data.pop('user', None)
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        # retrieve Profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.user.save()
        instance.save()
        return instance
