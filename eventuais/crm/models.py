import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

from eventuais.users.models import User


def validate_probability_range(p):
    if not (0 <= p <= 100):
        msg = "Probability must be between 0 and 100"
        raise ValidationError(msg)


class Tag(models.Model):
    """Tags for categorizing CRM objects."""

    name = models.CharField(_("Name"), max_length=100, unique=True)
    color = models.CharField(_("Color"), max_length=20, blank=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class Activity(models.Model):
    """Activity model for tracking interactions with contacts and accounts."""

    class ActivityType(models.TextChoices):
        CALL = "call", _("Call")
        EMAIL = "email", _("Email")
        MEETING = "meeting", _("Meeting")
        TASK = "task", _("Task")
        NOTE = "note", _("Note")
        OTHER = "other", _("Other")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Generic relation to allow activities to be associated with different models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    activity_type = models.CharField(_("Activity Type"), max_length=20, choices=ActivityType.choices)
    subject = models.CharField(_("Subject"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    # Date and time information
    start_date = models.DateTimeField(_("Start Date/Time"))
    end_date = models.DateTimeField(_("End Date/Time"), null=True, blank=True)

    # Task-specific fields
    due_date = models.DateTimeField(_("Due Date"), null=True, blank=True)
    completion_date = models.DateTimeField(_("Completion Date"), null=True, blank=True)
    is_completed = models.BooleanField(_("Is Completed"), default=False)

    # User who performed the activity
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="performed_activities")

    # User to whom the activity is assigned (for tasks)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_activities",
        verbose_name=_("Assigned To"),
    )

    # User who created the activity
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_activities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.activity_type}: {self.subject}"


class CustomField(models.Model):
    """Custom fields for extending entity models."""

    class FieldType(models.TextChoices):
        TEXT = "text", _("Text")
        TEXTAREA = "textarea", _("Text Area")
        NUMBER = "number", _("Number")
        DATE = "date", _("Date")
        DATETIME = "datetime", _("Date & Time")
        BOOLEAN = "boolean", _("Boolean")
        SELECT = "select", _("Select")
        MULTISELECT = "multiselect", _("Multi-Select")
        URL = "url", _("URL")
        EMAIL = "email", _("Email")
        PHONE = "phone", _("Phone")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Field Name"), max_length=100)
    field_type = models.CharField(_("Field Type"), max_length=20, choices=FieldType.choices)
    description = models.TextField(_("Description"), blank=True)

    # The content type this custom field is for (Account, Contact, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("Model"))

    # For select/multiselect fields
    choices = models.JSONField(
        _("Choices"),
        blank=True,
        null=True,
        help_text=_("JSON array of choices for select fields"),
    )

    is_required = models.BooleanField(_("Required"), default=False)
    default_value = models.TextField(_("Default Value"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()}) for {self.content_type.model}"

    class Meta:  # type: ignore
        verbose_name = _("Custom Field")
        verbose_name_plural = _("Custom Fields")
        unique_together = [["name", "content_type"]]


