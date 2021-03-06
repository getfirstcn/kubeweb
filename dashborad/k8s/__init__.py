#encoding:utf-8
from kubernetes import client, config
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from django.views.generic import TemplateView, View, ListView
from kubernetes import client, config
import repitl, dp
from django.shortcuts import render

#
# class PodList(TemplateView):
#
#     template_name = 'k8s/pod.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(PodList, self).get_context_data(**kwargs)
#         # context['userlist'] = User.objects.all()
#         config.load_kube_config()
#         v1 = client.CoreV1Api()
#         ret = v1.list_pod_for_all_namespaces(watch=False)
#
#         # 获取所有的用户列表对象
#         paginator = Paginator(userlist, 2)
#         page = self.request.GET.get('page', 1)
#         print page
#         try:
#             page_obj = paginator.page(page)
#         except EmptyPage:
#             page_obj = paginator.page(1)
#         print page_obj.object_list
#         context['page_obj'] = page_obj
#         CountPage = page_obj.paginator.page_range
#         if page_obj.number < 6:
#             CurPage = 6
#         else:
#             CurPage = page_obj.number
#         ppaa = CountPage[CurPage-6:CurPage+4]
#         context['views_page'] = ppaa
#         return context
#
#     def get(self, request, *args, **kwargs):
#         self.request = request
#         return super(PodList, self).get(request, *args, **kwargs)


def pod_list(request):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    latest_question_list = v1.list_pod_for_all_namespaces(watch=False)
    template = loader.get_template('k8s/pod.html')
    context = RequestContext(request, {
        'latest_question_list': latest_question_list,
    })
    print(latest_question_list)
    return HttpResponse(template.render(context))


class Nm_list(TemplateView):
    template_name = 'k8s/namespace.html'

    def get_context_data(self, **kwargs):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        # 好像米=前端模板不支持切面,这里把namespace 循环除来=加到nmlist里面
        nm_list = []
        for i in v1.list_namespace(watch=False).items:
            nm_list.append(i.metadata.self_link.split('/')[-1])

        context = super(Nm_list, self).get_context_data(**kwargs)
        context['nm_list'] = nm_list
        # context['nm_list'] = [1, 2, 3]

        return context

    def post(self, request):
        ret = {'status': 0}
        name = request.POST.get('name', None)

        if name:
            try:
                # 实例化一个api配置
                config.load_kube_config()
                v1 = client.CoreV1Api()
                # 实例化一个namespace对象
                ns = client.V1Namespace()
                ns.metadata = client.V1ObjectMeta(name=name)

                # 生成namespace
                v1.create_namespace(body=ns)
                print(name)
            except Exception as e:
                ret['status'] = 1
                ret['msg'] = e.args
        return JsonResponse(ret, safe=True)


class Dp_list(TemplateView):
    # 模板渲染
    template_name = 'k8s/dp.html'

    def get_context_data(self, **kwargs):
        config.load_kube_config()
        v1 = client.AppsV1beta2Api()
        context = super(Dp_list, self).get_context_data(**kwargs)
        dp_list = v1.list_deployment_for_all_namespaces().items
        context['dp_list'] = dp_list
        return context


class SelectType(View):

    def get(self, request, types):
        print(types)
        if types == 'add':
            return render(request, 'k8s/dpp.html', {'title': 'rebbot 晕为'})
        if types == 'img':
            a = repitl.get_image_name()
            return JsonResponse(a, safe=False)

        if types == 'pj':
            return JsonResponse(repitl.get_project())

        if types == 'ns':
            config.load_kube_config()
            v1 = client.CoreV1Api()
            nm_list = []
            for i in v1.list_namespace(watch=False).items:
                nm_list.append(i.metadata.self_link.split('/')[-1])
            return JsonResponse(nm_list, safe=False)

    def post(self, request, types):
        if types == 'img':
            pj_id = request.POST.get('pid')
            a = repitl.get_image_name(project_id=pj_id)

            if a:
                return JsonResponse(a, safe=False)
            else:
                return JsonResponse('N', safe=False)

        if types == 'tags':
            repo_name = request.POST.get('image')
            tags = repitl.get_tags(repo_name)
            return JsonResponse(tags, safe=False)


class Add_Mod_Dp(View):
    def post(self, request, types):
        if types == 'add':
            ns = request.POST.get('ns').encode('utf-8')
            msg = request.POST.get('image').encode('utf-8')
            tags = request.POST.get('tags').encode('utf-8')
            rc = int(request.POST.get('rc').encode('utf-8'))
            env = request.POST.get('env').encode('utf-8')
            print(ns, msg, tags, rc, env)
            try:
                config.load_kube_config()
                extensions_v1beta1 = client.ExtensionsV1beta1Api()
                deploy = dp.create_deployment_object(tags=tags, images=msg, rc=rc, envs=env)
                dp.create_deployment(extensions_v1beta1, deploy, ns=ns)
            except Exception as e:
                return HttpResponse(e)
            # if msg == images:
            return HttpResponse('ok')
        if types =='delete':
            ns = request.POST.get('ns_name').encode('utf-8')
            dp_name = request.POST.get('dp_name').encode('utf-8')
            ret = {'status': 0}
            if dp_name is None:
                ret['status'] = 100
                ret['msg'] = 'ns_name or dp_name is None'
                return JsonResponse(ret)
            else:
                try:
                    config.load_kube_config()
                    extensions_v1beta1 = client.ExtensionsV1beta1Api()
                    dp.delete_deployment(extensions_v1beta1, ns=ns, images=dp_name)
                    ret['status'] = 0
                except Exception as e:
                    ret['msg'] = e
                return JsonResponse(ret)







