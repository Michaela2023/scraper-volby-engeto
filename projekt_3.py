"""
projekt_3.py: Election scraper
author: Michaela Řežábková
email: rezabkova.michaela@seznam.cz
discord: --
"""
import csv
import random
import sys
from time import gmtime, mktime
import requests
from bs4 import BeautifulSoup


def ArgsProcessing(argv):
    if len(argv) != 3:
        print("Wrong number of arguments. Exiting...")
        exit(1)
    return argv[1], argv[2]





if __name__ == '__main__':
    url, outFile = ArgsProcessing(sys.argv)
    #get the page
    page = requests.get(url)
    #check if the page was loaded correctly
    if page.status_code != 200:
        print("Error loading the page. Exiting...")
        exit(1)

    html_content = page.text

    # Create a BeautifulSoup object to analyze HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all links on the page with X in the text
    text_to_find = 'X'
    links_with_x = []
    for tr in soup.find_all('tr'):
        for td in tr.find_all('td'):
            link = td.find('a', string=text_to_find)
            if link:
                link = tr.find('a', string=tr.text.split("\n")[1])
                links_with_x.append((link,tr.text.split("\n")[1], tr.text.split("\n")[2]))

    # city or town or village
    villages = []
    for link in links_with_x:
        village = {}
        village["code"] = link[1]
        village["name"] = link[2]

        villageContent = requests.get("https://volby.cz/pls/ps2017nss/"+link[0]['href'])
        villageSoup = BeautifulSoup(villageContent.text, 'html.parser')
        try:
            villageNumbers = villageSoup.find_all('div', id='publikace')[0].find_all('tr')[2].text.split("\n")
        except IndexError:
            continue
        village["registered"] = villageNumbers[4]
        village["envelopes"] = villageNumbers[5]
        village["valid"] = villageNumbers[8]
        village["votesForParties"] = []
        #//*[@id="inner"]/div[1]/table/tbody/tr[3]/td[2]
        inner = villageSoup.find_all('div', id='inner')
        partiesData = inner[0].find_all('tr')
        for tr in partiesData:
            #find all first td
            party = {}
            row = tr.find_all('td')
            if row == [] or row[0].text == "-":
                continue
            party["number"] = row[0].text
            party["name"] = row[1].text
            party["votes"] = row[2].text
            party["percentage"] = row[3].text
            village["votesForParties"].append(party)
        villages.append(village)

        # Open the CSV file in write mode
        with open(outFile, 'w', newline='', encoding='utf-8') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            partiesHeader = []
            for p in villages[0]["votesForParties"]:
                partiesHeader = partiesHeader + [p["name"]]
            writer.writerow(["kód obce", "název obce", "voliči v seznamu", "vydané obálky", "platné hlasy"]+partiesHeader)

            # Write the data rows to the CSV file
            for vilage in villages:
                writer.writerow([vilage["code"], vilage["name"], vilage["registered"], vilage["envelopes"], vilage["valid"]] + [p["votes"] for p in vilage["votesForParties"]])
