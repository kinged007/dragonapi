"""
Multiple functions to publish tips to various platforms

"""

# from rich import print
from loguru import logger as log
import asyncio
import requests
from dateutil.parser import parse
from pydantic import BaseModel

from models.html import markdown_to_html
from modules import telegram
from modules import translate

from ..schema import TipSchema, HunchClubPublishPlatform
from utils.datetime import utc_now, utc_datetime, datetime

class PublishTips(BaseModel):
    
    translator:translate.Module = None
    
    def __init__(self ): 
        super().__init__()
        self.translator = translate.Module()
        
    def ready(self, platform:HunchClubPublishPlatform, force=False):
        
        try:
            
            if not platform:
                raise Exception("No data or platform provided")
            
            credentials = platform.platform.credentials
            icons = platform.icons.model_dump()
            
            # Active check should be done by controller or ui
            # if not platform.active:
            #     return False
            if not platform.platform.target:
                raise Exception("No platform/target provided")
            
            # Check if we are on schedule
            if not force:
                if utc_datetime(platform.next_publish) > utc_now():
                    log.debug(f"PublishTips:{platform.name} Not Ready: Next Publish: {platform.next_publish}")
                    return False
            
            log.debug(f"PublishTips Ready: {platform.channel} {platform.platform.target}")
            
            return True
        
        except Exception as e:
            log.error(e)
            return False
        
    async def _post_message(self, platform:HunchClubPublishPlatform, message:str):
        
        # Check for malformations..
        if "{" in message and "}" in message:
            log.error("Malformed message: "+message)
            raise Exception(f"Malformed message on '{platform.name}'. There should not be any curly brackets in the final message: {message}")
        
        # Check for multiple targets, comma seperated and loop
        targets = platform.platform.target.split(",")
        _errors = []
        
        for target in targets:
            target = target.strip()
            try:
                # Filter target and call relative function
                if platform.channel == 'telegram':
                    await self.post_telegram(platform, message, target)
                if platform.channel == "smtp":
                    await self.post_smtp(platform, message, target)
                if platform.channel == 'brevo_api':
                    await self.post_brevo_api(platform, message, target)
                await asyncio.sleep(1)
            except Exception as e:
                log.error(e)
                _errors.append(e)
        
        if _errors:
            return False
        
        return True
        
    async def publish(self, data:list = [], platform:HunchClubPublishPlatform = None, force=False):
        
        log.debug(f"Publishing {platform.publish_type}...")
        
        if not platform:             
            raise Exception("No platform provided")
                
        if not self.ready( platform, force):
            return False
        
        _lang = platform.language.lower()
        _format = platform.tips_format
        _max = int(platform.max_tips) if platform.max_tips else 0
        _sort_by = platform.sort_by or 'datetime'
        _sort_order = platform.sort_order or 'asc'
        _tips_message = platform.tips_message
        _date_format = platform.date_format or "%Y-%m-%d %H:%M"
        _publish_type = platform.publish_type
        
        # Get all tips and sort it out.
        log.info(f"Got {len(data)} {_publish_type} to publish to {platform.name}")
        
        if not data and not platform.publish_if_no_tips:
            raise Exception("No tips data was found for the search criteria.")
            # await self.cron.log("No tips to publish")

        if not _tips_message or _tips_message.strip() == "":
            log.debug("No format provided for publish_tips. Skipping...")
            raise Exception("No format provided for publish_tips. Skipping...")
            # return
        
        if data and not isinstance(data[0], TipSchema):
            log.warning("Data is not in the correct format. It should be a list of TipSchema")
            new_data = []
            for x in data:
                new_data.append(TipSchema(**x))
            data = new_data
            
        # Sort tips 
        tips = sorted(data, key=lambda k: getattr(k, _sort_by), reverse=True if _sort_order == 'desc' else False)
        published_tips = []
        published_profits = []
        
        for tip in tips:
            if _max>0 and len(published_tips) >= _max:
                log.debug("Reached max tips")
                break
            
            # Apply tips format
            # Replace template variables from tips data
            # Available variables: event_type, event_name, datetime, participants, selection, odds, description, bet_result, event_result
            _results = _format
            _tip_profit = 0
            
            if _publish_type == 'results':
                if not tip.bet_result:
                    # log.warning(f"Skipping tip without bet_result: {tip}")
                    log.warning(f"Tip is without bet_result: {tip.event_name} {tip.participants} {tip.datetime}")
                    continue
            
            log.debug(tip)
            
            for k,v in tip.model_dump().items():
                try:
                    # print(k,v)
                    if k.startswith("_") or "{"+str(k)+"}" not in _format: continue
                    if isinstance(v, list):
                        v = " vs ".join(v) if len(v) <= 2 else ", ".join(v)
                        
                    if k == 'bet_result':
                        if _publish_type == 'results' and v.lower() in ['win','lose','void']:
                            _tip_profit = platform.stake_amount * float(tip.odds) if v.lower() == 'win' else 0 if v.lower() == 'void' else -platform.stake_amount
                            log.debug(_tip_profit)
                            published_profits.append(_tip_profit) 
                            if platform.use_icons:
                                v = platform.icons.bet_win if v.lower() == 'win' else platform.icons.bet_lose if v.lower() == 'lose' else platform.icons.bet_void
                            else:
                                v = v.capitalize()
                        else:
                            # Remove curly brackets from bet_result
                            v = ""
                            
                    if k == 'event_result':
                        # Remove curly brackets from bet_result
                        if _publish_type != 'results':
                            v = ""
                            
                    if k == 'datetime':
                        if isinstance(v, str):
                            try:
                                v = parse(v)
                            except ValueError:
                                print(f"Could not parse datetime: {v}")
                        if isinstance(v, datetime):
                            v = v.strftime(_date_format)
                    if k == 'event_type':
                        if platform.use_icons:
                            v = hasattr(platform.icons, v) and getattr(platform.icons, v) or v
                            # v = self.icons[v] if v in self.icons else v
                        else:
                            v = v.capitalize()
                    # Translate
                    if 'en' not in _lang and k in ['description','selection','participants', 'bet_result']: 
                        v = self.translator.translate(v, _lang, "en")
                    _results = _results.replace("{" + str(k) + "}", str(v))
                except Exception as e:
                    # await self.cron.log(e)
                    log.error(e)
                    break
            
            if any(f"{{{k}}}" in _results for k in ['stake','profit']):
                _results = _results.replace("{stake}", "{:.2f}".format(platform.stake_amount))
                if _publish_type == 'results':
                    # TODO Calculate profit correctly using the odds. Use published_profits to calculate the profit
                    # platform.stake_amount * float(tip.odds)
                    _results = _results.replace("{profit}", "{:.2f}".format(_tip_profit))
                else:
                    _results = _results.replace("{profit}", "")
            
            if _results:
                published_tips.append(_results)
                
        if not published_tips:
            # await self.cron.log("No tips to publish")
            if not platform.publish_if_no_tips:
                return published_tips
            else:
                log.debug("No tips to publish, sending 'no tips' message...")
                published_tips.append(platform.no_tips_message)
            
        
        log.debug(f"Total Profit: {published_profits}")
        
        # Get tips message
        # Translate it first
        ## UPDATE: Do not translate the message, as it is already expected to be translated in the UI. 
        ## UPDATE: Do not append results to the message, if it is skipped, thene maybe a different message should be published.
        # if 'en' not in _lang:
        #     # Translate
        #     _tips_message = self.translator.translate(_tips_message.replace("{tips}","###T###"), _lang, "en").replace("###T###", "{tips}")
        # # Verify {tips} is present
        # if "{tips}" not in _tips_message:
        #     _tips_message += "\n{tips}"
        
        # Replace {tips} with tips
        _tips_message = _tips_message.replace("{tips}", "\n".join(published_tips))
        # {total_tips} {total_profit}
        if _publish_type == 'results':
            _tips_message = _tips_message.replace("{total_profit}", "{:.2f}".format(sum(published_profits)))
        else:
            _tips_message = _tips_message.replace("{total_profit}", "")
            
        _tips_message = _tips_message.replace("{total_tips}", str(len(published_tips)))
        
        print(_tips_message) # DEBUG
        
        try:
            if await self._post_message(platform, _tips_message):
                
                log.info(f"{platform.name}: Published {len(published_tips)} {_publish_type.capitalize()} to {platform.channel}")
                
            return published_tips
        except Exception as e:
            raise Exception(str(e))
    
    # TODO Deprecate this function in favour of a single publish function, using platform attribute publish_type to determine the type of publish
    async def publish_results(self, data:dict = None, platform:HunchClubPublishPlatform = None, force=False):
        log.warning("DEPRECATED: publish_results")
        if not data or not platform: 
            raise Exception("No data or platform provided")
        
        if not self.ready(platform, force):
            return False
        

        _lang = platform.language.lower()
        _format = platform.results_format
        _max = int(platform.max_tips) if platform.max_tips else 0
        _sort_by = platform.sort_by or 'datetime'
        _sort_order = platform.sort_order or 'asc'
        _tips_message = platform.results_message
        _date_format = platform.date_format or "%Y-%m-%d %H:%M"
        
        log.debug(f"Publishing {len(data) if _max == 0 else _max} results to platform")

        if not data:
            raise Exception("No tips data was found for the search criteria.")
            # await self.cron.log("No tips to publish")
            return
        if not _tips_message or _tips_message.strip() == "":
            log.debug("No format provided for publish_results. Skipping...")
            raise Exception("No format provided for publish_results. Skipping...")
            # return

        # Sort tips 
        tips = sorted(data, key=lambda k: k[_sort_by], reverse=True if _sort_order == 'desc' else False)
        published_tips = []
        _included_tips = 0
        published_profits = []
        
        # TODO implement group by options
        # # Group by datetime, event_type, event_name, selection, odds, event_result, bet_result
        # group_by: str = "event_name"
        # group_by_help: str = "Group the tips by the selected field. This is used to group the tips together and publish them as a single message."
        # group_by_options: list = ["datetime", "event_type", "event_name", "selection", "odds", "event_result", "bet_result"]

        for tip in tips:
            if _max>0 and _included_tips >= _max:
                print("Reached max tips")
                break
            
            # Apply tips format
            # Replace template variables from tips data
            # Available variables: event_type, event_name, datetime, participants, selection, odds, description, bet_result, event_result
            _results = _format
            
            for k,v in tip.items():
                try:
                    if k.startswith("_") or "{"+str(k)+"}" not in _format: continue
                    if isinstance(v, list):
                        v = " vs ".join(v) if len(v) <= 2 else ", ".join(v)
                    if k == 'bet_result':
                        published_profits.append(v)
                        # print(platform.icons)
                        if platform.use_icons:
                            v = platform.icons.bet_win if v.lower() == 'win' else platform.icons.bet_lose if v.lower() == 'lose' else platform.icons.bet_void
                        else:
                            v = v.capitalize()
                    if k == 'datetime':
                        if isinstance(v, str):
                            try:
                                v = parse(v)
                            except ValueError:
                                print(f"Could not parse datetime: {v}")
                        if isinstance(v, datetime):
                            v = v.strftime(_date_format)
                    if k == 'event_type':
                        if platform.use_icons:
                            v = hasattr(platform.icons, v) and getattr(platform.icons, v) or v
                            # v = self.icons[v] if v in self.icons else v
                        else:
                            v = v.capitalize()
                    # Translate
                    if 'en' not in _lang and k in ['description','selection','participants', 'bet_result']: 
                        v = self.translator.translate(v, _lang, "en")
                    _results = _results.replace("{" + str(k) + "}", str(v))
                    # print(_results)
                except Exception as e:
                    # await self.cron.log(e)
                    log.error(e)
                    break
                
            if _results:
                published_tips.append(_results)
                _included_tips += 1
                
        if not published_tips:
            # await self.cron.log("No tips to publish")
            return published_tips
            
        # Get tips message
        # Translate it first
        ## UPDATE: Do not translate the message, as it is already expected to be translated in the UI. 
        ## UPDATE: Do not append results to the message, if it is skipped, thene maybe a different message should be published.
        # if 'en' not in _lang:
        #     # Translate
        #     _tips_message = self.translator.translate(_tips_message.replace("{results}","###T###"), _lang, "en").replace("###T###", "{results}")
        # # Verify {tips} is present
        # if "{results}" not in _tips_message:
        #     _tips_message += "\n{results}"
        # Replace {tips} with tips
        _tips_message = _tips_message.replace("{results}", "\n".join(published_tips))
        
        print(_tips_message, published_profits)
        
        try:
            if await self._post_message(platform, _tips_message):
            
                log.info(f"Published {len(published_tips)} results to {platform.channel}")

            return published_tips
        
        except Exception as e:
            raise Exception(str(e))

    async def post_telegram(self, platform:HunchClubPublishPlatform, message:str, specific_target:str = None):
        
        token = platform.platform.credentials.api_key
        telegram_client = telegram.Module()
        telegram_client.connect(token)
        
        target = specific_target if specific_target else platform.platform.target
        
        # Publish to channel with image
        if platform.tips_photo:
            telegram_client.send_image(target, platform.tips_photo )
            
        # Send message
        telegram_client.send_message(target, message, parse_mode="Markdown")
        
        # await self.cron.log(f"Published {len(published_tips)} tips/results to Telegram")
        

    async def post_brevo_api(self, platform:HunchClubPublishPlatform, message:str, specific_target:str = None):
        
        log.info("Sending email via Brevo API...")
        
        target = specific_target if specific_target else platform.platform.target
        
        token = platform.platform.credentials.api_key
        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": platform.platform.name,
                "email": platform.platform.credentials.email
            },
            "to": [
                {
                    "email": target,
                }
            ],
            "subject": platform.platform.credentials.subject,
            "textContent": markdown_to_html(message),
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": token
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            # print(response.text)
            response = response.json()
            # eg. response = {"messageId":"<202402082129.60963195813@smtp-relay.mailin.fr>"}
            if 'messageId' in response:
                log.info("Email sent successfully")
            else:
                raise Exception(str(response))
            
        except Exception as e:
            log.error(e)
            raise Exception("Error sending email: "+str(e))
        
        # await self.cron.log(f"Published {len(published_tips)} tips/results to Brevo API (email)")
        

    async def post_smtp(self, platform:HunchClubPublishPlatform, message:str, specific_target:str = None):
        # Send email
        import smtplib
        from email.mime.text import MIMEText
        
        target = specific_target if specific_target else platform.platform.target
        
        # Define the SMTP server credentials
        smtp_server = platform.platform.credentials.smtp_server
        smtp_port = platform.platform.credentials.smtp_port
        smtp_username = platform.platform.credentials.username
        smtp_password = platform.platform.credentials.password
        from_email = platform.platform.credentials.email
        to_email = target
        
        if not any([smtp_server, smtp_port, smtp_username, smtp_password, from_email, to_email]):
            raise Exception("SMTP credentials not completely configured")
        
        # Create the email
        msg = MIMEText(message)
        msg['Subject'] = platform.platform.credentials.subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        log.info("Sending email using SMTP...")
        
        try:
            # Send the email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.connect()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            log.error(e)
            raise Exception("Error sending email: "+str(e))
        
        # await self.cron.log(f"Published {len(published_tips)} tips/results to SMTP (email)")