from django.contrib import admin

from ..models import (
    Character,
    Conversation,
    LLMConfiguration,
    MainButton,
    Message,
    OtherButton,
    Promocode,
    PromocodeUsage,
    Referral,
    Tariff,
    Transaction,
    User,
)
from .button import MainButtonAdmin, OtherButtonAdmin
from .character import CharacterAdmin
from .chat import ConversationAdmin, MessageAdmin
from .llm import LLMConfigurationAdmin
from .payment import TariffAdmin, TransactionAdmin
from .promocode import PromocodeAdmin, PromocodeUsageAdmin
from .referral import ReferralAdmin
from .user import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Referral, ReferralAdmin)
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
