# Here we will put validation on the data

from rest_framework import serializers
from .models import User
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# LoginIn Serializer 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # after login for sending the details of user with token 
        data['user'] = {
            "id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "role": self.user.role,
            "slug": self.user.slug
        }
        return data

# Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'full_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def validate_role(self, value):
        #convert role to uppercase to prevent case senstivity error
        if value:
            return value.upper()
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''),
            role=validated_data.get('role', 'VIEWER'),
            is_active=False  # user created but status is inactive can't login because email is not verified 
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password','full_name','city','state','phone_number','role','slug','is_active']
        read_only_fields = ['slug','id']
        extra_kwargs = {
            'password': {'write_only':True, 'min_length':8}
        }
    
    # Validation For Phone Number
    def validate_phone_number(self,value):
        if value:
            if not re.match(r'^\+?1?\d{9,15}$', value):
                raise serializers.ValidationError("Phone Number ust be in Correct Format")
        return value
    
    # validation for Name 
    def validation_full_name(self,value):
        if value and len(value) < 3:
            raise serializers.ValidationError("Name should be atl least 3 character long ")
        
        return value
    
    # validation for role coming from frontend to convert it into upercase 
    def validate_role(self, value):
        if value:
            return value.upper()
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self,instance, validated_data):
        password = validated_data.pop('password',None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)