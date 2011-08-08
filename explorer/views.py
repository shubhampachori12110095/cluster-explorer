from django.shortcuts import render_to_response
from django.http import HttpResponse
import settings
from cluster.hierarchy import *
import json
import StringIO
from helpers import doc_to_dict
from django.views.decorators.http import condition

all_docs = ClusterHierarchy(settings.DATA_ROOT)

def _get_params(step = None, cluster=None, doc=None):
    if step:
        step = int(step)
    else:
        step = 1
    if cluster:
        cluster = int(cluster)
    if doc:
        doc = int(doc)
    return {'step':step,'cluster':cluster,'doc':doc}

def _get_step(step = 1, cluster = 1):
    count = { # You can probably do this in the template
        "steps"     : len(all_docs),
        "clusters"  : len(all_docs[int(step)-1]),
    }
    clusters = [doc_to_dict(i,1,20) for i in all_docs[int(step)-1]]
    return {"clusters":clusters, "count":count} 

def _get_cluster(step = 1, cluster = 1, limit = 0):
    cluster_docs = all_docs[int(step)-1][int(cluster)-1]
    return_dict = doc_to_dict(all_docs[int(step)-1][int(cluster)-1],limit,20)
    return_dict['id'] = cluster
    return return_dict

def _get_doc(step = 1, cluster = 1, doc = 1):
    return_dict = doc_to_dict( [all_docs[int(step)-1][int(cluster)-1][int(doc)-1]] )
    return_dict['id'] = doc
    return return_dict

def index(request, step = None, cluster = None, doc = None):
    response_dict = {}
    response_dict['params']         = _get_params(step,cluster,doc)
    if doc:
        response_dict['doc']        = _get_doc(int(step),int(cluster),int(doc))        
    if cluster:
        #limit = int(request.GET.get('limit', 10))
        response_dict['cluster']    = _get_cluster(int(step),int(cluster))
    if step:
        response_dict['step']       = _get_step(int(step))
    else:
        response_dict['step']       = _get_step()

    return render_to_response("index.html",response_dict)

def api(request, step = None, cluster = None, doc = None):
    response_dict = {}
    response_dict['params']         = _get_params(step,cluster,doc)
    if doc:
        response_dict['doc']        = _get_doc(int(step),int(cluster),int(doc))
    elif cluster:
        try:
            limit = int(request.GET['limit'])
        except:
            limit = 0
        response_dict['cluster']    = _get_cluster(int(step),int(cluster), limit)
    elif step:
        response_dict['step']       = _get_step(int(step))
    else:
        response_dict['step']       = _get_step()

    response_dict = json.dumps(response_dict)
    return HttpResponse(response_dict, mimetype="application/json")

@condition(etag_func=None) #Django has a known bug with streaming HTTP responses- see https://code.djangoproject.com/ticket/7581. This is here in case this project ever ends up using middleware in a way that would break streaming, but it currently isn't.
def csv(request, step):
    response = HttpResponse(all_docs.stream_csv(int(step)), mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=step-%s.csv"%(step)
    return response