"""Management API views for customer-facing management interface."""

from __future__ import annotations
from typing import Any
from django.contrib.auth import login
from django.db.models import QuerySet
from mgmt.models import Company
from mgmt.models import User
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet
from tracking.forms import CampaignSubAdminForm
from tracking.forms import TrackingSubAdminForm
from tracking.models import Campaign
from tracking.models import Tracking
from .serializers import CampaignSerializer
from .serializers import ImageRequestDataSerializer
from .serializers import RecipientSerializer
from .serializers import TrackingRequestDataSerializer
from .serializers import TrackingSerializer
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
        password = serializer.validated_data.pop("password", None)
        user = serializer.save()
        if password:
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


class RequestDataViewSet(GenericViewSet):
    """ViewSet for fetching individual request data details."""

    permission_classes = [IsAuthenticated]

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
    serializer_class = TrackingSerializer

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
