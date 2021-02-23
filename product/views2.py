import json
from datetime import datetime
from random   import randint

from django.http  import JsonResponse, HttpResponse
from django.views import View

from user.utils     import login_decorator
from product.models import (Menu,
                            Category, 
                            Product,
                            Image,
                            ProductStock,
                            RelatedProduct,
                            Disease,
                            ProductDisease,
                            Allergy,
                            ProductAllergy,
                            Goal,
                            ProductGoal,
                            ProductDietaryHabit,
                            DietaryHabit,
                            VeganLevel,
                            ActivityLevel,
                            GenderCode,
                            AgeLevel)
from user.models    import User, Address
from order.models   import Promotion, Order, Review, OrderProductStock, OrderStatus, ShipmentStatus

class ProductView(View):
    def get(self, request, id=None):
        result = []
        # show_all
        if id == None:
            categories = Category.objects.all() #category_all
            for category in categories: #category_all
                context = {}
                context["id"] = category.id
                context["subcategory"] = {}
                context["subcategory"]["title"] = category.name
                context["subcategory"]["description"] = category.description
                
                products = Product.objects.filter(category=category)    #products_category for product_category in products_category
                
                product_list = []   #product_info_list
                for product in products:
                    goals = product.goal.all()      #goals_product      for goal_product in goals_product
                    product_stocks = product.productstock_set.all()     #product_SSPs     for product_SSP in product_SSPs 알아맞춰봥
                    goal_name_list = [goal.name for goal in goals]
                    product_stock_price_list = [product_stock.price for product_stock in product_stocks] #product_price_list
                    product_stock_count_list = [product_stock.stock for product_stock in product_stocks] #product_stock_list
                    product_stock_size_list = [product_stock.size for product_stock in product_stocks]
                    is_soldout = True if sum(product_stock_count_list) == 0 else False

                    product_dic = {     #product_info
                        "id": product.id,
                        "displayTitle": product.name, 
                        "subTitle": product.sub_name,
                        "imageUrl": product.image_set.get(is_main=True).image_url,  
                        "symbolURL": goal_name_list,             
                        "description": product.description,
                        "displayPrice": product_stock_price_list, 
                        "displaySize": product_stock_size_list,
                        "isNew": product.is_new,
                        "isSoldout": is_soldout
                    }
                    product_list.append(product_dic)

                context["item"] = product_list
                result.append(context)

            return JsonResponse({"data": result, "message": "SUCCESS"}, status=200)
        
        #recently added  
        if id == 99999:               # 프론트에 얘기하기 
            products = Product.objects.filter(is_new=True)
            for product in products:
                goals = product.goal.all()
                product_stocks = product.productstock_set.all()

                product_stock_price_list = [product_stock.price for product_stock in product_stocks]
                product_stock_count_list = [product_stock.stock for product_stock in product_stocks]
                product_stock_size_list = [product_stock.size for product_stock in product_stocks]
                is_soldout = True if sum(product_stock_count_list) == 0 else False

                product_dic = {
                        "id": product.id,
                        "displayTitle": product.name, 
                        "subTitle": product.sub_name,
                        "imageUrl": product.image_set.get(is_main=True).image_url,   #나중에 수정해야함 is_main
                        "symbolURL": [goal.name for goal in goals],#이름으로 변경                
                        "description": product.description,
                        "displayPrice": product_stock_price_list,
                        "displaySize": product_stock_size_list,
                        "isNew": product.is_new,
                        "stock": is_soldout
                        }
                
                result.append(product_dic)
            
            return JsonResponse({"data": result, "message": "SUCCESS"}, status=200)
        
        
        if Category.objects.filter(id=id).exists:
            categories = Category.objects.filter(id=id)
            for category in categories:
                context = {}
                context["id"] = category.id
                context["subcategory"] = {}
                context["subcategory"]["title"] = category.name
                context["subcategory"]["description"] = category.description
                
                products = Product.objects.filter(category=category)
                product_list = []
                for product in products:
                    goals = product.goal.all()
                    product_stocks = product.productstock_set.all()

                    product_stock_price_list = [product_stock.price for product_stock in product_stocks]
                    product_stock_count_list = [product_stock.stock for product_stock in product_stocks]
                    product_stock_size_list = [product_stock.size for product_stock in product_stocks]
                    is_soldout = True if sum(product_stock_count_list) == 0 else False

                    product_dic = {
                        "id": product.id,
                        "displayTitle": product.name, 
                        "subTitle": product.sub_name,
                        "imageUrl": product.image_set.get(is_main=True).image_url,   #나중에 수정해야함 is_main
                        "symbolURL": [goal.name for goal in goals],#이름으로 변경                
                        "description": product.description,
                        "displayPrice": product_stock_price_list,
                        "displaySize": product_stock_size_list,
                        "isNew": product.is_new,
                        "isSoldout": is_soldout
                        }
                    product_list.append(product_dic)

                context["item"] = product_list
                result.append(context)
            
            return JsonResponse({"data": result, "message": "SUCCESS"}, status=200)
        
                    
