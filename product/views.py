import json
from datetime     import datetime
from random       import randint

from django.views import View
from django.http  import JsonResponse, HttpResponse

from user.utils   import login_decorator
from order.models import Order, OrderProductStock
from .models      import (
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

        # size, price, is_soldout
        product_SSPs = ProductStock.objects.filter(product=product)  # SSP: size, stock, price
        size = [product_SSP.size for product_SSP in product_SSPs]
        if category == 'vitamins':
            price          = product_SSPs[0].price   
            is_soldout     = bool(product_SSPs[0].stock == 0)
        else:
            price = {
                product_SSPs[0].size : product_SSPs[0].price,
                product_SSPs[1].size : product_SSPs[1].price
            }
            is_soldout = {
                product_SSPs[0].size : bool(product_SSPs[0].stock == 0),
                product_SSPs[1].size : bool(product_SSPs[1].stock == 0)
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
        context['productId']           = product.id 
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
        context['productSize']         = size
        context['productPrice']        = price
        context['isSoldOut']           = is_soldout
        context['dietaryHabitList']    = [dietary_habit.name for dietary_habit in product.dietary_habit.all()]
        context['similarProduct']      = similar_product_list[:2] 

        return JsonResponse({"data": context, "message": "SUCCESS"}, status=200)
        
class ProductToCartView(View):  
    @login_decorator
    def post(self, request):
            data          = json.loads(request.body)
            user          = request.user
            product_id    = data.get('productId', None)
            product_size  = data.get('productSize', None)
            product_price = data.get('productPrice', None)

            if not (product_id and product_price): 
                return JsonResponse({"message": "KEY_ERROR"}, status=400)            

           # if product_size == "":
           #     product_size = None
            print(data)
            print(product_size)
            print(type(product_size))

            if not ProductStock.objects.filter(product_id=product_id, size=product_size):
                return JsonResponse({"message": "PRODUCT_DOES_NOT_EXIST"}, status=400)

            product_price = float(product_price)

            if not Order.objects.filter(user=user, order_status_id=1).exists():
                shipping_cost = 5 if product_price < 20 else 0
                
                order_info    = Order.objects.create( 
                    user            = user,
                    order_number    = datetime.today().strftime("%Y%m%d") + str(randint(10000, 100000)),
                    order_status_id = 1,
                    sub_total_cost  = product_price,
                    shipping_cost   = shipping_cost,
                    total_cost      = product_price + shipping_cost
                )
            else:
                order_info = Order.objects.get(user=user, order_status_id=1)
                order_info.sub_total_cost = float(order_info.sub_total_cost) + product_price
                order_info.shipping_cost  = 5 if order_info.sub_total_cost < 20 else 0
                order_info.total_cost     = float(order_info.sub_total_cost) + order_info.shipping_cost
                order_info.save()

            # order_product_stocks insert
            added_product = ProductStock.objects.get(product_id=product_id, size=product_size)
            OrderProductStock.objects.update_or_create(
                order         = order_info,
                product_stock = added_product,
                defaults      = {
                    "quantity" : 1
                }
            )

            return JsonResponse({"message": "SUCCESS"}, status=200)

