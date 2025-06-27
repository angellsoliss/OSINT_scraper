import requests, csv
from bs4 import BeautifulSoup
from datetime import datetime
import os
from sentence_transformers import SentenceTransformer, util

def scorer(score):
    if score >= 0.20:
        return f"HIGH :{score}"
    elif score >= 0.10:
        return f"MEDIUM: {score}"
    else:
        return f"NOT RELEVANT: {score}"


def scrapeGoogle(keyword):
    articles = []
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    #set up AI for relevancy scoring
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    #include multiple domains to compare
    reference1 = (
        "phishing, spear phishing, social engineering, credential harvesting, email lures, "
        "BEC, business email compromise, QR code phishing, fake login page, MFA fatigue, SVG phishing"
    )

    reference2 = (
        "ransomware, data encryption, ransom note, extortion, file locker, decryptor key, double extortion, "
        "RaaS, ransomware-as-a-service, data leak site, payload delivery, crypto demand"
    )

    reference3 = (
        "zero-day, exploit, CVE, patch, vulnerability disclosure, remote code execution, privilege escalation, "
        "unpatched software, initial access vector, memory corruption, buffer overflow"
    )

    reference4 = (
        "OSINT tools, Shodan, passive reconnaissance, threat intelligence feeds, social media monitoring, "
        "domain enumeration, metadata extraction, WHOIS, Google dorking, Maltego, FOCA, email harvesting"
    )

    reference5 = (
        "leaked credentials, dark web, data breach, identity theft, stolen passwords, info stealer, credential dump, "
        "combo list, stealer logs, underground forums, account takeover"
    )

    reference6 = (
    "DDoS, distributed denial of service, network flood, amplification attack, volumetric attack, "
    "botnet, HTTP flood, L7 attack, record-breaking attack, terabit spike"
    )

    reference7 = (
        "AI-powered threats, LLM abuse, adversarial prompts, prompt injection, AI hallucination, synthetic phishing, "
        "deepfake social engineering, GenAI threats, automated reconnaissance"
    )

    reference8 = (
        "supply chain attack, third-party breach, vendor compromise, software dependency attack, "
        "package manager exploit, malicious library, backdoor installer"
    )

    reference9 = (
        "cloud security, SaaS misconfiguration, insecure APIs, hybrid cloud, cloud ransomware, identity federation risk, "
        "cloud workload protection, S3 leak, Azure, AWS, GCP"
    )

    reference10 = (
        "malware, trojan, spyware, rootkit, worm, loader, dropper, backdoor, RAT, keylogger, malicious binary"
    )

    reference_vector1 = model.encode(reference1)
    reference_vector2 = model.encode(reference2)
    reference_vector3 = model.encode(reference3)
    reference_vector4 = model.encode(reference4)
    reference_vector5 = model.encode(reference5)
    reference_vector6 = model.encode(reference6)
    reference_vector7 = model.encode(reference7)
    reference_vector8 = model.encode(reference8)
    reference_vector9 = model.encode(reference9)
    reference_vector10 = model.encode(reference10)

    #format user query into searchable url
    query = keyword.strip().replace(" ", "+")
    url = f"https://www.google.com/search?q={query}&gl=us&tbm=nws&num=100"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    #create timestamp for csv file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #check if scraped folder exists
    if not os.path.exists("scraped"):
        os.makedirs("scraped")
    
    #define full file path
    file_path = os.path.join("scraped", f'scraped_{query}_{timestamp}.csv')

    #create csv file with timestamp in scraped folder
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        writer.writerow(['Link', 'Title', 'Snippet', 'Date', 'Source', 'Relevancy Rating (Closer to 1.0 = More Relevant)'])

        #fetch each individual article box
        for a in soup.select("div.SoaBEf"):
            #each article box = SoaBEf
            #source = MgUUmf span
            #title = n0jPhd
            #snippet = GI74Re
            #date = OSrXXb
            #fetch information and format as dictionary, append dict to articles list
            link = a.find('a')
            title = a.select_one('.n0jPhd')
            snippet = a.select_one('.GI74Re')
            date = a.select_one('.OSrXXb')
            source = a.select_one('.MgUUmf span')

            #check if all elements of dictionary are present
            if link and title and snippet and date and source:
                dictionary =  {
                        "Link" : link['href'],
                        "Title" : title.get_text(),
                        "Snippet" : snippet.get_text(),
                        "Date" : date.get_text(),
                        "Source" : source.get_text()
                    }
                articles.append(dictionary)

                #vectorize snippet and title
                articleBlurb = f"{title.get_text()} {snippet.get_text()}"
                articleBlurb_vector = model.encode(articleBlurb)

                #score blurb based on each domain in the references list
                relevancy = max(
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector1).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector2).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector3).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector4).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector5).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector6).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector7).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector8).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector9).item()),
                    scorer(util.cos_sim(articleBlurb_vector, reference_vector10).item()),
                )

                writer.writerow([link['href'], title.get_text(), snippet.get_text(), date.get_text(), source.get_text(), relevancy])

while True:
    print("Press ctrl + c to exit")
    word = input("Search for: ")
    print("working...")
    scrapeGoogle(word)
    print(f"Saved {word} scraping results as csv file!")