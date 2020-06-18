# Twitter usage analysis during COVID-19 lockdown imposition
 
With the novel corona virus pandemic outbreak the Government of India imposed various stages of lockdown to curb the transmission. This meant that social media became the outlet for many people and we aim to evaluate the changes in behavior and usage for the twitter platform.

src: https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdown_in_India

### Data collection
---
A BFS was perfomed starting with a few micro-celerbrities as seed users to extract users in the Indian region. Outliers such as inactive users, protected accounts and verified accounts were ignored to avoid samples which have no significant changes in behavior. Morever to make the traversal sufficiently deep and extensive these users were avoided. 

From the users gathered, the timeline of statuses were extracted until the beginning of the year 2020 for analysis purposes. 

Statuses were grouped into tweets, retweets and replies for a more nuanced analysis

Further top hastags were gathered and then the relevant tweets were extracted to perform a sentiment analysis.