class GoalView(View):
    def get(self, request, id):
        result = []
        if Goal.objects.filter(id=id):
            # product_result = []
            products = Product.objects.filter(goal=Goal.objects.get(id=id).id)
            for product in products:
                goals = product.goal.all()
                product_stocks = product.productstock_set.all()

                product_stock_price_list = [product_stock.price for product_stock in product_stocks]
                product_stock_count_list = [product_stock.stock for product_stock in product_stocks]
                product_stock_size_list = [product_stock.size for product_stock in product_stocks]
                is_soldout = True if sum(product_stock_count_list) == 0 else False

                product_dic = {
                        "id": product.id,
                        "displayTitle": product.name, 
                        "subTitle": product.sub_name,
                        "imageUrl": product.image_set.get(is_main=True).image_url,   #나중에 수정해야함 is_main
                        "symbolURL": [goal.name for goal in goals],#이름으로 변경                
                        "description": product.description,
                        "displayPrice": product_stock_price_list,
                        "displaySize": product_stock_size_list,
                        "isNew": product.is_new,
                        "isSoldout": is_soldout
                        }
                
                result.append(product_dic)

            return JsonResponse({"data": result, "message": "SUCCESS"}, status=200)

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
        


#Add 눌렀을 때 
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

            product_price = float(product_price)

            # orders insert
            if not Order.objects.filter(user=user, order_status_id=1).exists():
                shipping_cost = 5 if product_price < 20 else 0
                order         = Order.objects.create(  # order_info
                    user            = user,
                    order_number    = datetime.today().strftime("%Y%m%d") + str(randint(1000, 10000)),
                    order_status_id = 1,
                    sub_total_cost  = product_price,
                    shipping_cost   = shipping_cost,
                    total_cost      = product_price + shipping_cost
                )
                

            else:
                order = Order.objects.get(user=user, order_status_id=1)
                order.sub_total_cost = float(order.sub_total_cost) + product_price
                order.shipping_cost  = 5 if order.sub_total_cost < 20 else 0
                order.total_cost     = float(order.sub_total_cost) + order.shipping_cost
                order.save()
            
            if not ProductStock.objects.filter(product_id=product_id, size=product_size):
                return JsonResponse({"message": "PRODUCT_DOES_NOT_EXIST"}, status=400)

            # order_product_stocks insert
            added_product = ProductStock.objects.get(product_id=product_id, size=product_size)
            # OrderProductStock.objects.create(
            #     order         = order,
            #     product_stock = added_product,
            #     quantity      = 1
            # )
            OrderProductStock.objects.update_or_create(
                order         = order,
                product_stock = added_product,
                defaults      = {
                    'quantity' : 1
                }
            )

            return JsonResponse({"message": "SUCCESS"}, status=200)