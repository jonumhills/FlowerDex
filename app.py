import os
import cv2
from flask import Flask, redirect, url_for, request, render_template,session
from keras.models import load_model
import numpy as np
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pandas as pd
import tensorflow as tf

#global model
global model,graph
def init():
    print("Loaading Model...")
    model=load_model('model.h5')
    model.summary()
    graph=tf.get_default_graph()
    print("Successfull")
    return model,graph
model,graph=init()



#Dictonary for flower class, medicinal values, IUCN websites for respective flower class
categories=["bluecrown passion flower","cyclamen persicum","echinacea angustifolia","garden nasturtium","lotus","nuragica columbine","nymphaea loriana","philodendron gloriosum","spear thistle","tillandsia lagensis"]

categories1=["bluecrown_passion_flower","cyclamen_persicum","echinacea_angustifolia","garden_nasturtium","lotus","nuragica_columbine","nymphaea_loriana","philodendron_gloriosum","spear_thistle","tillandsia_lagensis"]

medic={"bluecrown passion flower":"Passion Flower","lotus":"Indian Lotus","echinacea angustifolia":"Echinacea","spear thistle":"Milk Thistle"}

regions={"bluecrown passion flower":"Grown from Southern Europe to Central Asia, generally adapted to steppes and mountainous areas with temperate climate","cyclamen persicum":"Originates from Southern USA and New Mexico but it is a versatile plant grown around the world","echinacea angustifolia":"species are native to Asia, with smaller numbers native to Europe, North America, and northwestern Africa.","garden nasturtium":" species grow in tropical forests, but others can be found in semi-desert regions, near the seashore and in the tundra","lotus":"Originates from Southern Asia and Australia, these days it is commonly found in all aquatic cultures throughout the world","nuragica columbine":"Native to southwestern North America, tropical America, and South America","nymphaea loriana":"Most species grow in temperate and tropical areas. Species usually inhabits forests, grasslands, marshes and mountains.","philodendron gloriosum":"It is native to the Old World and is found from Cape Verde and the Canary Islands, Europe across to northern and eastern Africa, the Mediterranean, southwest Asia to southeast India","spear thistle":"Centred in the north temperate zone, native to the Mediterranean and central Asian areas.","tillandsia lagensis":"It usually inhabits grasslands, meadows, gardens, urban areas and areas near the roadsides.Native to Europe"}

scientific_names={"bluecrown passion flower":"Passiflora caerulea","cyclamen persicum":"Cyclamen_persicum ","echinacea angustifolia":"Echinacea_angustifolia","garden nasturtium":"Tropaeolum_majus","lotus":"Nelumbo Nucifera","nuragica columbine":"Aquilegia_nuragica","nymphaea loriana":"nymphaea_loriana","philodendron gloriosum":"Philodendron","spear thistle":"Cirsium vulgare","tillandsia lagensis":"tillandsia_lagensis"}


en_status={"bluecrown passion flower":"https://www.iucnredlist.org/species/179504/1580872","cyclamen persicum":"https://www.iucnredlist.org/species/135016/4052882","echinacea angustifolia":"https://www.iucnredlist.org/species/117909851/123324018","garden nasturtium":"https://www.iucnredlist.org/species/88503701/88503805","lotus":"https://www.iucnredlist.org/species/164281/1038562","nuragica columbine":"https://www.iucnredlist.org/species/61672/12520091","nymphaea loriana":"https://www.iucnredlist.org/species/81359075/81360324","philodendron gloriosum":"https://www.iucnredlist.org/species/129739546/129739550","spear thistle":"https://www.iucnredlist.org/species/22702200/93864664","tillandsia lagensis":"https://www.iucnredlist.org/species/182043/136070708"}

en_sts={"bluecrown passion flower":"Least Concern","cyclamen persicum":"Least Concern","echinacea angustifolia":"Least Concern","garden nasturtium":"Endangered","lotus":"Least Concern","nuragica columbine":"Critically Endangered","nymphaea loriana":"Endangered","philodendron gloriosum":"Vulnerable","spear thistle":"Endangered","tillandsia lagensis":"Data Deficient"}

medic_value=str()
p=int()

