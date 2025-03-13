from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

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


class TagSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = Tag
        fields = ["id", "name", "color"]


class SocialProfileSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source="get_platform_display", read_only=True)

    class Meta:  # type: ignore
        model = SocialProfile
        fields = ["id", "platform", "platform_display", "url", "username", "created_at", "updated_at"]


class ActivitySerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.name", read_only=True)
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:  # type: ignore
        model = Activity
        fields = [
            "id",
            "content_type",
            "content_type_name",
            "object_id",
            "activity_type",
            "activity_type_display",
            "subject",
            "description",
            "start_date",
            "end_date",
            "due_date",
            "completion_date",
            "is_completed",
            "performed_by",
            "performed_by_name",
            "created_by",
            "created_by_name",
            "assigned_to",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class CustomFieldSerializer(serializers.ModelSerializer):
    field_type_display = serializers.CharField(source="get_field_type_display", read_only=True)
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:  # type: ignore
        model = CustomField
        fields = [
            "id",
            "name",
            "field_type",
            "field_type_display",
            "description",
            "content_type",
            "content_type_name",
            "choices",
            "is_required",
            "default_value",
            "created_at",
            "updated_at",
        ]


class CustomFieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="field.name", read_only=True)
    field_type = serializers.CharField(source="field.field_type", read_only=True)
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:  # type: ignore
        model = CustomFieldValue
        fields = [
            "id",
            "field",
            "field_name",
            "field_type",
            "content_type",
            "content_type_name",
            "object_id",
            "value",
            "created_at",
            "updated_at",
        ]


class ContactListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Contact objects when listed in Account serializer."""

    full_name = serializers.CharField(read_only=True)

    class Meta:  # type: ignore
        model = Contact
        fields = ["id", "first_name", "last_name", "full_name", "title", "email", "phone"]


class AccountListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Account objects when listed in Contact serializer."""

    account_type_display = serializers.CharField(source="get_account_type_display", read_only=True)
    industry_display = serializers.CharField(source="get_industry_display", read_only=True)

    class Meta:  # type: ignore
        model = Account
        fields = ["id", "name", "account_type", "account_type_display", "industry", "industry_display", "website"]


class AccountSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source="get_account_type_display", read_only=True)
    industry_display = serializers.CharField(source="get_industry_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    primary_contact_name = serializers.CharField(source="primary_contact.full_name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    contacts = ContactListSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    level = serializers.IntegerField(read_only=True)
    social_profiles = SocialProfileSerializer(many=True, read_only=True)

    class Meta:  # type: ignore
        model = Account
        fields = [
            "id",
            "name",
            "account_type",
            "account_type_display",
            "industry",
            "industry_display",
            "website",
            "parent",
            "parent_name",
            "level",
            "primary_contact",
            "primary_contact_name",
            "phone",
            "email",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "assigned_to",
            "assigned_to_name",
            "tags",
            "description",
            "annual_revenue",
            "employee_count",
            "contacts",
            "social_profiles",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "level"]


class ContactSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    account_details = AccountListSerializer(source="account", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source="parent.full_name", read_only=True)
    level = serializers.IntegerField(read_only=True)
    social_profiles = SocialProfileSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:  # type: ignore  # type: ignore
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "title",
            "parent",
            "parent_name",
            "level",
            "account",
            "account_details",
            "email",
            "phone",
            "mobile",
            "use_account_address",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "status",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "tags",
            "description",
            "date_of_birth",
            "email_opt_out",
            "phone_opt_out",
            "social_profiles",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "level", "full_name"]


class OpportunityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Opportunity objects when listed in other serializers."""

    stage_display = serializers.CharField(source="get_stage_display", read_only=True)

    class Meta:  # type: ignore # type: ignore
        model = Opportunity
        fields = ["id", "name", "stage", "stage_display", "amount", "probability", "expected_close_date"]


class OpportunitySerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    account_details = AccountListSerializer(source="account", read_only=True)
    primary_contact_details = ContactListSerializer(source="primary_contact", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:  # type: ignore
        model = Opportunity
        fields = [
            "id",
            "name",
            "account",
            "account_details",
            "primary_contact",
            "primary_contact_details",
            "stage",
            "stage_display",
            "amount",
            "probability",
            "expected_close_date",
            "next_step",
            "description",
            "assigned_to",
            "assigned_to_name",
            "tags",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


# Nested serializers for the 360° customer view
class AccountDetailSerializer(AccountSerializer):
    """Extended Account serializer that includes opportunities for 360° view."""

    opportunities = OpportunityListSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ["opportunities", "activities"]


class ContactDetailSerializer(ContactSerializer):
    """Extended Contact serializer that includes opportunities for 360° view."""

    opportunities = OpportunityListSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta(ContactSerializer.Meta):
        fields = ContactSerializer.Meta.fields + ["opportunities", "activities"]


# Content type serializer for working with generic relations
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:  # type: ignore
        model = ContentType
        fields = ["id", "app_label", "model"]


class CampaignSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:  # type: ignore
        model = Campaign
        fields = [
            "id",
            "name",
            "description",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "sent_count",
            "open_count",
            "click_count",
            "bounce_count",
            "unsubscribe_count",
            "assigned_to",
            "assigned_to_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "tags",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "sent_count",
            "open_count",
            "click_count",
            "bounce_count",
            "unsubscribe_count",
        ]


class SegmentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    static_contacts_count = serializers.SerializerMethodField()

    def get_static_contacts_count(self, obj):
        return obj.static_contacts.count()

    class Meta:  # type: ignore
        model = Segment
        fields = [
            "id",
            "name",
            "description",
            "criteria",
            "contact_count",
            "is_dynamic",
            "static_contacts",
            "static_contacts_count",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "contact_count"]


# Marketing Email Serializer (complete version)
class MarketingEmailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)

    class Meta:  # type: ignore
        model = MarketingEmail
        fields = [
            "id",
            "name",
            "subject",
            "html_content",
            "text_content",
            "campaign",
            "campaign_name",
            "sequence_order",
            "delay_days",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class CampaignRecipientSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    contact_name = serializers.CharField(source="contact.full_name", read_only=True)

    class Meta:  # type: ignore
        model = CampaignRecipient
        fields = [
            "id",
            "campaign",
            "campaign_name",
            "contact",
            "contact_name",
            "status",
            "status_display",
            "sent_at",
            "opened_at",
            "clicked_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class SupportTicketSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    contact_name = serializers.CharField(source="contact.full_name", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:  # type: ignore
        model = SupportTicket
        fields = [
            "id",
            "subject",
            "description",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "category",
            "contact",
            "contact_name",
            "account",
            "account_name",
            "assigned_to",
            "assigned_to_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "resolved_at",
            "due_by",
            "is_overdue",
            "tags",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "is_overdue"]


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    ticket_subject = serializers.CharField(source="ticket.subject", read_only=True)

    def get_sender_name(self, obj):
        if obj.is_customer:
            return "Customer"
        return obj.sender.name if obj.sender else "Unknown"

    class Meta:  # type: ignore
        model = TicketMessage
        fields = [
            "id",
            "ticket",
            "ticket_subject",
            "content",
            "is_customer",
            "sender",
            "sender_name",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class ReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    shared_with_count = serializers.SerializerMethodField()

    def get_shared_with_count(self, obj):
        return obj.shared_with.count()

    class Meta:  # type: ignore
        model = Report
        fields = [
            "id",
            "name",
            "description",
            "report_type",
            "report_type_display",
            "query_params",
            "chart_type",
            "display_columns",
            "filters",
            "sort_by",
            "sort_direction",
            "created_by",
            "created_by_name",
            "is_public",
            "shared_with",
            "shared_with_count",
            "schedule_enabled",
            "schedule_frequency",
            "schedule_recipients",
            "created_at",
            "updated_at",
            "last_run_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "last_run_at"]


class DashboardItemSerializer(serializers.ModelSerializer):
    report_name = serializers.CharField(source="report.name", read_only=True)
    dashboard_name = serializers.CharField(source="dashboard.name", read_only=True)

    class Meta:  # type: ignore
        model = DashboardItem
        fields = [
            "id",
            "dashboard",
            "dashboard_name",
            "report",
            "report_name",
            "position_x",
            "position_y",
            "width",
            "height",
            "custom_title",
        ]


class DashboardSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    items = DashboardItemSerializer(many=True, read_only=True)
    shared_with_count = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()

    def get_shared_with_count(self, obj):
        return obj.shared_with.count()

    def get_report_count(self, obj):
        return obj.reports.count()

    class Meta:  # type: ignore
        model = Dashboard
        fields = [
            "id",
            "name",
            "description",
            "layout",
            "reports",
            "created_by",
            "created_by_name",
            "is_public",
            "shared_with",
            "shared_with_count",
            "report_count",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]
