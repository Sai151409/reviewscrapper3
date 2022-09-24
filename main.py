from flask import Flask, request, render_template
from flask_cors import cross_origin
from bs4 import BeautifulSoup as bs
import requests
from urllib.request import urlopen as uReq


app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def home_page():
    return render_template('index.html')


@app.route('/review', methods=['GET', 'POST'])
@cross_origin()
def review():
    if request.method == 'POST':
        try:
            search_string = request.form['content'].replace(" ", "")
            flipkart_url = 'https://www.flipkart.com/search?q=' + search_string
            uClient = uReq(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_page, 'html.parser')
            bigbox = flipkart_html.find_all("div", {'class': "_1AtVbE col-12-12"})
            del bigbox[0:3]
            productLink = 'https://www.flipkart.com' + bigbox[0].div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, 'html.parser')
            comments = prod_html.find_all('div', {'class': "_16PBlm"})
            filename = search_string + '.csv'
            fw = open(filename, 'w')
            headers = 'Product, Name, Rating, Comment Heading, Comments'
            fw.write(headers)
            reviews = []
            for i in range(len(comments)-1):
                try:
                    Name = comments[i].div.div.find_all('p', {'class': "_2sc7ZR _2V5EHH"})[0].text
                except:
                    Name = 'No Name'
                try:
                    Rating = comments[0].div.div.div.div.text
                except:
                    Rating = 'No Rating'
                try:
                    comment_heading = comments[i].div.div.div.p.text
                except:
                    comment_heading = 'No Comment Heading'
                try:
                    Comments = comments[i].div.div.find_all('div', {'class' : ''})[0].text
                except:
                    Comments = 'No Multiple Comments'
                mydict = {'Product' : search_string,
                          'Name' : Name,
                          'Rating' : Rating,
                          'Comment Heading' : comment_heading,
                          'Comments' : Comments}
                reviews.append(mydict)
            return render_template('result.html', review=reviews[0:len(reviews)-1])
        except Exception as e:
            print(f'The error is : {e}')
            return 'Something Went Wrong'
    else:
        return render_template('index.html')



if __name__ == '__main__':
    app.run(port=2705)
