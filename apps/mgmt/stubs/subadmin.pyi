from typing import Any
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union
from django.contrib import admin
from django.db.models import Model
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import URLPattern

T = TypeVar("T", bound=Model)

class SubAdmin(admin.ModelAdmin[T]):
    model: Type[T]
    subadmins: List[Type[admin.ModelAdmin[Any]]]

    def get_urls(self) -> List[URLPattern]: ...
    def get_subadmin_urls(self) -> List[URLPattern]: ...
    def get_subadmin_instances(self) -> List[admin.ModelAdmin[Any]]: ...
    def get_subadmin_queryset(self, request: HttpRequest) -> QuerySet[T]: ...
    def get_subadmin_queryset_for_model(
        self, request: HttpRequest, model: Type[Model]
    ) -> QuerySet[Model]: ...

class RootSubAdmin(admin.ModelAdmin[T]):
    model: Type[T]
    subadmins: List[Type[admin.ModelAdmin[Any]]]

    def get_urls(self) -> List[URLPattern]: ...
    def get_subadmin_urls(self) -> List[URLPattern]: ...
    def get_subadmin_instances(self) -> List[admin.ModelAdmin[Any]]: ...
    def get_subadmin_queryset(self, request: HttpRequest) -> QuerySet[T]: ...
    def get_subadmin_queryset_for_model(
        self, request: HttpRequest, model: Type[Model]
    ) -> QuerySet[Model]: ...
