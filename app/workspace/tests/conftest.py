import pytest
from django.contrib.auth import get_user_model

from core.models import Team
from workspace.models import Workspace
from subscription.models import Subscription, Price, ProductFeature, Feature, Product, SubscriptionItem, StripeUser

User = get_user_model()


@pytest.fixture
def user():
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
    }
    user = User.objects.create_user(**user_data)
    stripe_user = StripeUser.objects.create(user=user, customer_id="test_customer")

    # Create features and link them to a product via ProductFeature model
    feature_data = {
        "max_workspaces": "max_workspaces__10",
        "max_users": "max_users__10",
        "max_socials": "max_socials__10",
    }
    product = Product.objects.create(product_id='product_id_1', active=True)

    for feature_id in feature_data.values():
        feature = Feature.objects.create(feature_id=feature_id)
        ProductFeature.objects.create(product=product, feature=feature)

    # Create a price for the product
    price = Price.objects.create(price_id='price_id_1', product=product, price=1000, active=True, currency='PLN')

    # Create a subscription for the user
    subscription = Subscription.objects.create(
        stripe_user=stripe_user,
        subscription_id="sub_test",
        status='active',
        cancel_at_period_end=False
    )

    # Create a subscription item
    SubscriptionItem.objects.create(subscription=subscription, price=price, quantity=1)

    return user


@pytest.fixture
def team(user):
    return Team.objects.create(name="Test Team", owner=user)


@pytest.fixture
def workspace(team):
    return Workspace.objects.create(name="Test Workspace", team=team)
