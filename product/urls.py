from django.urls import path
from .views      import ProductDetailView, ProductToCartView 

urlpatterns = [
    path('/<int:product_id>', ProductDetailView.as_view()),
    path('/tocart', ProductToCartView.as_view()), 
]
