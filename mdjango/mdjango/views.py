from django.http import HttpResponse
import json
from mova.models import *
from visualization.models import *
from mdjango.runspider import thread


def handle(f_name, f_director, f_actor):
    ans = []
    fid = []
    if f_name != '0':#按照影片名要求搜索数据库
        op = {}
        it = Film.objects.get(name=f_name)
        fid.append(it.filmid)
    else:
        for item in Film.objects.all().values_list('filmid'):
            fid.append(int(list(item)[0]))
    if f_director != '0':#按照导演名要求搜索数据库
        res = Director.objects.filter(name=f_director)
        fid1 = []
        for it in res:
            if it.filmid in fid:
                fid1.append(it.filmid)
        fid = fid1
    if f_actor != '0':#按照演员名要求搜索数据库
        res = Actor.objects.filter(name=f_actor)
        fid1 = []
        for it in res:
            if it.filmid in fid:
                fid1.append(it.filmid)
        fid = fid1
    for it in fid:#将搜索结果装成字典写入jason文件中，同时向前端返回jason格式的数据
        target = Film.objects.get(filmid=it)
        op = {}
        op['name'] = target.name
        op['type'] = target.type
        op['score_rate'] = target.score_rate
        op['score_num'] = target.score_num
        op['date'] = target.date
        op['boxoffice'] = target.boxoffice
        op['day_boxoffice'] = target.day_boxoffice
        op['week_boxoffice'] = target.week_boxoffice
        op['score'] = target.score
        op['actor'] = []
        op['director'] = []
        res = Actor.objects.filter(filmid=it)
        for uu in res:
            op['actor'].append(uu.name)
        res = Director.objects.filter(filmid=it)
        for uu in res:
            op['director'].append(uu.name)
        ans.append(op)
    json_str = json.dumps(ans)
    with open('data.json','wb') as j:
        j.write(json_str.encode())
    return json_str


# 接口函数
def movie(request):
    if request.method == 'POST':  # 当提交表单时
        dic={}
        # 判断是否传参
        if request.POST:
            a= request.POST.get('a', -1)
            #b = request.POST.get('b')
            # 判断参数中是否含有a和b
            if int(a) == -1:
                return HttpResponse('参数错误')
            elif int(a) == 1:
                film = request.POST.get('film', '')#search
                actor = request.POST.get('actor', '')
                director = request.POST.get('director', '')
                dic = handle(film, director, actor)
                return HttpResponse(dic)
            elif int(a) == 2:
                #visualization
                func_selected = request.POST.get('func_selected', '0')
                year = request.POST.get('year', '0')
                quarter = request.POST.get('quarter','0')
                month = request.POST.get('month', '0')
                top_x = int(request.POST.get('top_x', 0))
                print(func_selected, year, quarter, month, top_x)
                data_dict = data_visualization(func_selected, year, quarter, month, top_x)
                data_json = json.dumps(data_dict)
                return HttpResponse(data_json)
            elif int(a) == 3:
                #save chart
                chart_download = str(request.POST.get('chart_download'))
                info = save_charts_as_pdf(chart_download)
                info = json.dumps(info)
                return HttpResponse(info)
            elif int(a) == 4:
                spider_start = request.POST.get('start', 0)
                if spider_start:
                    thread(spider_start)
                    msg = 'OK'
                    msg = json.dumps(msg)
                    return HttpResponse(msg)
                else:
                    return HttpResponse('爬取失败:-(')
            else:
                return HttpResponse('无效功能')
        else:
            return HttpResponse('输入为空')
 
    else:
        return HttpResponse('方法错误')
    
