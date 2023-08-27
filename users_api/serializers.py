# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime
from user_network_api.models import Inspiration




User = get_user_model()

# User Registration Serializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=16)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'},max_length=16)
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(max_length=100)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    biography = serializers.CharField(max_length=500, allow_blank=True, allow_null=True, required=False)
    created_at = serializers.DateTimeField(default=datetime.now())
    updated_at = serializers.DateTimeField(default=datetime.now())
    is_verified = serializers.BooleanField(default=False, required=False)
    verification_token = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False)


    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'biography', 'created_at', 'updated_at', 'is_verified', 'verification_token', 'last_login']

    def validate(self, attrs):

        # Check if passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"message": "Password fields didn't match."})

        return attrs
    
    def create(self, validated_data):
        try:
            # Create user instance
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],                
            )
            user.set_password(validated_data['password'])
            user.save()

            # Return success message and user instance
            return user

        except Exception as e:
            raise serializers.ValidationError({'message': 'Username or email already exists.', 'error': str(e)})


#Login Serializer

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get('password', None)

        if username and password:
            user = User.objects.filter(username=username).first()

            if user:
                if not user.is_active:
                    raise serializers.ValidationError({"message": "User account is not active."})
                
                if not user.is_verified:
                    raise serializers.ValidationError({"message": "User account is not verified."})

                if not user.check_password(password):
                    raise serializers.ValidationError({"message": "Unable to log in with provided credentials."})

            else:
                raise serializers.ValidationError({"message": "Unable to log in with provided credentials."})

        else:
            raise serializers.ValidationError({"message": "Must include 'username' and 'password' fields."})

        attrs['user'] = user
        return attrs


# User verification serializer
class UserVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100) 
    def validate(self, attrs):
        user = self.context['user']
        user.is_verified = True
        user.save()
        return attrs
    
# User Profile Update Serializer
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    biography = serializers.CharField(max_length=500, allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = ['','first_name', 'last_name', 'biography']

# User Public Info Serializer I have to move the public info serializer to user_network_api
class PrivateUserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    followed_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'biography', 'profile_picture', 'created_at', 'updated_at', 'is_verified', 'followers_count', 'followed_count']

    def get_followers_count(self, user):
        return Inspiration.objects.filter(followed=user).count()

    def get_followed_count(self, user):
        return Inspiration.objects.filter(follower=user).count()


class PublicUserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    followed_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'followers_count', 'followed_count']

    def get_followers_count(self, user):
        return Inspiration.objects.filter(followed=user).count()

    def get_followed_count(self, user):
        return Inspiration.objects.filter(follower=user).count()

class UpdateProfilePictureSerializer(serializers.ModelSerializer):
    #profile pic serializer UrlField
    profile_picture = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = User
        fields = ['profile_picture']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=16, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(max_length=16, write_only=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(max_length=16, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        #if old password is not correct then raise error
        if not self.context['user'].check_password(attrs['old_password']):
            raise serializers.ValidationError({"message": "Old password is not correct."})
        # Check if passwords match
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"message": "Password fields didn't match."})
       #if new password is same as old password then raise error
        if self.context['user'].check_password(attrs['new_password']):
            raise serializers.ValidationError({"message": "New password is same as old password."})
        return attrs



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()