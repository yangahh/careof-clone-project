import json
from datetime       import datetime
from random         import randint

from django.http    import JsonResponse, HttpResponse
from django.views   import View

from user.utils     import login_decorator
from user.models    import User, Address
from product.models import Product, ProductStock, Image 
from .models        import (
    Order,
    OrderProductStock,
    Promotion,
)

class CartView(View):
     @login_decorator
     def get(self, request):
        user = request.user
        
        if not Order.objects.filter(user=user, order_status_id=1).exists():
            return JsonResponse({"message": "EMPTY"}, status=200)
        
        order_exist          = Order.objects.get(user=user, order_status_id=1)
        order_products_exist = order_exist.orderproductstock_set.filter(order=order_exist)
        
        cart_product_list = []
        for order_product_exist in order_products_exist:
            product_SSP  = order_product_exist.product_stock 
            product      = product_SSP.product
            product_info = {
                "category"        : product.category.menu.name,
                "productId"       : product.id,
                "productName"     : product.name,
                "productSubName"  : product.sub_name,
                "productStockId"  : product_SSP.id,
                "productSize"     : product_SSP.size,
                "productPrice"    : product_SSP.price,
                "productImageUrl" : product.image_set.get(is_main=True).image_url,
                "productQuantity" : order_product_exist.quantity
            }
            cart_product_list.append(product_info)

        data = {
            "orderNumber": order_exist.order_number,
            "carts": cart_product_list,
        }

        return JsonResponse({"data": data, "message": "SUCCESS"}, status=200)

class CartDetailView(View):
    @login_decorator
    def post(self, request, product_stock_id):
        data         = json.loads(request.body)
        user         = request.user
        product_id   = data.get('productId', None)
        size_new     = data.get('productSize', None)
        quantity_new = data.get('productQuantity', None)
        
        print("===========start=============")
        print(f'product_id: {product_id}')
        print(f'quantity_new: {quantity_new}')
        print(type(quantity_new))
        print(f'size_new: {size_new}')
        print(type(size_new))

        if not (product_id and quantity_new):
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        if not ProductStock.objects.filter(id=product_stock_id):
            return JsonResponse({"message": "DOES_NOT_EXIST"}, status=404)
        

        print("=====is validate product_stock?========")
        if not ProductStock.objects.filter(product_id=product_id, size=size_new):
            return JsonResponse({"message": "DOES_NOT_EXIST"}, status=400)
        
        # 대상 상품 조회
        order_exist          = Order.objects.get(user=user, order_status_id=1)
        target_order_product = order_exist.orderproductstock_set.filter(product_stock_id=product_stock_id)

        print("=====is target_order_product?========")
        
        if not target_order_product:
            return JsonResponse({"message": "DOES_NOT_EXIST"}, status=400)
        
        target_order_product      = target_order_product[0] 
        target_order_product_size = target_order_product.product_stock.size
        product_new               = ProductStock.objects.get(product_id=product_id, size=size_new)
        print(f"=====기존 상품 : {target_order_product}=====")
        print(f"=====새로 바꿀 상품 : {product_new.id}, {product_new.size}=====")
        # 변경할 상품이 이미 OrderProductStock에 존재하는 경우
        if target_order_product_size != size_new: 
            order_product_already_exist = OrderProductStock.objects.filter(order=order_exist, product_stock=product_new) 
            #order_product_already_exist = order_exist.product_stock.get(id=product_new.id) 
            if order_product_already_exist:
                print("=========already target===========")
                print("=====바꿀 상품이 이미 있는거 : {order_product_already_exist[0]}=====")

                if bool(product_new.stock - quantity_new < 0):
                    return JsonResponse({"message": "OUT_OF_STOCK"}, status=200)

                order_product_already_exist[0].quantity = quantity_new
                order_product_already_exist[0].save()

                # 원래 있던 상품은 새로 바꿀 상품이 이미 존재하는게 있으므로 삭제 
                target_order_product.delete()
                return JsonResponse({"message": "SUCCESS"}, status=200)

        if bool(product_new.stock - int(quantity_new) < 0):
            return JsonResponse({"message": "OUT_OF_STOCK"}, status=200)

        target_order_product.product_stock = product_new
        target_order_product.quantity      = quantity_new
        target_order_product.save()

        return JsonResponse({"message": "SUCCESS"}, status=200)

    @login_decorator
    def delete(self, request, product_stock_id):
        if not ProductStock.objects.filter(id=product_stock_id):
            return JsonResponse({"message": "DOES_NOT_EXIST"}, status=404)

        user          = request.user
        order_exist   = Order.objects.get(user=user, order_status_id=1)
        product_exist = ProductStock.objects.get(id=product_stock_id)
        
        if not OrderProductStock.objects.filter(order=order_exist, product_stock=product_exist):
            return JsonResponse({"message": "DOES_NOT_EXIST"}, status=404)

        order_product_exist = OrderProductStock.objects.get(order=order_exist, product_stock = product_exist)
        order_product_exist.delete()

        # 장바구니에 상품이 없을 경우 order 정보 삭제
        if not OrderProductStock.objects.filter(order=order_exist).exists():
            order_exist.delete()

        return JsonResponse({"message": "SUCCESS"}, status=200) 

