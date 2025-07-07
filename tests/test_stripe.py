import os
import pytest
import stripe

def test_stripe_key_is_set():
    secret = os.environ.get("STRIPE_SECRET_KEY")
    assert secret, "STRIPE_SECRET_KEY n'est pas défini dans l'environnement"
    stripe.api_key = secret
    # Test simple : lister les produits (doit retourner une liste, même vide)
    products = stripe.Product.list(limit=1)
    assert isinstance(products.data, list)

def test_stripe_list_products():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    products = stripe.Product.list(limit=2)
    assert isinstance(products.data, list)

def test_stripe_list_prices():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    prices = stripe.Price.list(limit=2)
    assert isinstance(prices.data, list)