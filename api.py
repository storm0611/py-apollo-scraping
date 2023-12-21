import os
import json
import time
from multiprocessing import Queue
import threading
from requests import Session, post
from dotenv import load_dotenv
from main import export_one
from database import my_sqlite
from datetime import datetime

load_dotenv()

query_filter = os.environ.get("FILTER_QUERY")
api_key = os.environ.get("API_KEY")
people_queue = Queue()
session = Session()
session.headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache"
}
main_completed = 0
sub_completed = 0

def send_people_requests(data):
    print("filter data = ", data)
    response = post(
        url="https://api.apollo.io/v1/mixed_people/search", 
        params={
    "api_key": "8IcH383WUImLf_4EzLFaMQ",
    "per_page": 25,
    "page": 1,
    "contact_email_status": ["verified"],
    "person_locations": ["United Kingdom"],
    "person_titles": [
        "owner",
        "founder",
        "ceo",
        "director",
        "c suite",
        "partner",
        "head of sales",
        "cmo",
        "cfo",
        "head of marketing",
        "operations director",
        "vp of development",
        "VP"
    ]
}
    )
    print(response.json())
    if response.status_code == response.ok:
        return response.json()
    return None

def send_bulk_people_requests(data):
    response = session.post(
        url="https://api.apollo.io/api/v1/people/bulk_match", 
        data=data
    )
    if response.status_code == response.ok:
        return response.json()
    print(response)
    return None

def sub_proc():
    global sub_completed
    sub_completed = 0
    while True:
        while people_queue.empty():
            if main_completed:
                sub_completed = 1
                return
            time.sleep(2)
        bundle = people_queue.get(block=False)
        response = send_bulk_people_requests(data={
            "api_key": api_key,
            "reveal_personal_emails": True,
            "details": bundle
        })
        time.sleep(2)
        matches = response["matches"]
        with open(f'matches{int(datetime.now().timestamp())}.json', 'w') as outfile:
            json.dumps(matches, outfile)
        for detail in matches:
            if not len(my_sqlite.select(pid=detail["id"])):
                export_one(data={
                    "person_id": detail["id"],
                    "name": detail["name"],
                    "person_linkedin": detail["linkedin_url"],
                    "email": detail["email"],
                    "job_title": detail["title"],
                    "person_link": detail["twitter_url"],
                    "company_name": detail["organization"]["name"],
                    "company_link": detail["organization"]["blog_url"],
                    "company_website": detail["organization"]["website_url"],
                    "company_linkedin": detail["organization"]["linkedin_url"],
                    "company_twitter": detail["organization"]["twitter_url"],
                    "company_facebook": detail["organization"]["facebook_url"],
                    "location": detail["organization"]["raw_address"],
                    "employees": detail["organization"]["estimated_num_employees"],
                    "industry": detail["organization"]["industry"],
                    "keywords": detail["organization"]["keywords"],
                    "phone_number": detail["organization"]["primary_phone"],
                    "phone": detail["organization"]["phone"],
                    "personal_emails": detail["personal_emails"]
                })
                my_sqlite.insert(pid=detail["id"])
                ###########################
                sub_completed = 1
                return
                #################

if __name__ == "__main__":
    data = {
        "api_key": api_key,
        "per_page": 25,
        "page": 1
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
    results = send_people_requests(data=data)
    if not results:
        print("No Results")
        exit(0)
    print("Search People Results = ", results)
    partial_results_limit = results["partial_results_limit"]
    pagination = results["pagination"]
    people = results["people"]
    # with open('my_data.json', 'r') as f:
    #     my_dict = json.load(f)
    main_completed = 0
    t1 = threading.Thread(target=sub_proc)
    t1.start()
    page = 1
    bundle = []
    while True:
        with open(f'people{int(datetime.now().timestamp())}.json', 'w') as outfile:
            json.dumps(people, outfile)
        for person in people:
            bundle.append({
                "id": person["id"]
            })
            if len(bundle) == 10:
                try:
                    people_queue.put(bundle, block=False)
                except:
                    pass
                bundle = []
        page += 1
        # if page > pagination.get("total_pages"):
        if page > 2:
            break
        data["page"] = page
        results = send_people_requests(session=session, data=data)
        time.sleep(5)
        people = results["people"]
    main_completed = 1
    while not sub_completed:
        time.sleep(5)
