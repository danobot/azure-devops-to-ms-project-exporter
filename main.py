from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint
import csv
import datetime
import logging
from utils import emit
from writer import print_work_item
from azure.devops.v5_1.work_item_tracking.models import Wiql
from writer import writeToFile
# Fill in with your personal access token and org URL
personal_access_token = ''
organization_url = ''

# Create a connection to the org
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

discovered_samples = {}
def resource(decorated_resource):
    def decorate(sample_func):
        def run(*args, **kwargs):
            emit("Running `{0}.{1}`".format(sample_func.__module__, sample_func.__name__))
            sample_func(*args, **kwargs)

        run.__name__ = sample_func.__name__

        if sample_func.__module__ not in discovered_samples:
            logger.debug("Discovered area `%s`", sample_func.__module__)
            discovered_samples[sample_func.__module__] = {}

        area_samples = discovered_samples[sample_func.__module__]
        if decorated_resource not in area_samples:
            logger.debug("Discovered resource `%s`", decorated_resource)
            area_samples[decorated_resource] = []

        logger.debug("Discovered function `%s`", sample_func.__name__)
        area_samples[decorated_resource].append(run)

        return run
    return decorate


"""
WIT samples
"""


logger = logging.getLogger(__name__)

def wiql_query():
    wit_client = connection.clients.get_work_item_tracking_client()
    wiql = Wiql(
        query="""
        select [System.WorkItemType],
        [System.Title],
        [System.State],
        [System.Tags],
        [System.Id],
        [System.AssignedTo],
        [Microsoft.VSTS.Scheduling.StoryPoints] 
        from WorkItems
        where [System.Id] = 10288
        order by [System.ChangedDate] desc"""
    )
    wiql_results = wit_client.query_by_id(id="your saved query id here")

    results = []
    ids = []
    work_items = []
    for l in wiql_results.work_item_relations:
        results.append(l.target)
        work_items.append(wit_client.get_work_item(int(l.target.id), expand="Relations"))
        ids.append(int(l.target.id))
    emit("results: {0}".format(len(results)))
    emit("ids: {0}".format(len(ids)))
    # pprint.pprint(ids)
    writeToFile(work_items, ids)

    # wiql_results = wiql_results.work_item_relations
   


workItems = wiql_query()
