import pytest
from django.db import transaction

from ..models import Profile, User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "create_func,exp_staff,exp_superuser,exp_is_active",
    [
        [User.objects.create_user, False, False, False],
        [User.objects.create_superuser, True, True, True],
    ],
)
@pytest.mark.parametrize("password", [None, "pass"])
def test_create_user(create_func, exp_staff, exp_superuser, exp_is_active, password):
    username = "user1"
    email = "user@example.com"
    name = "Jane Doe"

    with transaction.atomic():
        user = create_func(username, email=email, name=name, password=password)

    assert user.username == username
    assert user.email == email
    assert user.name == name
    assert user.get_full_name() == name
    assert user.is_staff is exp_staff
    assert user.is_superuser is exp_superuser
    assert user.is_active is exp_is_active

    if password is not None:
        assert user.check_password(password)

    assert Profile.objects.filter(user=user).exists()
