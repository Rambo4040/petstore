from typing import Any
from django.shortcuts import render,redirect
from .models import pet,customer,cart,order,payment,orderdetail
from django.http import HttpResponse
from django.views.generic import DeleteView,ListView,CreateView,UpdateView,DetailView
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class petview(ListView):
    model = pet
    template_name = 'petview.html'
    context_object_name = 'petobj'  

    def get_context_data(self, **kwargs):
            try:
                data = self.request.session['sessionvalue']
                context = super().get_context_data(**kwargs)
                context['session'] = data
                return context
            except:
                context = super().get_context_data(**kwargs)
                return context


class petviewcm(ListView):
    template_name= 'petview.html'
    context_object_name ='petobj'


def petviewcmfun(request):
    petdetails = pet.cpetobj.getdata('dog')
    return render(request,'PetView.html',{'petobj':petdetails})   


def search(request):
    if request.method == "POST":
        session = request.session['sessionvalue']
        searchdata = request.POST.get('Search')
        petobj = pet.objects.filter(Q(name__icontains = searchdata) | Q(breeds__icontains = searchdata) | Q(species__icontains = searchdata))
        return render(request, 'petview.html', {'petobj': petobj, 'session':session})
    

def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        firstName = request.POST.get('firstName')
        phoneno = request.POST.get('phoneno')
        email = request.POST.get('email')
        password = request.POST.get('password')
        epassword = make_password(password)

        cutobj = customer(name=firstName, password=epassword, email=email, phoneno=phoneno)
        cutobj.save()
        return redirect('../login/')
    
def login(request):
    if request.method == "GET":
         return render(request, 'login.html')
    elif request.method =="POST":
        user = request.POST.get('username')
        print(user)
        password = request.POST.get('pass')
        print(password)

        cust = customer.objects.filter(email=user)
        if cust:
            custobj = customer.objects.get(email=user)

            flag = check_password(password,custobj.password)

            if flag:
                request.session['sessionvalue'] =  custobj.email
                return redirect('../petview/')
            else:
                return render(request, 'login.html',{'msg': 'Incorrect Username or Password !'})
        else:
            return render(request, 'login.html', {'msg': 'Incorrect Username or Password !'})
        

class petdetail(DetailView):
    model = pet
    template_name = 'petdetail.html'
    context_object_name = 'i'


def addtocart(request):
    productid = request.POST.get('productid')
    try:
        custsession = request.session['sessionvalue'] #email of customer
        custobj = customer.objects.get(email = custsession) #fetch record from database table using email
        print('inside the try')
        custid = custobj.id #fetch customer id using customer object
        pobj = pet.objects.get(id = productid)

        flag = cart.objects.filter(cid = custobj.id,pid = pobj.id)
        if flag:
            cartobj = cart.objects.get(cid = custobj.id,pid = pobj.id)
            cartobj.quantity = cartobj.quantity +1
            cartobj.totalamount = pobj.price * cartobj.quantity
            cartobj.save()
        else:
            cartobj = cart(cid = custobj,pid = pobj, quantity = 1,totalamount = pobj.price*1)
            cartobj.save()

        return redirect('../petview/')
    except:
        return redirect('../login/')






def viewcart(request):
    custsession = request.session['sessionvalue'] #email of customer
    custobj = customer.objects.get(email = custsession) 
    cartobj = cart.objects.filter(cid = custobj.id)

    return render(request,'cart.html',{'cartobj':cartobj, 'session':custsession})



def cq(request):
    cemail = request.session['sessionvalue']
    pid = request.POST.get('pid')
    # print(pid)
    custobj = customer.objects.get(email = cemail)
    pobj = pet.objects.get(id = pid)
    cartobj = cart.objects.get(cid = custobj.id, pid = pobj.id)
    print(cartobj)
    if request.POST.get('changequantitybutton') == '+':
        print("inside + quantity")
        cartobj.quantity = cartobj.quantity + 1
        print( cartobj.quantity)
        cartobj.totalamount = cartobj.quantity * pobj.price
        cartobj.save()
    
    elif request.POST.get('changequantitybutton') == '-':
        print("inside - quantity")
        if cartobj.quantity == 1:
            cartobj.delete()
        else :
            cartobj.quantity = cartobj.quantity - 1
            cartobj.totalamount = cartobj.quantity * pobj.price
            cartobj.save()

    return redirect('../viewcart/')


def summary(request):
    custsession = request.session['sessionvalue']
    custobj = customer.objects.get(email = custsession)
    cartobj = cart.objects.filter(cid = custobj.id)
    totalbill = 0
    for i in cartobj:
        totalbill = i.totalamount + totalbill

    return render(request, 'summary.html', {'session':custsession, 'cartobj': cartobj, 'totalbill': totalbill})


def placeorder(request):
    fn = request.POST.get('fn')
    ln = request.POST.get('ln')
    phoneno = request.POST.get('phoneno')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    pincode = request.POST.get('pincode')

    datev = date.today()
    orderobj = order(firstname = fn, lastname = ln, phoneno = phoneno, address = address, city = city, state = state, pincode = pincode, orderdate = datev, orderstatus= 'pending')
    orderobj.save()
    
    ono = str(orderobj.id) +str(datev).replace('-', '')
    orderobj.ordernumber = ono
    orderobj.save()

    custsession = request.session['sessionvalue']
    custobj = customer.objects.get(email = custsession)
    cartobj = cart.objects.filter(cid = custobj.id)
    totalbill = 0
    for i in cartobj:
        totalbill = i.totalamount + totalbill

    
    from django.core.mail import EmailMessage

    sm = EmailMessage('Order Placed', 'order placed from pet store application. Tota bill of your order is ' +str(totalbill), to=['rambovalo2404@gmail.com'])
    sm.send()


    # authorize razorpay client with API Keys.
    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
 
 

    currency = 'INR'
    amount = 20000  # Rs. 200
 
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = '../PetView'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'payment.html', {'orderobj':orderobj, 'session': custsession, 'cartobj': cartobj, 'totalbill': totalbill, 'context' : context})



def success(request):
    orderid = request.GET.get('order_id')
    tid = request.GET.get('payment_id')
    request.session['sessionvalue'] = request.GET.get('session')
    custsession = request.session['sessionvalue']
    custobj = customer.objects.get(email=custsession)
    cartobj = cart.objects.filter(cid=custobj.id)
    orderobj = order.objects.get(ordernumber = orderid)

    

    paymentobj = payment(customerid = custobj, oid = orderobj, paymentstatus = 'Paid', transactionid = tid)
    paymentobj.save()

    for i in cartobj:
        # orderobj = placeorder(ordernumber = ono, cid = custobj, pid = i.pid, quantity = i.quantity, totalamount = i.totalamount, paymentid = paymentobj)
        orderdetailobj = orderdetail(paymentid = paymentobj,ordernumber = orderid, productid = i.pid,customerid = i.cid,quantity = i.quantity,totalprice = i.totalamount)
        orderdetailobj.save()
        i.delete()
    
    totalbill = 0
    for i in cartobj:
        totalbill = i.totalamount + totalbill

    return render(request,'success.html',{'session':custsession,'payobj':paymentobj, 'order':orderobj, 'cartobj': cartobj,  'totalbill' :totalbill})
    

def logout(request):
    del(request.session['sessionvalue'])
    return redirect('../login/')

