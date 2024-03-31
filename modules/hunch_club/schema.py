# from beanie import Document
from mongoengine import connect, Document
from fastapi.security import HTTPBasicCredentials
from pydantic import ConfigDict, BaseModel, EmailStr
from enum import Enum
import datetime as dt
from typing import Optional

class PermissionsOptions(Enum):
    read = "read"
    tips_read = "tips_read"
    write = "write"


class SportsIcons(BaseModel):
    bet_win: str = "✅"
    bet_lose: str = "❌"
    bet_void: str = "♻️"
    football: str = "⚽️"
    basketball: str = "🏀"
    tennis: str = "🎾"
    baseball: str = "⚾️"
    ice_hockey: str = "🏒"
    american_football: str = "🏈"
    rugby: str = "🏉"
    handball: str = "🤾"
    volleyball: str = "🏐"
    cricket: str = "🏏"
    boxing: str = "🥊"
    mma: str = "🥋"
    esports: str = "🎮"
    table_tennis: str = "🏓"
    snooker: str = "🎱"
    darts: str = "🎯"
    cycling: str = "🚴"
    golf: str = "⛳️"
    motorsport: str = "🏎"
    specials: str = "🎲"
    politics: str = "🗳"
    entertainment: str = "🎭"
    other: str = "🎲"
    
class PublishPlatformCredentials(BaseModel): # suitable for twitter, email (smtp), email (API), telegram
    
    username: str = ""
    username_help: str = "Username required for logging into the platform, or From Name for email services."
    email: str = ""
    email_help: str = "Email required for logging into the platform, or From Email for email services."
    password: str = ""
    api_key: str = "" # for telegram, twitter, email (API)
    api_key_help: str = "Use this for the BotToken for Telegram, or the API Key for the email service provider or Twitter." 
    smtp_server: str = ""
    smtp_port: int = 587
    subject: str = ""
    subject_help: str = "Subject line for emails, ..."
    

class PublishTipsPlatform(BaseModel):
    name: str = "" # Deprecate ?
    website: str = ""
    website_help: str = "Website address for reference, or API Endpoint for ...."
    target: str = "" # chat id for telegram, username for twitter, email for email 
    # TODO change 'target' to a list of targets, each with their own template and language specification.... to reduce having 5 different platforms for 5 different languages, into 1 platform with 5 different targets.
    target_help: str = "Enter the chat id/username for telegram, or email address, or channel you want to publish to." 
    credentials: PublishPlatformCredentials = PublishPlatformCredentials()

# Not using this because it has no benefit outside of this app, as JSON objects do not carry forward the Enum type objects or type hints.
# class ChannelOptions(str, Enum):
#     telegram = "telegram"
#     twitter = "twitter"
#     email = "email"
#     brevo_api = "brevo_api"
    
