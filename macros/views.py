import json
import logging

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import MacrosForm
from .utils import zabbix_data, serialize, full_change_macros, VersionManager
from .tasks import change


class MacrosView(View):

    template_name = 'macros/macro.html'
    form_class = MacrosForm

    def get(self, request, *args, **kwargs):
        flag = request.GET.get('flag', False)
        form = self.form_class()
        zapi = zabbix_data()
        hosts = zapi.instance.host.get(
            groupids=['168', '174', '175'], selectMacros='extend')
        hosts = serialize(hosts)

        return render(request, self.template_name, {"hosts": hosts, "flag": flag, "form": form})

    def post(self, request, *args, **kwargs):
        """Здесь будет обработка данных с формы при отправке пост запроса и дальнейший запуск задачи"""
        form = self.form_class(request.POST)
        if form.is_valid():
            full_change_macros(form.cleaned_data["sheet"])
            change(form.cleaned_data["sheet"])
            url = '/macros/?flag=True'
            return redirect(url)
        return JsonResponse({"message": "Форма не валидна"}, status=200,
                            content_type='application/json')



@csrf_exempt
def version_webhook(request):
    if request.method == "POST":
        """
        item_id - список из ID элементов в Zabbix

        98240 - элемент Bars Web Check PRED-MIS
        83444 - элемент Bars Web Check MIS
        98248 - элемент Bars Web Check PRED-MIS 22.02
        198879 - элемент Bars Web Check MIS 22.02 KFU
        83458 - элемент Bars Web Check MIS 22.02
        232233, 232231 - элемент ФГБУ 'НИИ АГиР им. Д. О. Отта'
        333762 - элемент Новосибирская обл. {host_id: 11076}

        """

        item_id = ['98240', '83444', '98248', '198879',
                   '83458', '232233', '232231', '333762']
        data = json.loads(request.body)
        logging.info(f'webhook - {data}')
        if data.get("version") is not None:
            with VersionManager(data['version']) as version:
                zabbix = zabbix_data()
                for item in item_id:
                    zabbix.instance.item.update(itemid=item, preprocessing=[{

                        "type": 21,
                        "params": version
                    }])
            return JsonResponse({"message": "success", "webhook": data}, status=200,
                                content_type='application/json')
        return JsonResponse({"message": f"Error in data {data['version']}"}, status=400, content_type='application/json')



@csrf_exempt
def version_webhook_prod_otta(request):
    if request.method == "POST":
        data = json.loads(request.body)
        logging.info(f'webhook - prod {data}')
        if data.get("version") is not None:
            zabbix = zabbix_data()
            zabbix.instance.item.update(itemid=232232, preprocessing=
            [{
                "type": 21,
                "params": "return " + '"' + data['version'] + '"'
            }])

        return JsonResponse({"message": data}, status=200,
                            content_type='application/json')



@csrf_exempt
def version_webhook_preprod_otta(request):
    if request.method == "POST":
        data = json.loads(request.body)
        logging.info(f'webhook - preprod {data}')
        if data.get("version") is not None:
            zabbix = zabbix_data()
            zabbix.instance.item.update(itemid=232230, preprocessing=
            [{
                "type": 21,
                "params": "return " + '"' + data['version'] + '"'
            }])

        return JsonResponse({"message": data}, status=200,
                            content_type='application/json')

