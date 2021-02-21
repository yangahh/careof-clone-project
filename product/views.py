import json

from django.views import View
from django.http  import JsonResponse, HttpResponse

from .models import (
    Menu,
    Category,
    Product,
    Image,
    ProductStock,
    Disease,
    ProductDisease,
    Allergy,
    ProductAllergy,
    Goal,
    ProductGoal,
    DietaryHabit,
    ProductDietaryHabit,
)

class ProductDetailView(View):
    def get(self, request, product_id):
        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({'message': 'DOES_NOT_EXIST'}, status=404)

        product  = Product.objects.get(id=product_id)
        category = product.category.menu.name

        # is_vegan, is_vegeterian
        vegan_level = product.vegan_level_id
        if vegan_level == 1:
            is_vegan      = True
            is_vegeterian = False
        elif vegan_level == 2:
            is_vegan      = False
            is_vegeterian = True
        else:
            is_vegan      = False
            is_vegeterian = False

        # size, price
        product_SSPs = ProductStock.objects.filter(product=product)  # SSP: size, stock, price

        if category == 'vitamins':
            price      = product_SSPs[0].price   
            is_soldout = True if product_SSPs[0].stock == 0 else False 
        else:
            price = {
                product_SSPs[0].size : product_SSPs[0].price,
                product_SSPs[1].size : product_SSPs[1].price
            }
            is_soldout = {
                product_SSPs[0].size : True if product_SSPs[0].stock == 0 else False,
                product_SSPs[1].size : True if product_SSPs[1].stock == 0 else False,
            }
        
        # similar products
        similar_product_list = []
        goals_product        = product.goal.all()
        for goal_product in goals_product:
            similar_products = goal_product.product_set.exclude(id=product_id)

            for similar_product in similar_products:
                similar_product_info = {
                        'id'             : similar_product.id,
                        'title'          : similar_product.name,
                        'subTitle'       : similar_product.sub_name,
                        'imageUrl'       : similar_product.image_set.get(is_main=True).image_url,
                        'healthGoalList' : [goal.name for goal in similar_product.goal.all()]
                }
                similar_product_list.append(similar_product_info)
        
        context = {}
        context['category']            = category 
        context['productImageSrc']     = product.image_set.get(is_main=False).image_url
        context['productCardImageSrc'] = product.image_set.get(is_main=True).image_url
        context['isVegan']             = is_vegan
        context['isVegetarian']        = is_vegeterian
        context['healthGoalList']      = [goal.name for goal in product.goal.all()]
        context['title']               = product.name
        context['subTitle']            = product.sub_name
        context['description']         = product.description
        context['nutritionLink']       = product.nutrition_url
        context['allergyList']         = [allergy.name for allergy in product.allergy.all()]
        context['productPrice']        = price
        context['isSoldOut']           = is_soldout
        context['dietaryHabitList']    = [dietary_habit.name for dietary_habit in product.dietary_habit.all()]
        context['similarProduct']      = similar_product_list[:2] 

        return JsonResponse({"data": context, "message": "SUCCESS"}, status=200)
        