def remove_href_and_replacewith_children(tag):
    for a in tag.findAll('a'):
        a.replaceWithChildren()


# Define a flask app
app = Flask(__name__)
app.secret_key = "super secret key"
#Path to store all the uploaded images 
app.config["IMAGE_UPLOADS"] = "C:/Users/JONUMHILLS/fp1/static"


@app.route("/")
def index():
    
    return render_template("upload.html")

@app.route('/upload-image', methods=["GET","POST"])
def upload_image():
    
    path=str()
    path1=str()
    #getting the image and storing it into the respective path
    if request.method=="POST":
        if request.files:
            image=request.files["image"]
            print(image)
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            path=os.path.join(app.config["IMAGE_UPLOADS"], image.filename)
            #cv2.imread(image)
            path1=image.filename
    print(path)
    print(path1)
    print("image uploaded Predicting the flower....")
    #classifying the image first model is loaded and then the prediction is done
    cv2.imread(path)
    real_time_image=np.reshape(np.array(cv2.resize(cv2.imread(path),(100,100))),[1,100,100,3])
    #model = load_model('model.h5')
    #model.summary()
    with graph.as_default():
        k=model.predict(real_time_image)
    #print(k)
    max=np.amax(k)
    #print(max)
    number=list(np.where(k==max))
    p=int(number[1])
    print("flower is ",categories[p])
    print("Successfully classified")
    
    fname=str(categories[p])
    session['fn']=fname
    session['pos']=p
    #scientific name
    sc_name=scientific_names[categories[p]]
    
        
    #EndangeredStatus
    print("WebScraping Endangered status...")
    driver = webdriver.Chrome()
    url = en_status[categories[p]]
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    Endangered_status=str()
    count=0
    for i in soup.find_all("p", {"class": "card__data card__data--key card__data--accent"}):
        count+=1
        if(count==7):
            j=i.find("strong")
            print(j.text)
            Endangered_status=str(j.text)
    print("Successfully Scraped")
    
    return render_template("uploaded.html",name=fname,sn=sc_name,es=en_sts[categories[p]],user_image = path1)

@app.route('/flower-details', methods=["GET","POST"])
def flower_details():
    fn1=str()
    fn1=session.get('fn',None)
    #webscraping medic value
    print("webscraping medic value")
    print(fn1)
    #fn=g.pop('fname1',None)
    print(categories[p])
    if fn1 in medic:
        plantName=medic[fn1]
        API_URL = "http://www.remedieshouse.com/herbs/15-beautiful-flowering-plants-with-medicinal-uses/"
        page_response = requests.get(API_URL)
        #html parsing
        page_content = BeautifulSoup(page_response.content, "html.parser")
        #grabbing the data
        content = page_content.find_all("div", {'class': 'entry-content clearfix'})
        plantToDescriptionDict = {}
        #plantName = input("Enter the name of plant you want to know info about:\n")
        for tag in content:
            hTags = tag.find_all("h3")
            #print(hTags)
            remove_href_and_replacewith_children(tag)
            paraTags = tag.find_all("p")
            #print(paraTags)
            hc = 0
            for index in range(len(paraTags)):
                if not paraTags[index].find("img") and index != 0:
                    plantToDescriptionDict[hTags[hc].text.lower()] = paraTags[index].text
                    hc = hc + 1
        print(plantToDescriptionDict[plantName.lower()])
        medic_value=str(plantToDescriptionDict[plantName.lower()])
    else:
        print("No information Available")
        medic_value="No information Available"
    print("Successfully Scraped")

    #region
    print("getting regions...")
    main_region=regions[fn1]
    print("Done")
    #favourable conditions
    pp=session.get('pos',None)
    print("getting favourable conditions....")
    l=["Sun Needs", "Soil Needs","Height"]
    mod_name = categories1[pp]
    with open("fav_cond.txt","r+") as f3:
        for lines in f3:
            if mod_name in lines:
                details = lines.split()
                l.append (details[1])
                l.append (details[2])
                l.append (details[3])
    print("Done")            
                
    return render_template("flower_details.html",m=medic_value,mr=main_region,data1=l[0],data2=l[1],data3=l[2],data4=l[3],data5=l[4],data6=l[5])

    


if __name__ == '__main__':
    app.run(debug=True)