class CustomFieldValue(models.Model):
    """Values for custom fields on specific objects."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(
        CustomField,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("Custom Field"),
    )

    # Generic relation to the object this value belongs to
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    # The actual value of the custom field
    value = models.TextField(_("Value"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.field.name}: {self.value}"

    class Meta:  # type: ignore
        verbose_name = _("Custom Field Value")
        verbose_name_plural = _("Custom Field Values")
        unique_together = [["field", "content_type", "object_id"]]


class SocialProfile(models.Model):
    """Social media profiles for contacts and accounts."""

    class Platform(models.TextChoices):
        LINKEDIN = "linkedin", _("LinkedIn")
        TWITTER = "twitter", _("Twitter")
        FACEBOOK = "facebook", _("Facebook")
        INSTAGRAM = "instagram", _("Instagram")
        YOUTUBE = "youtube", _("YouTube")
        GITHUB = "github", _("GitHub")
        OTHER = "other", _("Other")

    # Generic relation to allow social profiles to be associated with different models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    platform = models.CharField(_("Platform"), max_length=20, choices=Platform.choices)
    url = models.URLField(_("Profile URL"))
    username = models.CharField(_("Username"), max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_platform_display()}: {self.username or self.url}"

    class Meta:  # type: ignore
        verbose_name = _("Social Profile")
        verbose_name_plural = _("Social Profiles")
        unique_together = [["content_type", "object_id", "platform"]]


class Account(MPTTModel):
    """Account model with hierarchical structure."""

    class AccountType(models.TextChoices):
        CUSTOMER = "customer", _("Customer")
        PARTNER = "partner", _("Partner")
        VENDOR = "vendor", _("Vendor")
        PROSPECT = "prospect", _("Prospect")
        COMPETITOR = "competitor", _("Competitor")
        OTHER = "other", _("Other")

    class Industry(models.TextChoices):
        TECHNOLOGY = "technology", _("Technology")
        FINANCE = "finance", _("Finance")
        HEALTHCARE = "healthcare", _("Healthcare")
        EDUCATION = "education", _("Education")
        MANUFACTURING = "manufacturing", _("Manufacturing")
        RETAIL = "retail", _("Retail")
        ENTERTAINMENT = "entertainment", _("Entertainment")
        OTHER = "other", _("Other")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Account Name"), max_length=255)
    account_type = models.CharField(
        _("Account Type"),
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CUSTOMER,
    )
    industry = models.CharField(_("Industry"), max_length=20, choices=Industry.choices, null=True, blank=True)
    website = models.URLField(_("Website"), blank=True)

    # Account hierarchy using MPTT
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent Account"),
    )

    # Primary contact person
    primary_contact = models.ForeignKey(
        "Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_for_accounts",
        verbose_name=_("Primary Contact"),
    )

    # Contact details
    phone = models.CharField(_("Phone"), max_length=30, blank=True)
    email = models.EmailField(_("Email"), blank=True)

    # Address fields
    address_line1 = models.CharField(_("Address Line 1"), max_length=255, blank=True)
    address_line2 = models.CharField(_("Address Line 2"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    state = models.CharField(_("State/Province"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)

    # Relationships
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_accounts",
        verbose_name=_("Account Owner"),
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="accounts")

    # Additional fields
    description = models.TextField(_("Description"), blank=True)
    annual_revenue = models.DecimalField(_("Annual Revenue"), max_digits=18, decimal_places=2, null=True, blank=True)
    employee_count = models.PositiveIntegerField(_("Number of Employees"), null=True, blank=True)

    # Activity tracking
    activities = GenericRelation(Activity)
    social_profiles = GenericRelation(SocialProfile)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_accounts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # MPTT-specific options
    class MPTTMeta:
        order_insertion_by = ["name"]

    # Regular Django model options
    class Meta:  # type: ignore
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Contact(MPTTModel):
    """Contact model with hierarchical structure."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")
        LEAD = "lead", _("Lead")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    title = models.CharField(_("Job Title"), max_length=100, blank=True)

    # Contact hierarchy using MPTT (e.g., manager-subordinate relationships)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subordinates",
        verbose_name=_("Reports To"),
    )

    # Account relationship
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts")

    # Contact details
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=30, blank=True)
    mobile = models.CharField(_("Mobile"), max_length=30, blank=True)

    # Address fields (can be same as account or different)
    use_account_address = models.BooleanField(_("Use Account Address"), default=True)
    address_line1 = models.CharField(_("Address Line 1"), max_length=255, blank=True)
    address_line2 = models.CharField(_("Address Line 2"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    state = models.CharField(_("State/Province"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)

    # Status and categorization
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.ACTIVE)

    # Relationships
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_contacts",
        verbose_name=_("Contact Owner"),
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="contacts")

    # Additional fields
    description = models.TextField(_("Description"), blank=True)
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)

    # Communication preferences
    email_opt_out = models.BooleanField(_("Email Opt-Out"), default=False)
    phone_opt_out = models.BooleanField(_("Phone Opt-Out"), default=False)

    # Activity tracking
    activities = GenericRelation(Activity)
    social_profiles = GenericRelation(SocialProfile)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_contacts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    # MPTT-specific options
    class MPTTMeta:
        order_insertion_by = ["last_name", "first_name"]

    # Regular Django model options
    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["email"]),
        ]


