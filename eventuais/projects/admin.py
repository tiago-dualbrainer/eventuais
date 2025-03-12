from django.contrib import admin

from .models import Comment
from .models import Crew
from .models import Equipment
from .models import Project
from .models import ProjectResourceAllocation
from .models import Task
from .models import Transportation

admin.site.register(Project)
admin.site.register(Equipment)
admin.site.register(Crew)
admin.site.register(Transportation)
admin.site.register(ProjectResourceAllocation)
admin.site.register(Task)
admin.site.register(Comment)
