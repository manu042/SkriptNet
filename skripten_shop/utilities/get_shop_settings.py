from skripten_shop.models import ShopSettings


class ShopSettingsObject():
    shop_settings = ShopSettings.objects.get(pk=1)

    @classmethod
    def current_semester_is(self):
        return self.shop_settings.current_semester

    @classmethod
    def membership_fee_is(cls):
        return cls.shop_settings.membership_fee
