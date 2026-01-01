"""Management API views for customer-facing management interface."""

from __future__ import annotations
from typing import Any
from common.enums import TokenStatus
from django.contrib.auth import login
from django.db.models import QuerySet
from mgmt.models import Company
from mgmt.models import User
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet
from tracking.forms import CampaignSubAdminForm
from tracking.forms import TrackingSubAdminForm
from tracking.models import AbstractRequestData
from tracking.models import Campaign
from tracking.models import Token
from tracking.models import Tracking
from .serializers import CampaignSerializer
from .serializers import ImageRequestDataSerializer
from .serializers import RecipientSerializer
from .serializers import TokenSerializer
from .serializers import TrackingDetailSerializer
from .serializers import TrackingListSerializer
from .serializers import TrackingRequestDataSerializer
from .serializers import UserCreateSerializer
from .serializers import UserSerializer


class SignupViewSet(GenericViewSet):
    """ViewSet for user signup."""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def signup(self, request: Request) -> Response:
        """Create a new user account with company."""

        username = request.data.get("username")
        email = request.data.get("email")
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")
        company_name = request.data.get("company_name")

        if not all([username, email, password1, password2, company_name]):
            return Response(
                {"errors": {"__all__": ["All fields are required"]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user
        if (
            not isinstance(username, str)
            or not isinstance(email, str)
            or not isinstance(password1, str)
        ):
            return Response(
                {"errors": {"__all__": ["Invalid input types"]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )

        # Create or get company
        company, _ = Company.objects.get_or_create(name=company_name)
        user.company = company
        user.save()

        login(request, user)
        return Response(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "company": user.company.name if user.company else None,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserViewSet(ModelViewSet):
    """ViewSet for user management."""

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_queryset(self) -> QuerySet[User]:
        """Filter users by the current user's company."""
        if not isinstance(self.request.user, User):
            return User.objects.none()
        user: User = self.request.user
        if not user.company:
            return User.objects.none()
        return User.objects.filter(company=user.company)

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request: Request) -> Response:
        """Login a user using Django's authentication."""
        from django.contrib.auth.forms import AuthenticationForm
        from .serializers import UserSerializer

        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return Response(
                {
                    "success": True,
                    "user": UserSerializer(user).data,
                }
            )
        return Response(
            {"errors": form.errors, "success": False},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"])
    def logout(self, request: Request) -> Response:
        """Logout the current user."""
        from django.contrib.auth import logout

        logout(request)
        return Response({"success": True})

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        """Get the current user's information."""
        if not isinstance(request.user, User):
            return Response(
                {"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user: User = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def dashboard(self, request: Request) -> Response:
        """Get dashboard data for the current user."""
        if not isinstance(request.user, User):
            return Response(
                {"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user: User = request.user
        company_data = None
        if user.company:
            from .serializers import CompanySerializer

            company_data = CompanySerializer(user.company).data
        return Response(
            {
                "company": company_data or {"name": "No Company"},
            }
        )

    def perform_create(self, serializer: Any) -> None:
        """Set company and password when creating a user."""
        if isinstance(self.request.user, User):
            user: User = self.request.user
            if user.company:
                password = serializer.validated_data.pop("password", None)
                new_user = serializer.save(company=user.company)
                if password:
                    new_user.set_password(password)
                    new_user.save()

    def perform_update(self, serializer: Any) -> None:
        """Handle password update if provided."""
        from rest_framework.exceptions import ValidationError

        password = serializer.validated_data.pop("password", None)
        current_password = serializer.validated_data.pop("current_password", None)
        user = serializer.save()
        if password:
            # If current_password is provided, validate it
            if current_password:
                if not user.check_password(current_password):
                    raise ValidationError({"current_password": ["Current password is incorrect"]})
            user.set_password(password)
            user.save()


class CompanyViewSet(GenericViewSet):
    """ViewSet for company management."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "patch"])
    def me(self, request: Request) -> Response:
        """Get or update the current user's company information."""
        if not isinstance(request.user, User):
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        user: User = request.user
        if not user.company:
            return Response({"error": "User has no company"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "GET":
            from .serializers import CompanySerializer

            serializer = CompanySerializer(user.company)
            return Response(serializer.data)

        if request.method == "PATCH":
            from .serializers import CompanySerializer

            # Use serializer for PATCH requests (better for API)
            serializer = CompanySerializer(user.company, data=request.data, partial=True)
            if serializer.is_valid():
                company = serializer.save()
                return Response(CompanySerializer(company).data)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=["get", "post"])
    def edit(self, request: Request) -> Response:
        """Get or update company information (legacy endpoint)."""
        if not isinstance(request.user, User):
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        user: User = request.user
        if not user.company:
            return Response({"error": "User has no company"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "GET":
            from .serializers import CompanySerializer

            serializer = CompanySerializer(user.company)
            return Response(serializer.data)

        if request.method == "POST":
            from mgmt.forms import CompanyForm

            form = CompanyForm(request.data, instance=user.company)
            if form.is_valid():
                form.save()
                return Response({"success": True})
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RequestDataPagination(PageNumberPagination):
    """Custom pagination for request data with configurable page size."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class RequestDataViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    """ViewSet for fetching individual request data details and listing with pagination/filtering."""

    permission_classes = [IsAuthenticated]
    pagination_class = RequestDataPagination

    def _validate_request(
        self, request: Request, pk: str | None
    ) -> tuple[int | None, Response | None]:
        """Validate request and extract ID."""
        if not pk:
            return None, Response(
                {"error": "Request data ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            request_data_id_int = int(pk)
        except ValueError:
            return None, Response(
                {"error": "Invalid request data ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(request.user, User) or not request.user.company:
            return None, Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        return request_data_id_int, None

    def _get_tracking_request_data(self, request: Request, request_data_id: int) -> Response | None:
        """Try to get and serialize TrackingRequestData."""
        from tracking.models import TrackingRequestData

        try:
            tracking_obj = TrackingRequestData.objects.get(pk=request_data_id)
            if not isinstance(request.user, User) or not request.user.company:
                return None
            if tracking_obj.tracking.company != request.user.company:
                return None
            serializer = TrackingRequestDataSerializer(tracking_obj, context={"request": request})
            return Response(serializer.data)
        except TrackingRequestData.DoesNotExist:
            return None

    def _get_image_request_data(self, request: Request, request_data_id: int) -> Response | None:
        """Try to get and serialize ImageRequestData."""
        from tracking.models import ImageRequestData

        try:
            image_obj = ImageRequestData.objects.get(pk=request_data_id)
            if not isinstance(request.user, User) or not request.user.company:
                return None
            if image_obj.tracking.company != request.user.company:
                return None
            serializer = ImageRequestDataSerializer(image_obj, context={"request": request})
            return Response(serializer.data)
        except ImageRequestData.DoesNotExist:
            return None

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Get detailed request data by ID."""
        request_data_id, error_response = self._validate_request(request, pk)
        if error_response:
            return error_response

        if request_data_id is None:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        # Try TrackingRequestData first
        response = self._get_tracking_request_data(request, request_data_id)
        if response:
            return response

        # Try ImageRequestData
        response = self._get_image_request_data(request, request_data_id)
        if response:
            return response

        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def _get_base_queryset(self) -> QuerySet[AbstractRequestData] | None:
        """Get base queryset filtered by tracking ID and user's company."""
        from common.enums import CampaignDataType
        from tracking.models import ImageRequestData
        from tracking.models import TrackingRequestData

        if not isinstance(self.request.user, User) or not self.request.user.company:
            return None

        user: User = self.request.user
        tracking_id = self.request.query_params.get("tracking_id")

        if not tracking_id:
            return None

        try:
            tracking = Tracking.objects.get(pk=int(tracking_id), company=user.company)
        except (Tracking.DoesNotExist, ValueError):
            return None

        # Determine which model to query based on campaign type
        if tracking.campaign and tracking.campaign.campaign_type == CampaignDataType.PACKAGES.value:
            return TrackingRequestData.objects.filter(tracking=tracking)
        elif tracking.campaign and tracking.campaign.campaign_type == CampaignDataType.IMAGES.value:
            return ImageRequestData.objects.filter(tracking=tracking)
        return None

    def _apply_text_filters(
        self, queryset: QuerySet[AbstractRequestData]
    ) -> QuerySet[AbstractRequestData]:
        """Apply text-based filters to the queryset."""
        filters_map = {
            "data_type": "data_type",
            "http_method": "http_method",
            "ip_address": "ip_address__icontains",
            "os": "os__icontains",
            "browser": "browser__icontains",
            "platform": "platform__icontains",
            "locale": "locale__icontains",
        }

        for param_name, filter_field in filters_map.items():
            value = self.request.query_params.get(param_name)
            if value:
                queryset = queryset.filter(**{filter_field: value})

        return queryset

    def _apply_date_filter(
        self, queryset: QuerySet[AbstractRequestData], param_name: str, field_name: str
    ) -> QuerySet[AbstractRequestData]:
        """Apply date filter to the queryset."""
        date_value = self.request.query_params.get(param_name)
        if not date_value:
            return queryset

        from datetime import datetime
        from django.utils import timezone

        try:
            date_obj = datetime.strptime(date_value, "%Y-%m-%d").date()
            start_datetime = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(date_obj, datetime.max.time()))
            queryset = queryset.filter(
                **{f"{field_name}__gte": start_datetime, f"{field_name}__lte": end_datetime}
            )
        except (ValueError, TypeError):
            pass

        return queryset

    def _apply_ordering(
        self, queryset: QuerySet[AbstractRequestData]
    ) -> QuerySet[AbstractRequestData]:
        """Apply ordering to the queryset."""
        ordering = self.request.query_params.get("ordering")
        if ordering:
            return queryset.order_by(ordering)
        return queryset.order_by("-server_timestamp")

    def get_queryset(self) -> QuerySet[AbstractRequestData]:
        """Get request data queryset filtered by tracking ID and user's company."""
        from tracking.models import TrackingRequestData

        queryset = self._get_base_queryset()
        if queryset is None:
            return TrackingRequestData.objects.none()

        queryset = self._apply_text_filters(queryset)
        queryset = self._apply_date_filter(queryset, "server_timestamp", "server_timestamp")
        queryset = self._apply_date_filter(queryset, "client_time", "client_time")
        queryset = self._apply_ordering(queryset)

        return queryset

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Return appropriate serializer based on campaign type."""
        from common.enums import CampaignDataType
        from tracking.models import Tracking

        tracking_id = self.request.query_params.get("tracking_id")
        if tracking_id:
            try:
                tracking = Tracking.objects.get(pk=int(tracking_id))
                if (
                    tracking.campaign
                    and tracking.campaign.campaign_type == CampaignDataType.IMAGES.value
                ):
                    return ImageRequestDataSerializer
            except Tracking.DoesNotExist:
                pass

        return TrackingRequestDataSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """List request data with pagination and filtering."""
        queryset = self.get_queryset()

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecipientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet for recipient management."""

    permission_classes = [IsAuthenticated]
    serializer_class = RecipientSerializer

    def get_queryset(self) -> QuerySet:
        """Filter recipients by the current user's company."""
        from tracking.models import Recipient

        if not isinstance(self.request.user, User):
            return Recipient.objects.none()
        user: User = self.request.user
        if not user.company:
            return Recipient.objects.none()
        return Recipient.objects.filter(company=user.company)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a recipient using the form for validation."""
        from tracking.forms import RecipientSubAdminForm

        form = RecipientSubAdminForm(request.data)
        if form.is_valid():
            recipient = form.save(commit=False)
            if isinstance(request.user, User) and request.user.company:
                recipient.company = request.user.company
            recipient.save()
            form.save_m2m()  # Save tags
            serializer = self.get_serializer(recipient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update a recipient using the form for validation."""
        instance = self.get_object()
        from tracking.forms import RecipientSubAdminForm

        form = RecipientSubAdminForm(request.data, instance=instance)
        if form.is_valid():
            recipient = form.save(commit=False)
            # Ensure company is set correctly
            if isinstance(request.user, User) and request.user.company:
                recipient.company = request.user.company
            recipient.save()
            form.save_m2m()  # Save tags
            serializer = self.get_serializer(recipient)
            return Response(serializer.data)
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


class CampaignViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet for campaign management."""

    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer

    def get_queryset(self) -> QuerySet[Campaign]:
        """Filter campaigns by the current user's company."""
        if not isinstance(self.request.user, User):
            return Campaign.objects.none()
        user: User = self.request.user
        if not user.company:
            return Campaign.objects.none()
        return Campaign.objects.filter(company=user.company)

    def perform_create(self, serializer: Any) -> None:
        """Set company when creating a campaign."""
        if isinstance(self.request.user, User):
            user: User = self.request.user
            if user.company:
                serializer.save(company=user.company)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a campaign using the form for validation."""

        form = CampaignSubAdminForm(request.data)
        if form.is_valid():
            campaign = form.save(commit=False)
            if isinstance(request.user, User):
                user: User = request.user
                if user.company:
                    campaign.company = user.company
                    campaign.save()
                    serializer = self.get_serializer(campaign)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": "User has no company"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update a campaign using the form for validation."""
        instance = self.get_object()
        from tracking.forms import CampaignSubAdminForm

        # Create a mutable copy of request.data and ensure company is set
        data: Any = {}
        if hasattr(request.data, "copy") and hasattr(request.data, "_mutable"):
            # QueryDict-like object
            data = request.data.copy()
            data._mutable = True
        else:
            # Regular dict
            data = dict(request.data)

        if isinstance(request.user, User) and request.user.company:
            # Set company in data so form validation passes
            data["company"] = request.user.company.id

        form = CampaignSubAdminForm(data, instance=instance)
        if form.is_valid():
            campaign = form.save(commit=False)
            # Ensure company is set correctly
            if isinstance(request.user, User) and request.user.company:
                campaign.company = request.user.company
            campaign.save()
            serializer = self.get_serializer(campaign)
            return Response(serializer.data)
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


class TrackingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet for tracking management."""

    permission_classes = [IsAuthenticated]
    serializer_class = TrackingListSerializer

    def get_serializer_class(self) -> type[Any]:
        """Return different serializers for list vs detail views."""
        if self.action == "retrieve":
            return TrackingDetailSerializer
        return TrackingListSerializer

    def get_queryset(self) -> QuerySet[Tracking]:
        """Filter tracking records by the current user's company."""
        if not isinstance(self.request.user, User):
            return Tracking.objects.none()
        user: User = self.request.user
        if not user.company:
            return Tracking.objects.none()
        return (
            Tracking.objects.filter(company=user.company)
            .select_related("campaign", "recipient")
            .prefetch_related("tokens")
        )

    def perform_create(self, serializer: Any) -> None:
        """Set company when creating a tracking record."""
        if isinstance(self.request.user, User):
            user: User = self.request.user
            if user.company:
                serializer.save(company=user.company)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a tracking record using the form for validation."""
        from tracking.forms import TrackingSubAdminForm

        form = TrackingSubAdminForm(request.data)
        if form.is_valid():
            tracking = form.save(commit=False)
            if isinstance(request.user, User):
                user: User = request.user
                if user.company:
                    tracking.company = user.company
                    # Validate campaign and recipient belong to company
                    if tracking.campaign.company != user.company:
                        return Response(
                            {"error": "Campaign does not belong to your company"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if tracking.recipient.company != user.company:
                        return Response(
                            {"error": "Recipient does not belong to your company"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    tracking.save()
                    serializer = self.get_serializer(tracking)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": "User has no company"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update a tracking record using the form for validation."""
        instance = self.get_object()

        form = TrackingSubAdminForm(request.data, instance=instance)
        if form.is_valid():
            if isinstance(request.user, User):
                user: User = request.user
                # Validate campaign and recipient belong to company
                if form.cleaned_data["campaign"].company != user.company:
                    return Response(
                        {"error": "Campaign does not belong to your company"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if form.cleaned_data["recipient"].company != user.company:
                    return Response(
                        {"error": "Recipient does not belong to your company"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            tracking = form.save()
            serializer = self.get_serializer(tracking)
            return Response(serializer.data)
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


class TokenPagination(PageNumberPagination):
    """Custom pagination for tokens with configurable page size."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class TokenViewSet(mixins.ListModelMixin, GenericViewSet):
    """ViewSet for token management."""

    permission_classes = [IsAuthenticated]
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    pagination_class = TokenPagination

    def get_queryset(self) -> QuerySet[Token]:
        """Filter tokens by the current user's company and optionally by tracking_id."""
        if not isinstance(self.request.user, User):
            return Token.objects.none()
        user: User = self.request.user
        if not user.company:
            return Token.objects.none()

        queryset = Token.objects.filter(tracking__company=user.company).select_related("tracking")

        # Filter by tracking_id if provided
        tracking_id = self.request.query_params.get("tracking_id")
        if tracking_id:
            try:
                queryset = queryset.filter(tracking_id=int(tracking_id))
            except (ValueError, TypeError):
                pass

        return queryset

    @action(detail=True, methods=["post"])
    def disable(self, request: Request, pk: int) -> Response:
        """Disable a token by setting its status to inactive."""
        token = self.get_object()
        token.status = TokenStatus.INACTIVE.value
        token.save(update_fields=["status"])
        from .serializers import TokenSerializer

        return Response(TokenSerializer(token).data)

    @action(detail=True, methods=["post"])
    def reactivate(self, request: Request, pk: int) -> Response:
        """Reactivate a token by setting its status to active."""
        token = self.get_object()
        token.status = TokenStatus.ACTIVE.value
        token.deleted_on = None
        token.save(update_fields=["status", "deleted_on"])
        from .serializers import TokenSerializer

        return Response(TokenSerializer(token).data)

    @action(detail=False, methods=["post"])
    def create_token(self, request: Request) -> Response:
        """Create a new token for a tracking record."""
        tracking_id = request.data.get("tracking_id")
        if not tracking_id:
            return Response(
                {"error": "tracking_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tracking = Tracking.objects.get(id=tracking_id)
        except Tracking.DoesNotExist:
            return Response(
                {"error": "Tracking record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify tracking belongs to user's company
        if not isinstance(request.user, User):
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user: User = request.user
        if not user.company or tracking.company != user.company:
            return Response(
                {"error": "Tracking record does not belong to your company"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate a unique token value
        import secrets

        token_value = secrets.token_urlsafe(32)

        # Ensure uniqueness
        while Token.objects.filter(value=token_value).exists():
            token_value = secrets.token_urlsafe(32)

        token = Token.objects.create(
            tracking=tracking,
            value=token_value,
            status=TokenStatus.ACTIVE.value,
        )

        from .serializers import TokenSerializer

        return Response(TokenSerializer(token).data, status=status.HTTP_201_CREATED)
