from django.contrib.auth import get_user_model
from rest_framework.fields import CharField
from rest_framework.serializers import HyperlinkedModelSerializer

from accounts.models import Profile

User = get_user_model()


class UserCreateSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        depth = 1
        fields = ('username', 'first_name', 'last_name', 'email', 'profile', )


class ProfileSerializer(HyperlinkedModelSerializer):
    username = CharField(source='user.username', read_only=True)
    email = CharField(source='user.email')
    first_name = CharField(source='user.first_name')
    last_name = CharField(source='user.last_name')
    company_name = CharField(source='user.company_name')
    phone_number = CharField(source='user.phone_number')

    class Meta:
        model = Profile
        depth = 1
        lookup_field = 'id'
        fields = ('username', 'first_name', 'last_name', 'about_you', 'email', 'phone_number', 'company_name')

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
