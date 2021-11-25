from pprint import pprint
from utils import emit
import csv
csv.register_dialect('excel', quoting=csv.QUOTE_MINIMAL)
def print_work_item(work_item):
    emit(
        "{0} {1}: {2}".format(
            work_item.fields["System.WorkItemType"],
            work_item.id,
            work_item.fields["System.Title"]
        )
    )


def writeToFile(workItems, ids):
  with open('msp-import.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Unique ID", "Outline Level",	"Name",	"Resource Names",	"Duration",	"Unique ID Predecessors","% Complete"]

    writer = csv.DictWriter(csvfile,dialect='excel', fieldnames=fieldnames)
    writer.writeheader()
    # pprint(len(workItems))
    rows = []
    unestimated = []
    untracked_deps = []
    unassigned = []
    for work_item in workItems:
        # print_work_item(work_item)
        level = 3
        if work_item.fields['System.WorkItemType'] == "Epic":
          level = 1
        if work_item.fields['System.WorkItemType'] == "Feature":
          level = 2
        name = "Missing title"
        if work_item.fields and 'System.Title' in work_item.fields:
          name = str(work_item.id) + " - " + work_item.fields['System.Title']
        points = None
        creator = "Creator"
        if 'System.CreatedBy' in work_item.fields :
          creator = work_item.fields['System.CreatedBy']['displayName']
     
        assignee = "Unassigned"
        if 'System.AssignedTo' in work_item.fields:
          if level == 3:
            assignee = work_item.fields['System.AssignedTo']['displayName']
        else: 
          unassigned.append(creator + "(creator),\t\t" + name)
        
        
        complete = 0.0
        if work_item.fields and 'System.State' in work_item.fields:
          if work_item.fields['System.State'] in ["Closed", "Removed", "Resolved"]:
            complete = 1.0

        
  
        if 'Microsoft.VSTS.Scheduling.StoryPoints' in work_item.fields:
          points = work_item.fields['Microsoft.VSTS.Scheduling.StoryPoints']
        else:
          points = 1
          if level == 3:
            unestimated.append(assignee + "," + name)

        predecessors = []
        if (work_item.relations):
          for r in work_item.relations:
            # pprint(r.rel)
            if r.rel == 'System.LinkTypes.Dependency-Reverse':
              # pprint(r.url)
              id = r.url.split("/")[-1]
              if int(id) in ids:
                # print("TRAKCING dependency " + str(id))
                predecessors.append(id)
              else:
                untracked_deps.append(id)
                print("FOUND UNTRACKED dependency " + str(id))
        # print(",".join(predecessors))
        d = {'Unique ID': work_item.id, 
          'Outline Level': level,
          'Name': name,
          'Resource Names': assignee,
          'Duration': points,
          'Unique ID Predecessors': str(",".join(predecessors)),
          '% Complete': complete
        }
        rows.append(d)
    print("Untracked Dependencies -----------------------")
    print("\n".join(untracked_deps))
    print("Unestimated -----------------------")
    print("\n".join(unestimated))
    print("Unassigned -----------------------")
    print("\n".join(unassigned))
    writer.writerows(rows)