class Opportunity(models.Model):
    """Opportunity model for sales pipeline management."""

    class Stage(models.TextChoices):
        PROSPECTING = "prospecting", _("Prospecting")
        QUALIFICATION = "qualification", _("Qualification")
        NEEDS_ANALYSIS = "needs_analysis", _("Needs Analysis")
        VALUE_PROPOSITION = "value_proposition", _("Value Proposition")
        DECISION_MAKERS = "decision_makers", _("Decision Makers")
        PROPOSAL = "proposal", _("Proposal")
        NEGOTIATION = "negotiation", _("Negotiation")
        CLOSED_WON = "closed_won", _("Closed Won")
        CLOSED_LOST = "closed_lost", _("Closed Lost")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Opportunity Name"), max_length=255)

    # Relationships
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="opportunities",
        verbose_name=_("Account"),
    )

    primary_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
        verbose_name=_("Primary Contact"),
    )

    # Pipeline information
    stage = models.CharField(_("Stage"), max_length=30, choices=Stage.choices, default=Stage.PROSPECTING)

    amount = models.DecimalField(_("Amount"), max_digits=18, decimal_places=2, null=True, blank=True)

    probability = models.PositiveSmallIntegerField(
        _("Probability (%)"),
        default=0,
        validators=[validate_probability_range],
    )

    expected_close_date = models.DateField(_("Expected Close Date"))

    # Additional information
    next_step = models.CharField(_("Next Step"), max_length=255, blank=True)
    description = models.TextField(_("Description"), blank=True)

    # Ownership and categorization
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_opportunities",
        verbose_name=_("Opportunity Owner"),
    )

    tags = models.ManyToManyField(Tag, blank=True, related_name="opportunities")

    # Activity tracking
    activities = GenericRelation(Activity)

    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_opportunities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Opportunity")
        verbose_name_plural = _("Opportunities")
        ordering = ["-expected_close_date"]

    def __str__(self):
        return self.name


