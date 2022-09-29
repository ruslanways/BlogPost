import copy
from pprint import pprint
from rest_framework import serializers
from .models import CustomUser, Like, Post
from django.contrib.auth.password_validation import validate_password



class UserSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='user-detail-update-destroy-api')
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = 'url', 'id', 'username', 'email', 'last_request', 'last_login', 'date_joined', 'is_staff', 'is_active', 'password', 'password2'
        extra_kwargs = {
            'password': {'style': {'input_type': 'password'} ,'write_only': True, 'validators': [validate_password]},
        }
        read_only_fields = 'id', 'is_active', 'last_request', 'last_login', 'date_joined', 'is_staff'

    def validate(self, data):
        data_without_password2 = copy.deepcopy(data)
        del data_without_password2['password2']
        validate_password(password=data.get('password'), user=CustomUser(**data_without_password2))
        return data

    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'Password': 'Passwords must match.'})
        instance = self.Meta.model._default_manager.create_user(
                                                    email=validated_data['email'],
                                                    username=validated_data['username'],
                                                    password=validated_data['password']
        )
        return instance

class UserDetailSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='user-detail-update-destroy-api')
    # Adding posts and likes that user has to show in response api
    post_set = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='post-detail-api')
    like_set = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='like-detail-api')

    class Meta:
        model = CustomUser
        fields = 'url', 'id', 'username', 'email', 'last_request', 'last_login', 'date_joined', 'is_staff', 'is_active', 'post_set', 'like_set', 'password'
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'password': {'required': False, 'write_only': True}
        }
        read_only_fields = 'id', 'is_active', 'last_request', 'last_login', 'date_joined', 'is_staff'
    
    def validate(self, data):
        user = CustomUser(**data) if data.get('password', False) and len(data) > 1 else self.context['obj'] 
        if data.get('password'):
            validate_password(password=data.get('password'), user=user)
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password_new = validated_data.get('password')
        if password_new:
            instance.set_password(password_new)
        instance.save()
        return instance

class TokenRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200)


class PostSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='post-detail-api')
    published = serializers.BooleanField(write_only=True, required=False, default=True, initial=True)
    author = serializers.HyperlinkedRelatedField(read_only=True, source='author.id', view_name='user-detail-update-destroy-api')
    # Example way to associate new created post with current user:
    # author = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
    # author_id = serializers.IntegerField(read_only=True, default=serializers.CurrentUserDefault())
    likes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = 'id', 'url', 'author', 'title', 'content', 'image', 'created', 'updated', 'published', 'likes'


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='post-detail-api')
    author = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail-update-destroy-api')

    class Meta:
        model = Post
        fields = 'id', 'url', 'author', 'title', 'content', 'image', 'created', 'updated', 'published', 'like_set'


class LikeSerializer(serializers.Serializer):

    created__date = serializers.DateField()
    likes = serializers.IntegerField()


class LikeDetailSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='like-detail-api')
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail-update-destroy-api')
    post = serializers.HyperlinkedRelatedField(read_only=True, view_name='post-detail-api')

    class Meta:
        model = Like
        fields = 'url', 'id', 'created', 'user', 'post'

