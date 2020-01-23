from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt 
def hello(request):
    if request.method == "POST":
        import requests, json
        import psycopg2
        conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=12345")
        cur = conn.cursor()
        
        json_data1 = json.loads(request.body) # request.raw_post_data w/ Django < 1.4
        url = "https://yandex.ru/maps/195/ulyanovsk/routes/minibus_61/796d617073626d313a2f2f7472616e7369742f6c696e653f69643d3139355f36315f6d696e696275735f726f6164636f6e73756c79616e6f76736b266c6c3d34382e32393533343425324335342e323732363338266e616d653d363126723d3333373326747970653d6d696e69627573/?clid=2270456&ll=48.295806%2C54.283906&z=14"
        if "url" in json_data1:
            url = json_data1["url"]
        r_id = int(url.split('minibus_')[1].split('/')[0])
        response = requests.get(url)
        htmlSource = response.text

        d = htmlSource.split('<script type="application/json" class="config-view">')[1].split('</script>')[0]

        data = json.loads(d)
        djson = data["masstransitLine"]["features"][0]["features"]

        count = 0
        
        
        
        dq={"point":[]}
        #dq["point"] = []
        
        for j in djson:
            if "properties" in j:
                qq = "select max(id) from mts_routepoint;"
                cur.execute(qq)
                max_count = cur.fetchall()
                max_count = max_count[0][0]
                if max_count:
                    count = max_count+1
                name = j["properties"]["name"]
                point = 'SRID=4326;POINT ({})'.format(' '.join([str(i) for i in j["geometries"][0]["coordinates"] ]))
                
                dq["point"].append({'point':point,'name':name})
                
                cur.execute(u"""INSERT INTO mts_routepoint (id, name, route_id, next_point_id, prev_point_id, point)
                VALUES (%s,%s,%s,%s,%s, %s)""",(count, name, r_id, count+1, max_count, point))
                conn.commit()
                count +=1
                
        return JsonResponse(dq)

#@csrf_exempt
def route(request, route_id):
    if request.method == "GET":
        import psycopg2
        conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=655477")
        cur = conn.cursor()
        cur.execute("""SELECT * FROM mts_routepoint WHERE route_id = {}""".format(route_id))
        data = cur.fetchall()
        out_q={"points":[]}
        for i in data:
            out_q["points"].append(
                {'id':i[0],
                'name':i[1],
                'route_id':i[2],
                'next_point_id':i[3],
                'prev_point_id':i[4],
                'point':i[5]}
                )
        return JsonResponse(out_q)
        #return HttpResponse()
        
        