class Campaign(models.Model):
    """Marketing campaign model for automating outreach."""

    class CampaignStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        ACTIVE = "active", _("Active")
        PAUSED = "paused", _("Paused")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Campaign Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    # Campaign details
    status = models.CharField(_("Status"), max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT)
    start_date = models.DateTimeField(_("Start Date"), null=True, blank=True)
    end_date = models.DateTimeField(_("End Date"), null=True, blank=True)

    # Campaign metrics
    sent_count = models.PositiveIntegerField(_("Emails Sent"), default=0)
    open_count = models.PositiveIntegerField(_("Emails Opened"), default=0)
    click_count = models.PositiveIntegerField(_("Links Clicked"), default=0)
    bounce_count = models.PositiveIntegerField(_("Emails Bounced"), default=0)
    unsubscribe_count = models.PositiveIntegerField(_("Unsubscribes"), default=0)

    # Ownership and metadata
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_campaigns",
        verbose_name=_("Campaign Owner"),
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Tags
    tags = models.ManyToManyField(Tag, blank=True, related_name="campaigns")

    # Activity tracking
    activities = GenericRelation(Activity)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Segment(models.Model):
    """Audience segmentation model for targeted marketing."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Segment Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    # Segment criteria stored as JSON
    criteria = models.JSONField(_("Segment Criteria"), help_text=_("JSON definition of segment filters"))

    # Cached count of contacts matching this segment
    contact_count = models.PositiveIntegerField(_("Contact Count"), default=0)

    # Whether this segment updates dynamically or is static
    is_dynamic = models.BooleanField(
        _("Dynamic Segment"),
        default=True,
        help_text=_("If true, membership updates automatically based on criteria"),
    )

    # For static segments, store explicit members
    static_contacts = models.ManyToManyField(Contact, blank=True, related_name="static_segments")

    # Ownership and metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_segments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Segment")
        verbose_name_plural = _("Segments")
        ordering = ["name"]

    def __str__(self):
        return self.name


class MarketingEmail(models.Model):
    """Email template model for marketing campaigns."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Template Name"), max_length=255)
    subject = models.CharField(_("Email Subject"), max_length=255)

    # Email content
    html_content = models.TextField(_("HTML Content"))
    text_content = models.TextField(
        _("Text Content"),
        blank=True,
        help_text=_("Plain text version for email clients that don't support HTML"),
    )

    # Campaign association
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="emails")

    # Sequence position (for drip campaigns)
    sequence_order = models.PositiveSmallIntegerField(_("Sequence Order"), default=0)
    delay_days = models.PositiveSmallIntegerField(
        _("Delay (Days)"),
        default=0,
        help_text=_("Days to wait before sending this email"),
    )

    # Ownership and metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_email_templates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Marketing Email")
        verbose_name_plural = _("Marketing Emails")
        ordering = ["campaign", "sequence_order"]
        unique_together = [["campaign", "sequence_order"]]

    def __str__(self):
        return self.name


