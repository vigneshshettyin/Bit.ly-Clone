from .serializers import LinkSerializer, UserLoginSerializer, UserRegisterSerializer, LinkSerializerWithoutUser
from .models import Link
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner

User = get_user_model()


class LoginViewSet(viewsets.ViewSet):

    """
    A simple ViewSet for authenticating users and returning an auth token.

    """

    serializer_class = UserLoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.initial_data
        user = User.objects.filter(email=data['email']).first()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,
                         'created': created})


class RegisterViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating a new user and generating a token for them.

    """

    serializer_class = UserRegisterSerializer

    def get_tokens_for_user(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return {'token': token.key,
                'created': created}

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = self.get_tokens_for_user(user)
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)


class LinkViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for creating short links. User is taken as null, because we don't need to know who created the link.
    """

    serializer_class = LinkSerializerWithoutUser

    def create(self, request):
        if Link.objects.filter(long_url=request.data['long_url']).exists():
            link = Link.objects.get(long_url=request.data['long_url'])
            serializer = self.serializer_class(link)
            return Response(serializer.data)
        else:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

    # def list(self, request):
    #     links = Link.objects.all()
    #     serializer = self.serializer_class(links, many=True)
    #     return Response(serializer.data)


class Redirector(View):
    """
    A simple View which redirects to the long_url and increments the click count.
    """

    def get(self, request, short_code, *args, **kwargs):
        try:
            link = Link.objects.get(short_code=short_code)
            link.clicks += 1
            link.save()
            return redirect(link.long_url)
        except Link.DoesNotExist:
            return redirect('/')


class CreateViewEditLinkViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, creating, retrieving, updating and deleting links for authenticated users.
    """

    serializer_class = LinkSerializer

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Link.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        link = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(link)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        link = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(
            link, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        link = get_object_or_404(queryset, pk=pk)
        link.delete()
        return Response(status=204)
