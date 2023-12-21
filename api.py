import os
import json
import time
from multiprocessing import Queue
from requests import Session
from dotenv import load_dotenv
load_dotenv()

people_queue = Queue()
completed = 0

def send_people_requests(session: Session, data: dict):
    response = session.post(
        url="https://api.apollo.io/v1/mixed_people/search", 
        data=data
    )
    print(response)
    if response.status_code == response.ok:
        return response.json()
    raise Exception(response.json())

def send_bulk_people_requests(session: Session, data: dict):
    response = session.post(
        url="https://api.apollo.io/v1/mixed_people/search", 
        data=data
    )
    print(response)
    if response.status_code == response.ok:
        return response.json()
    raise Exception(response.json())

if __name__ == "__main__":
    query_filter = os.environ.get("FILTER_QUERY")
    api_key = os.environ.get("API_KEY")
    data = {
        "api_key": api_key,
        "per_page": 25
    }
    for filter in query_filter.split("&"):
        key = filter.replace("[]", "").replace("%20", " ").split("=")[0]
        value = filter.replace("[]", "").replace("%20", " ").split("=")[1]
        if key == "personTitles":
            if not "person_titles" in data.keys():
                data["person_titles"] = []
            if not value in data["person_titles"]:
                data["person_titles"].append(value)
        elif key == "personLocations":
            if not "person_locations" in data.keys():
                data["person_locations"] = []
            if not value in data["person_locations"]:
                data["person_locations"].append(value)
        elif key == "organizationIndustryTagIds":
            if not "organization_ids" in data.keys():
                data["organization_ids"] = []
            if not value in data["organization_ids"]:
                data["organization_ids"].append(value)
        elif key == "contactEmailStatus":
            if not "contact_email_status" in data.keys():
                data["contact_email_status"] = []
            if not value in data["contact_email_status"]:
                data["contact_email_status"].append(value)
    print("filter data = ", data)
    session = Session()
    try:
        results = send_people_requests(session=session, data=data)
        partial_results_limit = results.get("partial_results_limit")
        pagination = results.get("pagination")
        people = results.get("people")
        with open('people.json', 'w') as outfile:
            json.dumps(people, outfile)
        # with open('my_data.json', 'r') as f:
        #     my_dict = json.load(f)
        page = 1
        bundle = []
        while True:
            for person in people:
                bundle.append({
                    "id": person["id"]
                })
                if len(bundle) == 10:
                    people_queue.put(bundle)
                    bundle = []
            page += 1
            if page > pagination.get("total_pages"):
                break
            results = send_people_requests(session=session, data=data)
            people = results.get("people")
        while not completed:
            time.sleep(5)
    except:
        print("Response Error")

    