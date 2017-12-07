# NewsDiscovery
A auto news discovery system built by myself.  
## Author
_Patrick WANG_, currently an undergraduate in City University of Hong Kong.  

## News Source
In the prototype stage, I only used Facebook's graph api to scrape Facebook posts' content. Most of the source are short. I'm thinking expanding the Web Spider Module into a large scale web scraping system to crawl web contents from various websites.

Sources:

* [x] Facebook pages' content
* [ ] HK local news press' website.
* [ ] Mainlands Weibo's data
* [ ] Twitter's data (They seems to have an API) 

## News Discover Algorithm

Current algorithm is pretty dumm. As most of the Facebook's contents are short, it normal NLP model's performance is not very well.   

Thinking about improving algorithms now. All ideas are extremely welcome!   

## Contribute to this project

All PRs that can benefit this project are welcome!  
Currently all source codes are formatted following PEP 8, which I think is a very practical and useful coding style.   
Please make sure you have format your code into PEP 8 style before pull request. Thanks.

## TODOs

* [ ] A Custom Recommender system (if we got enough visitors...). 
* [ ] A fully functional website (backend can be integrated into current src? not sure, thinking about Flask right now). 
* [ ] Refactor the whole system into a expandable news discover engine. (Improvement @@) 



