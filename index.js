const axios = require("axios");
const sqlite = import('sqlite-async');
const { appendFile } = require("fs");
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const csvWriter = createCsvWriter({
  path: './csv/data.csv',
  header: [
    { id: 'person_id', title: 'ID' },
    { id: 'name', title: 'Name' },
    { id: 'person_linkedin', title: 'Personal LinkedIn' },
    { id: 'email', title: 'Email' },
    { id: 'job_title', title: 'Job Title' },
    { id: 'person_link', title: 'Person Apollo Link' },
    { id: 'company_name', title: 'Company Name' },
    { id: 'company_link', title: 'Company Apollo Link' },
    { id: 'company_website', title: 'Company Website' },
    { id: 'company_linkedin', title: 'Company LinkedIn' },
    { id: 'company_twitter', title: 'Company Twitter' },
    { id: 'company_facebook', title: 'Company Facebook' },
    { id: 'location', title: 'Location' },
    { id: 'employees', title: 'Employees' },
    { id: 'industry', title: 'Industry' },
    { id: 'keywords', title: 'Keywords' },
    { id: 'phone_number', title: 'Phone Number' },
    { id: 'phone', title: 'Phone' },
    { id: 'personal_emails', title: 'Personal Emails' },
  ]
});

const API_KEY = "8IcH383WUImLf_4EzLFaMQ"
const FILTER_QUERY = "personTitles[]=owner&personTitles[]=founder&personTitles[]=ceo&personTitles[]=director&personTitles[]=c%20suite&personTitles[]=partner&personTitles[]=head%20of%20sales&personTitles[]=cmo&personTitles[]=cfo&personTitles[]=head%20of%20marketing&personTitles[]=operations%20director&personTitles[]=vp%20of%20development&personTitles[]=VP&personLocations[]=United%20Kingdom&organizationIndustryTagIds[]=5567e1887369641d68d40100&contactEmailStatus[]=verified";

let isDone = 0;
let isCompleted = 0;
const peopleList = [];

async function subprocess() {
  isCompleted = 0;
  while (1) {
    const people = peopleList.pop();
    if (people) {
      try {
        const response = await axios.post("https://api.apollo.io/api/v1/people/bulk_match", {
          api_key: API_KEY,
          reveal_personal_emails: true,
          details: bundle
        });
        const matches = response.data.matches;
        appendFile('matches.json', JSON.stringify(matches), (err) => {
          if (err) throw err;
          console.log('The "data to append" was appended to file!');
        });
        for (let i = 0; i < matches.length; i++) {
          const detail = matches[i];
          const raws = await db.all(`SELECT * FROM history WHERE pid=?`, [detail.id]);
          if (!raws.length) {
            const jsonData = [
              {
                person_id: detail.id,
                name: detail.name,
                person_linkedin: detail.linkedin_url,
                email: detail.email,
                job_title: detail.title,
                person_link: detail.twitter_url,
                company_name: detail.organization.name,
                company_link: detail.organization.blog_url,
                company_website: detail.organization.website_url,
                company_linkedin: detail.organization.linkedin_url,
                company_twitter: detail.organization.twitter_url,
                company_facebook: detail.organization.facebook_url,
                location: detail.organization.raw_address,
                employees: detail.organization.estimated_num_employees,
                industry: detail.organization.industry,
                keywords: detail.organization.keywords,
                phone_number: detail.organization.primary_phone,
                phone: detail.organization.phone,
                personal_emails: detail.personal_email
              }
            ];
            csvWriter.writeRecords(jsonData)
              .then(() => {
                console.log('JSON data appended to CSV file successfully');
              })
              .catch((error) => {
                console.error('Error occurred while appending JSON data to CSV file', error);
              });
            const result = await db.run(`INSERT INTO history (pid) VALUES(?)`, [detail.id]);
          }
        }
      } catch (e) {
        console.log("subprocess: ", e);
        break;
      }
    } else {
      if (isDone) {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
  isCompleted = 1;
}

async function thread() {
  data = {
    api_key: API_KEY,
    per_page: 25,
    page: 1,
    person_titles: [],
    person_locations: [],
    organization_ids: [],
    contact_email_status: [],
  }
  filter_items = FILTER_QUERY.split("&");
  for (let i = 0; i < filter_items.length; i++) {
    const filter = filter_items[i];
    key = filter.replace("[]", "").replace("%20", " ").split("=")[0].trim();
    value = filter.replace("[]", "").replace("%20", " ").split("=")[1].trim();
    if (key == "personTitles") {
      data.person_titles.push(value);
    } else if (key == "personLocations") {
      data.person_locations.push(value);
    } else if (key == "organizationIndustryTagIds") {
      data.organization_ids.push(value);
    } else if (key.indexOf("contactEmailStatus") >= 0) {
      data.contact_email_status.push(value);
    }
  }
  console.log("data=", data);
  isDone = 0;
  subprocess();
  let total_pages = 0;
  let page = 1
  let bundle = [];
  do {
    try {
      data.page = page;
      const response = await axios.post("https://api.apollo.io/v1/mixed_people/search", {
        api_key: '8IcH383WUImLf_4EzLFaMQ',
        per_page: 25,
        page: 1,
        person_titles: [
          'owner',
          'founder',
          'ceo',
          'director',
          'c suite',
          'partner',
          'head of%20sales',
          'cmo',
          'cfo',
          'head of%20marketing',
          'operations director',
          'vp of%20development',
          'VP'
        ],
        person_locations: [ 'United Kingdom' ],
        organization_ids: [ '5567e1887369641d68d40100' ],
        contact_email_status: [ 'verified' ]
      });
      console.log(response.data);
      const result = response.data;
      const people = result.people;
      appendFile('people.json', JSON.stringify(people), (err) => {
        if (err) throw err;
        console.log('The "data to append" was appended to file!');
      });
      if (!total_pages) {
        total_pages = result.pagination.total_pages;
      }
      for (let i = 0; i < people.length; i++) {
        bundle.push({
          "id": people[i].id
        });
        if (bundle.length == 10) {
          peopleList.push(bundle);
          bundle = [];
        }
      }
      page++;
      await new Promise((resolve) => setTimeout(resolve, 5000));
      ////////////////
      break;
///////////////
    } catch (e) {
      console.log("mainprocess: ", e);
      break;
    }
  } while (page <= total_pages);
  await new Promise((resolve) => setTimeout(resolve, 5000));
  isDone = 1;
  while (!isCompleted) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }
}

(async () => {
  const db = await (await sqlite).Database.open('./history.db');
  await db.run("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, pid TEXT);");
  await thread();
  await db.close();
})()