# NOTE: For keys that contain _help or _options, they should NOT be stored in the database. Make sure the UI filters them out before saving it.
class HunchClubPublishPlatformSchema(BaseModel):
    id: str = "" # Id of MongoDB document. Should Not required in this class...
    name: str = ""
    active: bool = False
    # channel: ChannelOptions = ChannelOptions.telegram # telegram, twitter, email
    # daily_schedule: datetime.time = datetime.time(8, 15)
    # daily_schedule_field: str = "time"
    # daily_schedule_help: str = "The time of day to publish the tips. This is in UTC time."
    publish_schedule:str = "30 8 * * *" # 8:30 UTC
    publish_schedule_help: str = "The time of day to publish the tips. This is in UTC time."
    next_publish: dt.datetime = dt.datetime.now(dt.timezone.utc)
    channel: str = "telegram" # telegram, twitter, email
    channel_options: list = ["telegram","twitter","smtp","brevo_api"] # telegram, twitter, email
    language: str = "EN"
    language_options: list = ["EN","ES","FR","DE","IT","PT","RU","AR","ZH","JA","KO","TR","VI","TH","ID","PL","NL","EL","HU","CS","SK","BG","RO","DA","SV","FI","NO","UK","HR","SR","SL","ET","LV","LT","MS","FA","HE","HI","BN","GU","KN","ML","MR","PA","TA","TE","UR"]
    language_help: str = "Language to use for the tips/results messages. Uses ISO 639 language codes, 2-letter format. https://cloud.google.com/translate/docs/languages"
    use_icons: bool = True
    max_tips: int = 0
    sort_by: str = "datetime"
    sort_by_options: list = ["datetime", "event_type", "event_name", "participants", "selection", "odds", "event_result", "bet_result","description"]
    sort_order: str = "asc"
    sort_order_options: list = ["asc", "desc"]
    # Group by datetime, event_type, event_name, selection, odds, event_result, bet_result
    group_by: str = "event_name"
    group_by_help: str = "Group the tips by the selected field. This is used to group the tips together and publish them as a single message."
    group_by_options: list = ["datetime", "event_type", "event_name", "selection", "odds", "event_result", "bet_result"]
    
    date_format: str = "%Y-%m-%d %H:%M"
    date_format_help: str = "Output format of match date and time. Default is '%Y-%m-%d %H:%M'. See formatting codes here: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes"
    # DONE Add filter criteria here for free/premium groups. 
    tips_filter: list = []
    tips_filter_options: list = ["unspecified","free","premium"]
    tips_filter_field: str = "multiselect"
    
    
    
    # Replace Tips and Results with ONE single schema. A new platform should be created for each tips and results.
    publish_type: str = "tips"
    publish_type_options: list = ["tips","results"] # TODO add report type with weekly/monthly stats
    tips_days_delta: int = 0 
    tips_days_delta_help: str = "Days from today into the future, for tips, (or past for results) to fetch tips. Use 0 for today only (or yesterday), 1 for today and tomorrow (or yesterday and day before), 2 for today, tomorrow and the next day, etc." 
    stake_amount: float = 1.0
    stake_amount_help: str = "The amount of money to use for the stake. This is used to calculate the potential profit/loss."
    
    publish_if_no_tips: bool = False
    publish_if_no_tips_help: str = "Send a message if no tips are available. If this is set to False, then the message will not be sent if there are no tips available."
    no_tips_message: str = "No tips available today."
    no_tips_message_help: str = "The message to send if no tips are available and 'publish_if_no_tips' is set to True. This text is NOT automatically translated."
    
    
    # Updated Tips and Results with ONE single schema. A new platform should be created for each tips and results.
    tips_format: str = "{event_type} {event_name} {datetime} {participants} {market_type} {selection} {odds}"
    tips_format_help: str = "Use {variable} in your template. Available options include: {event_type} {event_name} {datetime} {participants} {description} {market_type} {selection} {odds} {stake}. You can use {event_result} {bet_result} {profit} in 'results' publish type only or else it will be removed. The 'description', 'selection' and 'participants' are translated to selected language."
    tips_format_field: str = "textarea"
    tips_photo: str = ""
    tips_photo_help: str = "You may use a URL of an image to upload BEFORE the tips/results message. Leave blank to not use an image."
    tips_message: str = "*New Tips*\n{tips}"
    tips_message_field: str = "textarea"
    tips_message_help:str = "Your message to be published. Include '{tips}' to insert the tips/results using the defined format. You can include {total_tips} {total_profit}. Use Markdown. If this message is left empty, then the tips will not be published to this platform. This text is NOT automatically translated."
    # TODO add and implement show link previews for telegram, and show images for twitter (?).
    # show_link_preview: bool = False
    
    # results_format: str = "{event_type} {event_name} {participants} {selection} {odds} {event_result} : {bet_result}"
    # results_format_field: str = "textarea"
    # results_format_help: str = "Use {variable} in your template. Available options include: {event_type} {event_name} {datetime} {participants} {description} {selection} {odds} {event_result} {bet_result}. The 'description', 'selection', 'bet_result' and 'participants' are translated to selected language."
    # results_photo: str = ""
    # results_photo_help: str = "You may use a URL of an image to upload BEFORE the tips/results message. Leave blank to not use an image."
    # results_message: str = "*Yesterday's Results*\n{results}"
    # results_message_field: str = "textarea"
    # results_message_help:str = "Your message to be published.Include '{results}' to insert the results using the defined format. Use Markdown. If this message is left empty, then the results will not be published to this platform. This text is NOT automatically translated."
    
    platform: PublishTipsPlatform = PublishTipsPlatform() # PublishTipsPlatform
    platform_help: str = "The platform to publish the tips to. This includes the website, target and credentials. This is used to authenticate and send the tips to the correct location."
    
    icons: SportsIcons = SportsIcons()

    # class Settings:
        # name = "hunch_club_publish_platforms"


class HunchClubPublishPlatform(BaseModel):
    
    id: str = "" # Id of MongoDB document. Should Not required in this class...
    name: str = ""
    active: bool = False
    publish_schedule:str = "30 8 * * *" # 8:30 UTC
    next_publish: dt.datetime = dt.datetime.now(dt.timezone.utc)
    channel: str = "telegram" # telegram, twitter, email
    language: str = "EN"
    use_icons: bool = True
    max_tips: int = 0
    sort_by: str = "datetime"
    sort_order: str = "asc"
    group_by: str = "event_name"
    date_format: str = "%Y-%m-%d %H:%M"
    tips_filter: list = []
    publish_type: str = "tips"
    tips_days_delta: int = 0 
    stake_amount: float = 1.0
    publish_if_no_tips: bool = False
    no_tips_message: str = "No tips available today."
    platform: PublishTipsPlatform = PublishTipsPlatform() # PublishTipsPlatform
    tips_format: str = "{event_type} {event_name} {datetime} {participants} {selection} {odds}"
    tips_photo: str = ""
    tips_message: str = "*New Tips*\n{tips}"
    # results_format: str = "{event_type} {event_name} {participants} {selection} {odds} {event_result} : {bet_result}"
    # results_photo: str = ""
    # results_message: str = "*Yesterday's Results*\n{results}"

    icons: SportsIcons = SportsIcons()
    
    class Settings:
        name = "hunch_club_publish_platforms"

    def model_dump(self):
        """
        Overrides the default model_dump() and Returns a dictionary skipping all the help and field attributes.
        """
        def recursive_walk(data):
            new_data = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    new_data[key] = recursive_walk(value)
                else:
                    if not any(x in key for x in ['_help', '_field', '_options', '_disabled']):
                        new_data[key] = value
            return new_data
        return recursive_walk(super().model_dump())
        
        
class TipSchema(BaseModel):
    _id: str = ""
    datetime: dt.datetime = dt.datetime.now(dt.timezone.utc)
    participants: list = []
    event_name: str = ""
    event_type: str = ""
    market_type: Optional[str] = None
    selection: str = ""
    odds: Optional[float] = None
    description: str = ""
    language: Optional[str] = "en-US"
    event_result: Optional[str] = None
    bet_result: Optional[str] = None
    odds_url: Optional[str] = None
    publish_free: bool = False
    publish_vip: bool = False