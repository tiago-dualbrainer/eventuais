from django.contrib import admin

from .models import Account
from .models import Activity
from .models import Campaign
from .models import CampaignRecipient
from .models import Contact
from .models import CustomField
from .models import CustomFieldValue
from .models import Dashboard
from .models import DashboardItem
from .models import MarketingEmail
from .models import Opportunity
from .models import Report
from .models import Segment
from .models import SocialProfile
from .models import SupportTicket
from .models import Tag
from .models import TicketMessage

admin.site.register(Account)
admin.site.register(Activity)
admin.site.register(Campaign)
admin.site.register(CampaignRecipient)
admin.site.register(Contact)
admin.site.register(CustomField)
admin.site.register(CustomFieldValue)
admin.site.register(Dashboard)
admin.site.register(DashboardItem)
admin.site.register(MarketingEmail)
admin.site.register(Opportunity)
admin.site.register(Report)
admin.site.register(Segment)
admin.site.register(SocialProfile)
admin.site.register(SupportTicket)
admin.site.register(Tag)
admin.site.register(TicketMessage)