class CampaignRecipient(models.Model):
    """Tracks individual recipients in a campaign."""

    class RecipientStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        OPENED = "opened", _("Opened")
        CLICKED = "clicked", _("Clicked")
        BOUNCED = "bounced", _("Bounced")
        UNSUBSCRIBED = "unsubscribed", _("Unsubscribed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationships
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="recipients")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="campaign_interactions")

    # Status tracking
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=RecipientStatus.choices,
        default=RecipientStatus.PENDING,
    )

    # Engagement tracking
    sent_at = models.DateTimeField(_("Sent At"), null=True, blank=True)
    opened_at = models.DateTimeField(_("Opened At"), null=True, blank=True)
    clicked_at = models.DateTimeField(_("Clicked At"), null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore  # noqa: PGH003
        verbose_name = _("Campaign Recipient")
        verbose_name_plural = _("Campaign Recipients")
        unique_together = [["campaign", "contact"]]

    def __str__(self):
        return f"{self.id}"


class SupportTicket(models.Model):
    """Customer support ticket model for handling customer inquiries and issues."""

    class TicketStatus(models.TextChoices):
        NEW = "new", _("New")
        OPEN = "open", _("Open")
        PENDING = "pending", _("Pending")
        RESOLVED = "resolved", _("Resolved")
        CLOSED = "closed", _("Closed")

    class TicketPriority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(_("Subject"), max_length=255)
    description = models.TextField(_("Description"))

    # Ticket classification
    status = models.CharField(_("Status"), max_length=20, choices=TicketStatus.choices, default=TicketStatus.NEW)
    priority = models.CharField(
        _("Priority"),
        max_length=20,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
    )
    category = models.CharField(_("Category"), max_length=100, blank=True)

    # Relationships
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="support_tickets")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="support_tickets")

    # Support agent handling the ticket
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(_("Resolved At"), null=True, blank=True)

    # SLA tracking
    due_by = models.DateTimeField(_("Due By"), null=True, blank=True)
    is_overdue = models.BooleanField(_("Is Overdue"), default=False)

    # Tags
    tags = models.ManyToManyField(Tag, blank=True, related_name="support_tickets")

    # Activity tracking
    activities = GenericRelation(Activity)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Support Ticket")
        verbose_name_plural = _("Support Tickets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject}"


class TicketMessage(models.Model):
    """Individual messages within a support ticket conversation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")

    # Message content
    content = models.TextField(_("Message"))

    # Sender information
    is_customer = models.BooleanField(_("From Customer"), default=False)

    # User will be null for customer messages if they're not system users
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_messages")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:  # type: ignore
        verbose_name = _("Ticket Message")
        verbose_name_plural = _("Ticket Messages")
        ordering = ["created_at"]

    def __str__(self):
        prefix = "Customer" if self.is_customer else str(self.sender)
        return f"{prefix} message on {self.ticket}"


class Report(models.Model):
    """Customizable reports for CRM data analysis."""

    class ReportType(models.TextChoices):
        SALES = "sales", _("Sales Report")
        ACTIVITY = "activity", _("Activity Report")
        CONTACT = "contact", _("Contact Report")
        CAMPAIGN = "campaign", _("Campaign Performance")
        SUPPORT = "support", _("Support Analysis")
        CUSTOM = "custom", _("Custom Report")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Report Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    # Report configuration
    report_type = models.CharField(_("Report Type"), max_length=20, choices=ReportType.choices)

    # The actual query configuration as JSON
    query_params = models.JSONField(_("Query Parameters"), default=dict)

    # Display settings
    chart_type = models.CharField(_("Chart Type"), max_length=50, blank=True)
    display_columns = models.JSONField(_("Display Columns"), default=list)

    # Filters and sorting
    filters = models.JSONField(_("Filters"), default=list)
    sort_by = models.CharField(_("Sort By"), max_length=100, blank=True)
    sort_direction = models.CharField(
        _("Sort Direction"),
        max_length=4,
        default="desc",
        choices=[("asc", "Ascending"), ("desc", "Descending")],
    )

    # Ownership and sharing
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_reports")
    is_public = models.BooleanField(_("Public Report"), default=False)

    # Users who can view this report if not public
    shared_with = models.ManyToManyField(User, blank=True, related_name="shared_reports")

    # Scheduling
    schedule_enabled = models.BooleanField(_("Enable Scheduling"), default=False)
    schedule_frequency = models.CharField(_("Frequency"), max_length=50, blank=True)
    schedule_recipients = models.JSONField(_("Email Recipients"), default=list, blank=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run_at = models.DateTimeField(_("Last Run At"), null=True, blank=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Dashboard(models.Model):
    """Dashboards for displaying multiple reports and metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Dashboard Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    # Dashboard layout configuration
    layout = models.JSONField(_("Layout Configuration"), default=dict)

    # Reports included in this dashboard
    reports = models.ManyToManyField(Report, through="DashboardItem", related_name="dashboards")

    # Ownership and sharing
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_dashboards")
    is_public = models.BooleanField(_("Public Dashboard"), default=False)

    # Users who can view this dashboard if not public
    shared_with = models.ManyToManyField(User, blank=True, related_name="shared_dashboards")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Dashboard")
        verbose_name_plural = _("Dashboards")
        ordering = ["name"]

    def __str__(self):
        return self.name


class DashboardItem(models.Model):
    """Items displayed on a dashboard with position information."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="items")
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="dashboard_placements")

    # Position and size in the dashboard grid
    position_x = models.PositiveSmallIntegerField(_("X Position"))
    position_y = models.PositiveSmallIntegerField(_("Y Position"))
    width = models.PositiveSmallIntegerField(_("Width"), default=1)
    height = models.PositiveSmallIntegerField(_("Height"), default=1)

    # Custom title override
    custom_title = models.CharField(_("Custom Title"), max_length=255, blank=True)

    class Meta:  # type: ignore # noqa: PGH003
        verbose_name = _("Dashboard Item")
        verbose_name_plural = _("Dashboard Items")
        unique_together = [["dashboard", "position_x", "position_y"]]

    def __str__(self):
        return self.id
