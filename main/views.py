import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView


from .models import Region, GeneralUser, RegionsAndUsers, OtherUser
from .forms import UpdateUserRegionForm, UpdateUserForm, SearchUserForm, AddUserForm, MacrosForm


class MainView(TemplateView):
    template_name = 'main/index.html'


class MISView(View):
    template_name = 'mis/regions.html'

    def get(self, request, *args, **kwargs):
        regions = Region.objects.filter(service='MIS').order_by('name_region')
        return render(request, self.template_name, {"regions": regions})


class RegionView(View):
    template_name = None

    def get(self, request, *args, **kwargs):
        region_id = kwargs.get('pk')
        region, users_region = self.get_user_region(region_id)
        return render(request, self.template_name, {"region": region,
                                                    "users": [(user.pk, user,  user.username, user.is_admin)
                                                              for user in users_region]})

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        result = RegionsAndUsers.objects.filter(pk=data["user"]).delete()
        return JsonResponse({
            "message": f"Пользователь успешно удален"
        }, status=200, content_type='application/json')


    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print(data)
        RegionsAndUsers.objects.filter(username=data['user_id'], region=int(data['region']))\
                               .update(is_admin=data['is_admin'])
        OtherUser.objects.filter(pk=data['user_id']).update(username=data['username'])

        return JsonResponse({
            "message": f"Пользователь успешно обновлен"
        }, status=200, content_type='application/json')

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        region = Region.objects.get(pk= data["region"])
        user = OtherUser.objects.get(pk=data["user"])
        new_user = RegionsAndUsers.objects.filter(username=user, region=region).exists()
        if not new_user:
            new_user = RegionsAndUsers(username=user,
                                   region=region,
                                   is_admin=data['is_admin'])
            new_user.save()
            return JsonResponse({"is_ok": True},
                                status=200, content_type='application/json')

        return JsonResponse({"is_ok": False},
                            status=200, content_type='application/json')


    def get_user_region(self, region_id: int):
        region = Region.objects.get(pk=region_id)
        users_region = RegionsAndUsers.objects.filter(region=region_id)
        return region, users_region


class TFOMSView(View):
    template_name = 'tfoms/regions.html'

    def get(self, request, *args, **kwargs):
        regions = Region.objects.filter(service='TFOMS').order_by('name_region')
        return render(request, self.template_name, {"regions": regions})



class CoreUsersView(View):
    template_name = 'core_users/core.html'

    def get(self, request, *args, **kwargs):
        users = GeneralUser.objects.all().order_by('name')
        return render(request, self.template_name, {"users": users})


    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        GeneralUser.objects.filter(pk=int(data["user"])).update(username=data["username"], role=data["role"])
        return JsonResponse({"message": "Данные успешны обновлены"},
                            status=200, content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        GeneralUser.objects.filter(pk=data["user"]).delete()
        return JsonResponse({"message": "Пользователь удален"},
                            status=200, content_type='application/json')


class MiniUsersView(View):
    template_name = 'core_users/mini.html'

    def get(self, request, *args, **kwargs):
        users = GeneralUser.objects.filter(role="MINI").order_by('name')
        return render(request, self.template_name, {"users": users})

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        GeneralUser.objects.filter(pk=int(data["user"])).update(username=data["username"], role=data["role"])
        return JsonResponse({"message": "Данные успешны обновлены"},
                            status=200, content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        GeneralUser.objects.filter(pk=data["user"]).delete()
        return JsonResponse({"message": "Пользователь удален"},
                            status=200, content_type='application/json')



class UpdateRegionUserView(View):
    template_name = None
    form_class = UpdateUserRegionForm


    def get(self, request, *args, **kwargs):
        username = kwargs.get("username")
        region = Region.objects.get(pk=kwargs.get("pk"))
        user = OtherUser.objects.get(username=username)
        return render(request, self.template_name, {"form": self.form_class(username_initial=username),
                                                    "user": user, "region": region})


class AddRegionUserView(View):
    template_name = None
    form_class = SearchUserForm()

    def get(self, request, *args, **kwargs):
        print(kwargs.get("pk"))
        region = Region.objects.get(pk=kwargs.get("pk"))
        print(request.GET)
        if request.GET.get("name"):
            search_result = OtherUser.objects.filter(name__contains=request.GET.get("name"))
            return render(request, self.template_name, {"form": self.form_class,
                                                        "region": region,
                                                        "result": search_result})
        return render(request, self.template_name, {"form": self.form_class,
                                                    "region": region})


class UpdateUserView(View):
    template_name = None
    form_class = UpdateUserForm

    def get(self, request, *args, **kwargs):
        username = kwargs.get("username")
        user = GeneralUser.objects.get(username=username)
        return render(request, self.template_name, {"form": self.form_class(username_initial=username),
                                                    "user": user})


class AddUserView(View):
    template_name = None
    form_class = AddUserForm()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": self.form_class})


    def post(self,request, *args, **kwargs):
        data = json.loads(request.body)
        new_user = GeneralUser(name=data["name"],
                               username=data["username"],
                               role=data["role"])
        new_user.save()
        return JsonResponse({"message": "Данные успешны обновлены"},
                            status=200, content_type='application/json')






