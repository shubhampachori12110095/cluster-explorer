
from datetime import datetime
from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand
from pyes import ES, TermQuery

from analysis.corpus import Corpus
from analysis.ingestion import DocumentIngester
from analysis.parser import ngram_parser


def load_docket(docket):
    c = ES(['localhost:9200'])
        
    docs = list()
    
    for r in c.search(TermQuery("docket_id", docket), size=1000000)['hits']['hits']:
        text = "\n".join([file['text'].encode('ascii', 'replace') for file in r['_source']['files'] if len(file['text']) > 0])
        metadata = dict([(key, str(value)) for (key, value) in r['_source'].items() if key != 'files' and value is not None])
        docs.append(dict(text=text, metadata=metadata))
    
    return docs

def ingest_docket(agency, docket, docs, ngrams=None):
    print "Beginning processing %s at %s" % (docket, datetime.now())
    
    c = Corpus(metadata=dict(docket=docket, agency=agency))
    if ngrams:
        i = DocumentIngester(c, parser=ngram_parser(int(options['ngrams'])))
    else:
        i = DocumentIngester(c)
    i.ingest(docs)
    
    print "Finished processing at %s" % datetime.now()
    print "Added %d documents in corpus %d" % (len(docs), c.id)

def get_dockets(agency):
    c = ES(['localhost:9200'])

    query = {
        "from": 0,
        "size": 0,
        "query": { "match_all" : {} },
        "facets": {
            "docket_id": {
                "terms": { "field": "docket_id", "size": 1000000 },
                "facet_filter": { "term": { "agency": agency } }
            }
        }
    }
    
    return [r['term'] for r in c.search(query)['facets']['docket_id']['terms'] if r['count'] >= 50]


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-n", "--ngrams", dest="ngrams"),
        make_option('-a', "--agency", dest="agency"),
        make_option('-d', "--docket", dest="docket"),
    )

    @transaction.commit_on_success
    def handle(self, **options):
        print "Loading data from ElasticSearch at %s" % datetime.now()
        
        if options.get('docket'):
            dockets = [options['docket']]
        else:
            dockets = get_dockets(options['agency'])
            
        for docket in dockets:
            docs = load_docket(docket)
            ingest_docket(options['agency'], docket, docs, options.get('ngrams'))

        print "Done."

    
