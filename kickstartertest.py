import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
import json
import clearbit
import urllib.parse
from datetime import date
import datetime
import analytics

#api key for a track call in segment.io
analytics.write_key = 'Q6QwJI6Zo7Alfp5UxKoKncwh0xu3nk2O' 

#api key for clearbit
clearbit.key = 'sk_c10c427f21b01bc129b1d9a87de217b3' 

#defining variables to store the extrated data
kickstarter_id=""
kickstarter_backers=""
kickstarter_description=""
kickstarter_pledged=0
kickstarter_raised=0
kickstrter_enddate=""
kickstarter_owner=""

first_name=""
last_name=""
email=""
hunter_title=""
full_name=""
clearbit_title=""
company_name=""
company_industry=""

a=[]*10000
results={'leads':a}
stop_process=""
job_titles_ref=["CUSTOMER SERVICE","CUSTOMER SUCCESS",


def kickstarter_leadgen(newdate,pagination):
 kickstarter = 'https://www.kickstarter.com/discover/advanced?state=successful&sort=end_date&seed=2701396&page='+str(pagination)
 driver=webdriver.Chrome('/Users/vicky/Downloads/chromedriver')
 driver.get(kickstarter)
 time.sleep(10)
 html=driver.page_source

 soup=BeautifulSoup(html,'html.parser')
 
 #div element containing all the kickstarter project cards that you see in the website
 data=soup.find_all('div',{'class':'js-project-group'}) 
 
 #div elements corresponding all the individual kickstarter projects
 project_card=data[1].find_all('div',{'class':'js-track-project-card'})
 
 #looping throuh all the project cards in that respective page
 for p in range (0,len(project_card)):
  print()
  
  kickstarter_id=project_card[p].get('data-project_pid')  
  kickstarter_backers=project_card[p].get('data-project_backers_count')
  kickstarter_description=project_card[p].get('data-project_description')
  kickstarter_pledged=float(project_card[p].get('data-project_pledged'))
  kickstarter_raised=float(project_card[p].get('data-project_percent_raised'))*(kickstarter_pledged/100)
  
  #acquiring the link to move to a page within the project card to secure the creator and end date
  data2=project_card[p].find('div',{'class':'relative self-start'})

  #more_info provide the link to the page with the date and creator
  more_info=data2.find('a').get('href') #more_info provide the link to the page with the date and creator
  
  #opening chromedriver to scrape dynamic webpages of the respective kickstarter project
  driver1=webdriver.Chrome('/Users/vicky/Downloads/chromedriver')
  driver1.get(more_info)
  time.sleep(10)
  html2=driver1.page_source
  soup2=BeautifulSoup(html2,'html.parser')
  
  project_createrdata=soup2.find('div',{'class':'creator-name'})
  
  #get the name of the project creator
  kickstarter_owner=project_createrdata.find('a').text 

  #page path to navigate to the project creator's bio
  more_info2=project_createrdata.find('a').get('href') 

  #end date of the kickstarter project
  kickstrter_enddate=soup2.find('time',{'class':'js-adjust-time'}).text 
  print(kickstrter_enddate)
  
  
  if(str(kickstrter_enddate)!= newdate):
   kickstrter_enddate=str(kickstrter_enddate)
   pos1=kickstrter_enddate.find(" ") 
   pos2=kickstrter_enddate.find(",")
   pos3=newdate.find(" ")
   pos4=newdate.find(",")


   slice1=slice(pos1,pos2)
   slice2=slice(pos3,pos4)

   print(kickstrter_enddate[slice1])
   print(newdate[slice2])

   if(int(kickstrter_enddate[slice1])-1==int(newdate[slice2])):
    #closing the chrome webpage since the project finished today
    driver.close() 
    kickstarter = 'https://www.kickstarter.com/discover/advanced?state=successful&sort=end_date&seed=2701396&page='+str(pagination)
    driver=webdriver.Chrome('/Users/vicky/Downloads/chromedriver')
    driver.get(kickstarter)
    time.sleep(10)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    data=soup.find_all('div',{'class':'js-project-group'}) 
    project_card=data[1].find_all('div',{'class':'js-track-project-card'})
    continue
   else:
    print("This is an older date")
    stop_process=str(kickstrter_enddate)
    print(stop_process)
    #closing the chrome webpage since the dates don't match
    driver.close()
    return kickstrter_enddate
    break
  
  
  #closing the chrome webpage after extraction is complete
  driver1.close() 

  #opening chromedriver to scrape dynamic webpages of the respective kickstarter project's owner

  #building the url to navigate to the project creator's bio
  owner_infourl="https://www.kickstarter.com/"+more_info2 
  driver2=webdriver.Chrome('/Users/vicky/Downloads/chromedriver')
  driver2.get(owner_infourl)
  time.sleep(10)
  html3=driver2.page_source
  
  soup3=BeautifulSoup(html3,'html.parser')

  #Parent element of the element hosting the websites
  website_data=soup3.find('div',{'class':'pt3 pt7-sm mobile-hide'})  
  
  if(website_data is not None):

   #eliminating those creators without any websites linked to their profile
   if(website_data.find('h4').text.strip() =="Websites"): 
    kickstarter_domain=website_data.find('ul',{'class':'links list f5 bold'}).find_all('li')
  else:
   kickstarter_domain=""     

  #check to filter those without domains and start fetching data from our APIs
  if(kickstarter_domain != ""): 
   
   for z in range(len(kickstarter_domain)):
    
    website=kickstarter_domain[z].find('a').text.strip()

    #using the website to check website technologies using Whatcms
    whatcms_params = {'key':'7588b96ce73bff1c0c0cc77abb9f550a514e515449a2219acf51c4d53f724d686289b6',
                      'url':website
                      }
    whatcms ="https://whatcms.org/API/Tech?"
    
    whatcms_finalurl=whatcms+str(urllib.parse.urlencode(whatcms_params)) 
    
    whatcms_response = requests.get(whatcms_finalurl)
    time.sleep(10)
    domaintech_data = whatcms_response.text
    whatcms_data = json.loads(domaintech_data)
    
    
    if(len(whatcms_data['results'])!= 0):
     for x in range(len(whatcms_data['results'])):

      #filtering websites that use shopify or any other e-commerce website building blocks in their domain
      if ((whatcms_data['results'][x]['name']=='Shopify'
           or whatcms_data['results'][x]['name']=='WooCommerce'
           or whatcms_data['results'][x]['name']=='EasyDigitalDownloads'
           or whatcms_data['results'][x]['name']=='Weebly')):
       print("This company uses Shopify")
       
       #fetching all emails from that domain using hunter.io
       hunter='https://api.hunter.io/v2/domain-search?'
       hunter_params={'domain':website,
                      'api_key':'2ad4425fb4cba67e8ad0833c6da88a03f8598866',
                      'limit':'100'
                      }
       hunter_finalurl=hunter+str(urllib.parse.urlencode(hunter_params))
       
       hunter_response = requests.get(hunter_finalurl)
       domain_data = hunter_response.text
       hunter_data = json.loads(domain_data)
       
       for y in range (len(hunter_data['data']['emails'])):

        #filtering out ony the 'valid' or 'nominative' email addresses
        if (hunter_data['data']['emails'][y]['confidence']>75):
         
         first_name=hunter_data['data']['emails'][y]['first_name']
         last_name=hunter_data['data']['emails'][y]['last_name']
         email=hunter_data['data']['emails'][y]['value']
         hunter_title=hunter_data['data']['emails'][y]['position']
         
         #using clearbit API to enrich the potential lead's information
         clearbit_response = clearbit.Enrichment.find(email=hunter_data['data']['emails'][y]['value'], stream=True)

         #using clearbit API to enrich the potential lead's company information
         company_data = clearbit.Company.find(domain=website,stream=True)
         

         if(clearbit_response['person'] is not None):
          full_name=clearbit_response['person']['name']['fullName']
          clearbit_title=clearbit_response['person']['employment']['title']
          company_name=company_data['name']
          company_industry=company_data['category']['industryGroup']
         
         if(clearbit_response['person'] is None):
          full_name=""
          clearbit_title=""
          company_name=""
          company_industry=""
         
         # do a screening of Jobtitles...................................VERY IMPORTaNT
         #for j in (len(job_titles_ref)):
          #if(job_title_ref[j] in hunter_title.upper() or job_title_ref[j] in clearbit_title.upper()):

         results['leads'].append({'project_id':kickstarter_id,
                                  'backers':kickstarter_backers,
                                  'description':kickstarter_description,
                                  'pledged':kickstarter_pledged,
                                  'raised':kickstarter_raised,
                                  'enddate':kickstrter_enddate,
                                  'owner':kickstarter_owner,
                                  'firstName':first_name,
                                  'lastName':last_name,
                                  'fullName':full_name,
                                  'Email':email,
                                  'title1':hunter_title,
                                  'title2':clearbit_title,
                                  'compnayName':company_name,
                                  'industry':company_industry
                                  })  
         analytics.track('email','kickstarter-campaign-completed',
                         {'project_id':kickstarter_id,
                          'backers':kickstarter_backers,
                          'description':kickstarter_description,
                          'pledged':kickstarter_pledged,
                          'raised':kickstarter_raised,
                          'enddate':kickstrter_enddate,
                          'owner':kickstarter_owner
                          })
         
         #send lead data to the respective campaign in sendinblue
         sendinblue = "https://api.sendinblue.com/v3/contacts"

         payload = {
             "email":email,
             "attributes":{"PRENOM": first_name,
                           "NOM": last_name,
                           "ENTERPRISE": company_name,
                           "KICKSTARTER_PROJECT_ID":kickstarter_id,
                           "KICKSTARTER_AMOUNT_RAISED":kickstarter_raised,
                           "KICKSTARTER_PLEDGED":kickstarter_pledged,
                           "KICKSTARTER_DESCRIPTION":kickstarter_description
                           },
             "listIds": [116],
             "updateEnabled": False
         }
         headers = {
             "Accept": "application/json",
             "Content-Type": "application/json",
             "api-key": "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"
         }

         sendinblue_response = requests.request("POST", sendinblue, json=payload, headers=headers)
        print()
        
   #closing all active chrome webdrivers       
   driver2.close()
   driver.close()
    
   #opening a new chrome wedriver to continue extracting
   driver=webdriver.Chrome('/Users/vicky/Downloads/chromedriver')
   driver.get(kickstarter)
   time.sleep(10)
   html=driver.page_source
   soup=BeautifulSoup(html,'html.parser')
   data=soup.find_all('div',{'class':'js-project-group'})
   print(len(data))
   project_card=data[1].find_all('div',{'class':'js-track-project-card'})
   

today = date.today()
yesterday = today - datetime.timedelta(days=1)
year = yesterday.strftime("%Y")
month = yesterday.strftime("%B") 
day = yesterday.strftime("%d")
newdate=str(month+" "+day+","+" "+year)
print(newdate)

stop_process=newdate


for w in range(20):
 stop_process=kickstarter_leadgen(newdate,w+1)
 if (stop_process!=newdate):
  
  break

 else:
  kickstarter_leadgen(newdate,w+1)
 
 
 
#printing the results of the case stuudy

print(results)
json_dump = json.dumps(results)
print(json_dump)

with open('kickstarter_results.json','w') as json_file:
 json.dump(results,json_file)


  

 



