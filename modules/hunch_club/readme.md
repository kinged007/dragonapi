
## Structure

Module is managed / automated by APP. 
Module config is basic and is related to executing and running the module.
This module uses an external MongoDB database, which contains the data to publish, and configuration for specific platforms to publish to.

## Router

Endpoint: Get tips for today
    Retrieves the tips for the day.
    
Endpoint: Get tips results for yesterday
    Retrieves the results for the previous day.
    
Endpoint: Get publishing platform schema
    Retrieves the base model schema for the publishing platforms.
    
## Database structure

### Tips

All tips (raw tips) will be saved in the same database collection: 'daily_tips', 2 days in advance (T+2). New tips may be added T+1 or the same day. 
Tips must manually be selected where to publish (Free/VIP). If no tips are selected, an error will occur and Admins will be notified.

{
  "_id": ObjectId()
  "datetime": datetime      # date of match being played in ISO format
  "participants": [         # List of participants in match. Use full english name.
    "West Ham (Home)",
    "Manchester United (Away)"
  ],
  "event_name": "English Premier League",       # League name, championship, content. Use full english name
  "event_type": "football",                     # name of sport. eg. basketball, baseball, etc
  "selection": "West Ham win",                  # prediction.
  "odds": 2.55,                         
  "description": "In their last 6 consecutive home matches of all competitions, there have been no losses for West Ham",            # Prediction reasoning
  "language": "en-US",                          # DEPRECATE - All tips should be written in ENGLISH as the primary language. Translations will be made from EN to other languages.
  "event_result": "",                           # The results of the game. eg. Score, Win/Lose/Postponed/Cancelled, etc.
  "bet_result": "",                             # The result of the prediction. eg. Win/Lose/Void
  "odds_url": "https://trustdice.win/sports/soccer/england/premier-league/1565773"          # The url the odds were collected from.
  "publish_free": bool = False                  # Publish as a Free Tip, defaults to False
  "publish_vip": bool = False                   # Publish as a Premium tip, defaults to False
}
