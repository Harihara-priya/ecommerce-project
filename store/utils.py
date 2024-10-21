import json
from .models import *

# def cookieCart(request):
#     items = []   
#     order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
#     cartItems = order['get_cart_items']
#     try:
#         cart = json.loads(request.COOKIES['cart'])
#     except:
#         cart = {}
#         print('CART:', cart)
#         items = []
#         order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
#         cartItems = order['get_cart_items']
        
#         for i in cart:
#             #We use try block to prevent items in cart that may have been removed from causing error
#             try:
#                  cartItems += cart[i]['quantity']
                
#                  product = Product.objects.get(id=i)
#                  total = (product.price * cart[i]['quantity'])

#                  order['get_cart_total'] += total
#                  order['get_cart_items'] += cart[i]['quantity']
#                  item = {
#                        'id':product.id,
#                        'product':{
#                                  'id':product.id,
#                                   'name':product.name, 
#                                   'price':product.price, 
#                                   'imageURL':product.imageURL
#                                   }, 
#                                   'quantity':cart[i]['quantity'],
#                                   'digital':product.digital,'get_total':total,
#                         }
#                  items.append(item)
#                  if product.digital == False:
#                        order['shipping'] = True
#             except:
#                   pass
    
#     return {'cartItems' : cartItems ,'order':order, 'items':items}
def cookieCart(request):
    # Initialize default values
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']
    
    # Attempt to load the cart from cookies
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except :
        cart = {}
        print('CART:', cart)
    
    # Process each item in the cart
    for i in cart:
        try:
            quantity = cart[i]['quantity']
            cartItems += quantity
            
            # Fetch the product from the database
            product = Product.objects.get(id=i)
            total = product.price * quantity

            # Update order totals
            order['get_cart_total'] += total
            order['get_cart_items'] += quantity

            # Prepare the item dictionary
            item = {
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,  # Ensure imageURL is a valid field
                    'digital': product.digital,
                },
                'quantity': quantity,                
                'get_total': total,
            }
            items.append(item)

            # Determine if shipping is required
            if not product.digital:
                order['shipping'] = True
        except Product.DoesNotExist:
            # Handle the case where the product does not exist
            print(f"Product with id {i} does not exist.")
            continue
        except KeyError:
            # Handle the case where 'quantity' is not in cart[i]
            print(f"Quantity not found for product id {i}.")
            continue
    
    return {'cartItems': cartItems, 'order': order, 'items': items}

def cartData(request):
     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
          items = order.orderitem_set.all()
          cartItems = order.get_cart_items
          return {'items': items, 'order': order, 'cartItems': cartItems}
     else:
          #Create empty cart for now for non-logged in user
          cookieData = cookieCart(request)
          cartItems = cookieData['cartItems']
          order = cookieData['order']
          items = cookieData['items']
          return{'items':items, 'order':order, 'cartItems':cartItems}
     
def guestOrder(request, data ):

    print('User is not logged in')
    print('COOKIES:', request.COOKIES)

    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
				email=email,
				)
    customer.name = name
    customer.save()

    order = Order.objects.create(
			customer=customer,
			complete=False,
			)
    
    for item in items:
        product = Product.objects.get(id=item['id'])
        orderItem = OrderItem.objects.create(
            product=product,
				order=order,
				quantity=item['quantity'],
        )

        return customer, order
        
     