class CheckOutView(View):
    @login_decorator
    def get(self, request, order_number):
        user         = request.user

        if not order_number:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        order_info     = Order.objects.get(order_number=order_number)
        order_products = order_info.orderproductstock_set.all()
        
        cart_product_list = []
        for order_product in order_products:
            product_SSP  = order_product.product_stock
            product      = product_SSP.product
            product_info = {
                "category"        : product.category.menu.name,
                "productId"       : product.id,
                "productName"     : product.name,
                "productSubName"  : product.sub_name,
                "productStockId"  : product_SSP.id,
                "productSize"     : product_SSP.size,
                "productPrice"    : product_SSP.price,
                "productIsSoldOut": bool(product_SSP.stock - order_product.quantity <= 0), 
                "productImageUrl" : product.image_set.get(is_main=True).image_url,
                "productQuantity" : order_product.quantity
            }
            cart_product_list.append(product_info)
         
        address_info = user.address_set.filter(is_main=True)
        address      = address_info[0].address if address_info else ""
        zip_code     = address_info[0].zip_code if address_info else ""
        user_info = {
            "userName"    : user.name,
            "email"       : user.email,
            "phoneNumber" : user.phone_number,
            "address"     : address,
            "zipcode"     : zip_code
        }

        data = {
            "orderNumber": order_info.order_number,
            "carts"      : cart_product_list,
            "user"       : user_info
        }
        return JsonResponse({"data": data, "message": "SUCCESS"}, status=200)
        
    @login_decorator
    def post(self, request, order_number):
        data = json.loads(request.body)
        sub_total_cost = data.get('subTotalCost', None)
        shipping_cost  = data.get('shippingCost', None)
        promotion_code = data.get('promotionCode', None)
        total_cost     = data.get('totalCost', None)
        address_order  = data.get('address', None)
        zipcode_order  = data.get('zipcode', None)
        user           = request.user

        if not(order_number and sub_total_cost and shipping_cost and total_cost):
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
         
        if promotion_code:
            if not Promotion.objects.filter(code=promotion_code):
                return JsonResponse({"message": "WRONG_PROMOTION_CODE"}, status=200)
            promotion_code = Promotion.objects.get(code=promotion_code)

        order_info = Order.objects.get(order_number=order_number)
        order_info.order_status_id = 2
        order_info.sub_total_cost  = float(sub_total_cost)
        order_info.shipping_cost   = float(shipping_cost)
        order_info.promotion       = promotion_code
        order_info.total_cost      = float(total_cost)
        order_info.save()

        Address.objects.update_or_create(
            user     = user,
            address  = address_order,
            zip_code = zipcode_order,
            defaults = {
                'order'  : order_info,
                'is_main': False
            }
        )

        return JsonResponse({"message": "SUCCESS"}, status=200)
        
    # stock 업데이트는 카드 결제 들어가면 transaction로 처리하기
    # 결제 실패면 addresses의 order_id를 null로 바꾸기
