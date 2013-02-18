from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.contrib.auth.decorators import login_required as _login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

def login_required(function=None,
                   redirect_field_name=REDIRECT_FIELD_NAME,
                   login_url=None):
    if settings.TESTING or settings.DEBUG:
        return function
    else:
        return _login_required(function,redirect_field_name,login_url)

from momonitor.main.models import (RESOURCE_NAME_MAP,
                                   Service,
                                   CodeServiceCheck,
                                   RESOURCES)

from momonitor.main.forms import RESOURCE_FORM_MAP

from momonitor.main.decorators import ajax_required

@login_required
def index(request):
    request.breadcrumbs("Services",reverse("main_index"))

    services = Service.objects.all().order_by("id")
    return render_to_response("index.html",{'services':services},RequestContext(request))

@login_required
def service(request,service_id):
    service = get_object_or_404(Service,pk=service_id)

    request.breadcrumbs("Services",reverse("main_index"))
    request.breadcrumbs(service.name,reverse("main_service",kwargs={'service_id':service.id}))

    umpire_checks = service.umpireservicecheck.all().order_by("id")
    simple_checks = service.simpleservicecheck.all().order_by("id")
    compare_checks = service.compareservicecheck.all().order_by("id")
    code_checks = service.codeservicecheck.all().order_by("id")
    complex_checks = service.complexservicecheck.all().order_by("id")
    return render_to_response("service.html",{'service':service,
                                              'umpire_checks':umpire_checks,
                                              'simple_checks':simple_checks,
                                              'compare_checks':compare_checks,
                                              'code_checks':code_checks,
                                              'complex_checks':complex_checks},
                              RequestContext(request))

@login_required
def modal_form(request,resource_name,resource_id=None):
    if not RESOURCE_NAME_MAP.has_key(resource_name):
        raise Http404
    resource_cls = RESOURCE_NAME_MAP[resource_name]
    resource_form_cls = RESOURCE_FORM_MAP[resource_cls]

    if resource_id:
        instance = get_object_or_404(resource_cls,pk=resource_id)
        method="PUT"
        action = "/api/v1/%s/%s/?format=json" % (resource_cls.resource_name,
                                                 instance.id)
    else:
        instance = None
        method="POST"
        action="/api/v1/%s/?format=json" % (resource_cls.resource_name)

    #Hack to get code check upload to work
    if resource_cls == CodeServiceCheck:
        method="POST"

    if hasattr(instance,"service") or request.GET.has_key("sid"):
        form = resource_form_cls(instance=instance,
                                 initial={'service':instance.service.id if instance else request.GET.get("sid")})

    elif hasattr(instance,"complex_check") or request.GET.has_key("cid"):
        form = resource_form_cls(instance=instance,
                                 initial={"complex_check":instance.complex_check.id if instance else  request.GET.get("cid")})
    else:
        form = resource_form_cls(instance=instance)

    return render_to_response(form.template,{"form":form,
                                             "action":action,
                                             'method':method},
                              RequestContext(request))

@login_required
def refresh(request,resource_name,resource_id):
    if not RESOURCE_NAME_MAP.has_key(resource_name):
        raise Http404
    resource_cls = RESOURCE_NAME_MAP[resource_name]
    resource = get_object_or_404(resource_cls,pk=resource_id)
    resource.update_status()
    return HttpResponse("OK")

@login_required
def test_alert(request,service_id):
    service = get_object_or_404(Service,pk=service_id)
    service.send_alert(description="Test alert")
    return HttpResponse("OK")

@csrf_exempt
@login_required
def code_check_upload(request,instance_id=None):
    instance = None
    if instance_id:
        instance = get_object_or_404(CodeServiceCheck,pk=instance_id)

    if request.method == "DELETE":
        instance.delete()
        return HttpResponse("OK")

    data = request.POST.copy()
    form_cls = RESOURCE_FORM_MAP[CodeServiceCheck]
    form = form_cls(data,request.FILES,instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse("main_service",kwargs={'service_id':data['service']}))
    else:
        return HttpResponseBadRequest(form.errors.items())

def how_it_works(request):
    request.breadcrumbs("Services",reverse("main_index"))
    request.breadcrumbs("How it works",reverse("main_how_it_works"))
    return render_to_response("how-it-works.html",{},RequestContext(request))
