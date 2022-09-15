import copy
from dataclasses import fields
from email.policy import default
from rest_framework import serializers
from .models import CustomUser, Like, Post
from django.contrib.auth.password_validation import validate_password


class PostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

class PostCreateSerializer(PostsSerializer):

    # populate the author field autmatically to current authenticated user
    # if the author filed will be prompt explicitly - it'll be ignored
    author = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
    author_id = serializers.IntegerField(read_only=True, default=serializers.CurrentUserDefault())
    published = serializers.BooleanField(default=True, initial=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = 'id', 'username', 'email', 'last_request', 'last_login', 'date_joined', 'is_staff', 'is_active'

class UserCreateSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = 'id', 'username', 'email', 'is_active', 'password', 'password2'
        extra_kwargs = {
            'password': {'style': {'input_type': 'password'} ,'write_only': True, 'validators': [validate_password]},
            'id': {'read_only': True},
            'is_active': {'read_only': True},
        }
    
    # add standard Django validators
    # it's important to use object level validator here, because one of the Django validators require user object
    # for comparsion fields
    def validate(self, data):
        data_without_password2 = copy.deepcopy(data)
        del data_without_password2['password2']
        if not validate_password(password=data.get('password'), user=CustomUser(**data_without_password2)):
            return data

    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']
        print(password)
        print(password2)
        if password != password2:
            raise serializers.ValidationError({'Password': 'Passwords must match.'})
        instance = self.Meta.model._default_manager.create_user(
                                                    email=validated_data['email'],
                                                    username=validated_data['username'],
                                                    password=validated_data['password']
        )
        return instance



