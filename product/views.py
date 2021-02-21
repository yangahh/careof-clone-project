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

        product = Product.objects.get(id=product_id)
        context = {}
        
        # goals & similar_products
        goals = product.goal.all()
        goal_list = []
        
        if goals:
            for goal in goals:
                goal_list.append(goal.name)

                # similar_products
                similar_products = goal.product_set.all()
            context['goal'] = goal_list

            


        # product
        context['id'] = product.id
        context['displayTitle'] = product.name
        context['subtitle'] = product.sub_name
        context['description'] = product.description
        context['nutritionUrl'] = product.nutrition_url
        context['isNew'] = product.is_new
        context['veganLevel'] = product.vegan_level  # 1: vegan 2: vegetarian 3: non-vegetarian
        
        # dietary_habits
        dietary_habits = product.dietary_habit.all()
        #dietary_habit_list = []
        if dietary_habits:
            dietary_habit_list = [dietary_habit.name for dietary_habit in dietary_habits]
            context['dietaryHabit'] = dietary_habit_list
        
        # allergies
        allergies = product.allergy.all()
        if allergies:
            allergy_list = [allergy.name for allergy in allergies]
            context['allergy'] = allergy_list
        
        # similar_products
        

