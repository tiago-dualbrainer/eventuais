from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from eventuais.crm.models import Account
from eventuais.crm.models import Activity
from eventuais.crm.models import Campaign
from eventuais.crm.models import CampaignRecipient
from eventuais.crm.models import Contact
from eventuais.crm.models import CustomField
from eventuais.crm.models import CustomFieldValue
from eventuais.crm.models import Dashboard
from eventuais.crm.models import DashboardItem
from eventuais.crm.models import MarketingEmail
from eventuais.crm.models import Opportunity
from eventuais.crm.models import Report
from eventuais.crm.models import Segment
from eventuais.crm.models import SocialProfile
from eventuais.crm.models import SupportTicket
from eventuais.crm.models import Tag
from eventuais.crm.models import TicketMessage

from .serializers import AccountDetailSerializer
from .serializers import AccountSerializer
from .serializers import ActivitySerializer
from .serializers import CampaignRecipientSerializer
from .serializers import CampaignSerializer
from .serializers import ContactDetailSerializer
from .serializers import ContactListSerializer
from .serializers import ContactSerializer
from .serializers import ContentTypeSerializer
from .serializers import CustomFieldSerializer
from .serializers import CustomFieldValueSerializer
from .serializers import DashboardItemSerializer
from .serializers import DashboardSerializer
from .serializers import MarketingEmailSerializer
from .serializers import OpportunityListSerializer
from .serializers import OpportunitySerializer
from .serializers import ReportSerializer
from .serializers import SegmentSerializer
from .serializers import SocialProfileSerializer
from .serializers import SupportTicketSerializer
from .serializers import TagSerializer
from .serializers import TicketMessageSerializer


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Activities."""

    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["activity_type", "is_completed", "created_by", "assigned_to"]
    search_fields = ["subject", "description"]
    ordering_fields = ["due_date", "created_at", "completion_date"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["GET"])
    def my_activities(self, request):
        """Return activities assigned to the current user."""
        activities = self.queryset.filter(assigned_to=request.user)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def overdue(self, request):
        """Return overdue activities."""
        from django.utils import timezone

        activities = self.queryset.filter(due_date__lt=timezone.now(), is_completed=False)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class CustomFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Custom Fields."""

    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["field_type", "is_required", "content_type"]
    search_fields = ["name", "description"]

    @action(detail=False, methods=["GET"])
    def for_model(self, request):
        """Get custom fields for a specific model."""
        model_name = request.query_params.get("model")
        app_label = request.query_params.get("app_label", "eventuais.crm")

        if not model_name:
            return Response({"error": "model parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            fields = self.queryset.filter(content_type=content_type)
            serializer = self.get_serializer(fields, many=True)
            return Response(serializer.data)
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Model {model_name} not found in app {app_label}"}, status=status.HTTP_404_NOT_FOUND
            )


class CustomFieldValueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Custom Field Values."""

    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["field", "content_type"]

    @action(detail=False, methods=["GET"])
    def for_object(self, request):
        """Get custom field values for a specific object."""
        object_id = request.query_params.get("object_id")
        content_type_id = request.query_params.get("content_type_id")

        if not object_id or not content_type_id:
            return Response(
                {"error": "object_id and content_type_id parameters are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            values = self.queryset.filter(object_id=object_id, content_type_id=content_type_id)
            serializer = self.get_serializer(values, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Social Profiles."""

    queryset = SocialProfile.objects.all()
    serializer_class = SocialProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["platform", "content_type"]
    search_fields = ["username", "url"]


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Accounts."""

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["account_type", "industry", "assigned_to", "tags"]
    search_fields = ["name", "description", "email", "phone", "city", "country"]
    ordering_fields = ["name", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve" and self.request.query_params.get("detailed", False):
            return AccountDetailSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["GET"])
    def my_accounts(self, request):
        """Return accounts assigned to the current user."""
        accounts = self.queryset.filter(assigned_to=request.user)
        page = self.paginate_queryset(accounts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def contacts(self, request, pk=None):
        """Return contacts for a specific account."""
        account = self.get_object()
        contacts = account.contacts.all()
        page = self.paginate_queryset(contacts)
        if page is not None:
            serializer = ContactListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ContactListSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def opportunities(self, request, pk=None):
        """Return opportunities for a specific account."""
        account = self.get_object()
        opportunities = account.opportunities.all()
        page = self.paginate_queryset(opportunities)
        if page is not None:
            serializer = OpportunityListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OpportunityListSerializer(opportunities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def activities(self, request, pk=None):
        """Return activities for a specific account."""
        account = self.get_object()
        content_type = ContentType.objects.get_for_model(Account)
        activities = Activity.objects.filter(content_type=content_type, object_id=account.id)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Contacts."""

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "account", "assigned_to", "tags"]
    search_fields = ["first_name", "last_name", "email", "phone", "mobile", "city", "country", "description"]
    ordering_fields = ["last_name", "first_name", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve" and self.request.query_params.get("detailed", False):
            return ContactDetailSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["GET"])
    def my_contacts(self, request):
        """Return contacts assigned to the current user."""
        contacts = self.queryset.filter(assigned_to=request.user)
        page = self.paginate_queryset(contacts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def opportunities(self, request, pk=None):
        """Return opportunities where this contact is the primary contact."""
        contact = self.get_object()
        opportunities = contact.opportunities.all()
        page = self.paginate_queryset(opportunities)
        if page is not None:
            serializer = OpportunityListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OpportunityListSerializer(opportunities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def activities(self, request, pk=None):
        """Return activities for a specific contact."""
        contact = self.get_object()
        content_type = ContentType.objects.get_for_model(Contact)
        activities = Activity.objects.filter(content_type=content_type, object_id=contact.id)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class OpportunityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Opportunities."""

    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["stage", "account", "primary_contact", "assigned_to", "tags"]
    search_fields = ["name", "description", "next_step"]
    ordering_fields = ["expected_close_date", "amount", "probability", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["GET"])
    def my_opportunities(self, request):
        """Return opportunities assigned to the current user."""
        opportunities = self.queryset.filter(assigned_to=request.user)
        page = self.paginate_queryset(opportunities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(opportunities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def pipeline(self, request):
        """Return aggregated pipeline data by stage."""
        from django.db.models import Sum, Count, Avg

        pipeline_data = (
            self.queryset.values("stage")
            .annotate(
                count=Count("id"),
                total_amount=Sum("amount"),
                avg_amount=Avg("amount"),
                avg_probability=Avg("probability"),
            )
            .order_by("stage")
        )

        return Response(pipeline_data)

    @action(detail=True, methods=["GET"])
    def activities(self, request, pk=None):
        """Return activities for a specific opportunity."""
        opportunity = self.get_object()
        content_type = ContentType.objects.get_for_model(Opportunity)
        activities = Activity.objects.filter(content_type=content_type, object_id=opportunity.id)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing available content types."""

    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["app_label", "model"]
    search_fields = ["app_label", "model"]

    @action(detail=False, methods=["GET"])
    def crm_models(self, request):
        """Return only content types for CRM models."""
        crm_content_types = self.queryset.filter(app_label="eventuais.crm")
        serializer = self.get_serializer(crm_content_types, many=True)
        return Response(serializer.data)


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Campaigns."""

    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "assigned_to", "tags"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["GET"])
    def my_campaigns(self, request):
        """Return campaigns assigned to the current user."""
        campaigns = self.queryset.filter(assigned_to=request.user)
        page = self.paginate_queryset(campaigns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def emails(self, request, pk=None):
        """Return emails for a specific campaign."""
        campaign = self.get_object()
        emails = campaign.emails.all()
        page = self.paginate_queryset(emails)
        if page is not None:
            serializer = MarketingEmailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MarketingEmailSerializer(emails, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def recipients(self, request, pk=None):
        """Return recipients for a specific campaign."""
        campaign = self.get_object()
        recipients = campaign.recipients.all()
        page = self.paginate_queryset(recipients)
        if page is not None:
            serializer = CampaignRecipientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CampaignRecipientSerializer(recipients, many=True)
        return Response(serializer.data)


class MarketingEmailViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Marketing Emails."""

    queryset = MarketingEmail.objects.all()
    serializer_class = MarketingEmailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["campaign", "sequence_order"]
    search_fields = ["name", "subject", "html_content", "text_content"]
    ordering_fields = ["campaign", "sequence_order", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["GET"])
    def by_campaign(self, request):
        """Filter emails by campaign."""
        campaign_id = request.query_params.get("campaign_id")
        if not campaign_id:
            return Response({"error": "campaign_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        emails = self.queryset.filter(campaign_id=campaign_id).order_by("sequence_order")
        page = self.paginate_queryset(emails)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(emails, many=True)
        return Response(serializer.data)


class CampaignRecipientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Campaign Recipients."""

    queryset = CampaignRecipient.objects.all()
    serializer_class = CampaignRecipientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["campaign", "contact", "status"]
    search_fields = ["contact__first_name", "contact__last_name", "contact__email"]
    ordering_fields = ["status", "sent_at", "opened_at", "clicked_at", "created_at"]

    @action(detail=False, methods=["POST"])
    def add_contacts(self, request):
        """Add multiple contacts to a campaign."""
        campaign_id = request.data.get("campaign_id")
        contact_ids = request.data.get("contact_ids", [])

        if not campaign_id:
            return Response({"error": "campaign_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not contact_ids:
            return Response({"error": "contact_ids list is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            campaign = Campaign.objects.get(id=campaign_id)
            created_count = 0
            existing_count = 0

            for contact_id in contact_ids:
                try:
                    contact = Contact.objects.get(id=contact_id)
                    _, created = CampaignRecipient.objects.get_or_create(
                        campaign=campaign,
                        contact=contact,
                        defaults={"status": CampaignRecipient.RecipientStatus.PENDING},
                    )
                    if created:
                        created_count += 1
                    else:
                        existing_count += 1
                except Contact.DoesNotExist:
                    continue

            return Response(
                {
                    "message": f"Added {created_count} contacts to campaign. {existing_count} were already recipients.",
                    "added": created_count,
                    "existing": existing_count,
                }
            )
        except Campaign.DoesNotExist:
            return Response({"error": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SegmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Segments."""

    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_dynamic", "created_by"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "contact_count", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["GET"])
    def contacts(self, request, pk=None):
        """Return contacts in this segment."""
        segment = self.get_object()

        # For static segments, use the explicit contacts
        if not segment.is_dynamic:
            contacts = segment.static_contacts.all()
        else:
            # For dynamic segments, we'd execute the criteria logic
            # This is a placeholder - in a real app you'd process the criteria JSON
            # to build a dynamic query
            contacts = Contact.objects.none()

        page = self.paginate_queryset(contacts)
        if page is not None:
            serializer = ContactListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ContactListSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_contacts(self, request, pk=None):
        """Add contacts to a static segment."""
        segment = self.get_object()
        contact_ids = request.data.get("contact_ids", [])

        if segment.is_dynamic:
            return Response(
                {"error": "Cannot manually add contacts to a dynamic segment"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not contact_ids:
            return Response({"error": "contact_ids list is required"}, status=status.HTTP_400_BAD_REQUEST)

        added_count = 0
        for contact_id in contact_ids:
            try:
                contact = Contact.objects.get(id=contact_id)
                segment.static_contacts.add(contact)
                added_count += 1
            except Contact.DoesNotExist:
                continue

        # Update the contact count
        segment.contact_count = segment.static_contacts.count()
        segment.save()

        return Response(
            {
                "message": f"Added {added_count} contacts to segment.",
                "added": added_count,
            }
        )

    @action(detail=True, methods=["POST"])
    def remove_contacts(self, request, pk=None):
        """Remove contacts from a static segment."""
        segment = self.get_object()
        contact_ids = request.data.get("contact_ids", [])

        if segment.is_dynamic:
            return Response(
                {"error": "Cannot manually remove contacts from a dynamic segment"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not contact_ids:
            return Response({"error": "contact_ids list is required"}, status=status.HTTP_400_BAD_REQUEST)

        removed_count = 0
        for contact_id in contact_ids:
            try:
                contact = Contact.objects.get(id=contact_id)
                if contact in segment.static_contacts.all():
                    segment.static_contacts.remove(contact)
                    removed_count += 1
            except Contact.DoesNotExist:
                continue

        # Update the contact count
        segment.contact_count = segment.static_contacts.count()
        segment.save()

        return Response(
            {
                "message": f"Removed {removed_count} contacts from segment.",
                "removed": removed_count,
            }
        )


class SupportTicketViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Support Tickets."""

    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "category", "contact", "account", "assigned_to", "is_overdue", "tags"]
    search_fields = ["subject", "description", "category"]
    ordering_fields = ["created_at", "updated_at", "due_by", "resolved_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["GET"])
    def my_tickets(self, request):
        """Return tickets assigned to the current user."""
        tickets = self.queryset.filter(assigned_to=request.user)
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def messages(self, request, pk=None):
        """Return messages for a specific ticket."""
        ticket = self.get_object()
        messages = ticket.messages.all().order_by("created_at")
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = TicketMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TicketMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_message(self, request, pk=None):
        """Add a message to a ticket."""
        ticket = self.get_object()
        content = request.data.get("content")
        is_customer = request.data.get("is_customer", False)

        if not content:
            return Response({"error": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

        message = TicketMessage.objects.create(
            ticket=ticket, content=content, is_customer=is_customer, sender=None if is_customer else request.user
        )

        # Update the ticket's updated_at timestamp
        ticket.save(update_fields=["updated_at"])

        serializer = TicketMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def change_status(self, request, pk=None):
        """Change the status of a ticket."""
        ticket = self.get_object()
        status_value = request.data.get("status")

        if not status_value:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        if status_value not in dict(SupportTicket.TicketStatus.choices):
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        # If resolving the ticket, set the resolved_at timestamp
        if status_value == SupportTicket.TicketStatus.RESOLVED and ticket.status != SupportTicket.TicketStatus.RESOLVED:
            from django.utils import timezone

            ticket.resolved_at = timezone.now()

        ticket.status = status_value
        ticket.save()

        serializer = self.get_serializer(ticket)
        return Response(serializer.data)


class TicketMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ticket Messages."""

    queryset = TicketMessage.objects.all()
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["ticket", "is_customer", "sender"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        # For non-customer messages, set the sender to the current user
        if not serializer.validated_data.get("is_customer", False):
            serializer.save(sender=self.request.user)
        else:
            serializer.save()

        # Update the related ticket's updated_at timestamp
        ticket = serializer.instance.ticket
        ticket.save(update_fields=["updated_at"])


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Reports."""

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["report_type", "created_by", "is_public", "schedule_enabled"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "last_run_at"]

    def get_queryset(self):
        """Return reports that the user has access to."""
        user = self.request.user
        # Include reports that are public, created by the user, or shared with the user
        return Report.objects.filter(
            models.Q(is_public=True) | models.Q(created_by=user) | models.Q(shared_with=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["POST"])
    def run_report(self, request, pk=None):
        """Execute the report and return the results."""
        report = self.get_object()

        # In a real implementation, you would process the report's query_params here
        # This is a placeholder - in production, you'd execute the actual query
        # based on the report configuration

        # Update the last_run_at timestamp
        from django.utils import timezone

        report.last_run_at = timezone.now()
        report.save(update_fields=["last_run_at"])

        # Return mock results
        return Response(
            {
                "report_id": str(report.id),
                "report_name": report.name,
                "executed_at": report.last_run_at,
                "results": {
                    "data": [],  # This would contain the actual query results
                    "count": 0,
                },
            }
        )

    @action(detail=True, methods=["POST"])
    def share(self, request, pk=None):
        """Share a report with specified users."""
        report = self.get_object()
        user_ids = request.data.get("user_ids", [])

        if not user_ids:
            return Response({"error": "user_ids list is required"}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model

        User = get_user_model()

        added_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                report.shared_with.add(user)
                added_count += 1
            except User.DoesNotExist:
                continue

        return Response(
            {"message": f"Shared report with {added_count} users.", "shared_with_count": report.shared_with.count()}
        )


class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Dashboards."""

    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["created_by", "is_public"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        """Return dashboards that the user has access to."""
        user = self.request.user
        # Include dashboards that are public, created by the user, or shared with the user
        return Dashboard.objects.filter(
            models.Q(is_public=True) | models.Q(created_by=user) | models.Q(shared_with=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["POST"])
    def share(self, request, pk=None):
        """Share a dashboard with specified users."""
        dashboard = self.get_object()
        user_ids = request.data.get("user_ids", [])

        if not user_ids:
            return Response({"error": "user_ids list is required"}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model

        User = get_user_model()

        added_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                dashboard.shared_with.add(user)
                added_count += 1
            except User.DoesNotExist:
                continue

        return Response(
            {
                "message": f"Shared dashboard with {added_count} users.",
                "shared_with_count": dashboard.shared_with.count(),
            }
        )


class DashboardItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Dashboard Items."""

    queryset = DashboardItem.objects.all()
    serializer_class = DashboardItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["dashboard", "report"]

    def get_queryset(self):
        """Only return dashboard items for dashboards the user can access."""
        user = self.request.user
        accessible_dashboards = Dashboard.objects.filter(
            models.Q(is_public=True) | models.Q(created_by=user) | models.Q(shared_with=user)
        ).values_list("id", flat=True)

        return DashboardItem.objects.filter(dashboard_id__in=accessible_dashboards)
