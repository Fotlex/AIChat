from django.contrib import admin

from ..models import Character, Conversation, LLMConfiguration, Message, User
from .character import CharacterAdmin
from .chat import ConversationAdmin, MessageAdmin
from .llm import LLMConfigurationAdmin
from .user import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(LLMConfiguration, LLMConfigurationAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
