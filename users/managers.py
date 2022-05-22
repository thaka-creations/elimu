from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, is_staff, password=None):
        if not username:
            pass

        user = self.model(
            username=username,
            is_staff=is_staff
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username=username,
            is_staff=True,
            password=password
        )

        user.is_admin = True
        user.is_active = True
        user.account_status = "ACTIVE"
        user.save(using=self._db)
        return user
