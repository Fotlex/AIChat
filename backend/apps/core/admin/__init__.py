from django.contrib import admin

from ..models import Character, Conversation, LLMConfiguration, Message, User, Tariff, Transaction, Promocode, PromocodeUsage, MainButton, OtherButton
from .character import CharacterAdmin
from .chat import ConversationAdmin, MessageAdmin
from .llm import LLMConfigurationAdmin
from .user import UserAdmin
from .payment import TariffAdmin, TransactionAdmin
from .promocode import PromocodeAdmin, PromocodeUsageAdmin
from .button import MainButtonAdmin, OtherButtonAdmin


admin.site.register(User, UserAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(LLMConfiguration, LLMConfigurationAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(PromocodeUsage, PromocodeUsageAdmin)
admin.site.register(MainButton, MainButtonAdmin)
admin.site.register(OtherButton, OtherButtonAdmin)
