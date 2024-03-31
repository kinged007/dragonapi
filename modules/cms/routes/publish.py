from fastapi import APIRouter, Query, Request, Depends, BackgroundTasks
# from fastapi.responses import JSONResponse
# from loguru import logger as log
from os import path
from enum import Enum
from loguru import logger as log
# from rich import print

# Import app models
from models.utils import html_to_markdown, markdown_to_html
from modules.directus import Directus

# Import self module config
from modules.cms.config import Config
from modules.cms.src import directus as directus_helper, wordpress


router = APIRouter()

@router.get('/post/{post_id}')
async def publish_post(background_task: BackgroundTasks, request: Request, post_id: str = None):
    """
    Publish a post
    """
    
    directus = directus_helper.Directus()
    
    # Step 1: Get post object from database where destination.status == 'active'
    posts = directus.filter_publishable_posts(post_id)
    
  
    if posts:
        
        if isinstance(posts, dict): posts = [posts]
        for post in posts:
            print(post)
            background_task.add_task(publish_posts_in_background, post)
            
    else:
        return {"error":"No post found"}
        
    return {
        "message": f"Processing {len(posts)} posts in the background.",
    }

async def publish_posts_in_background(post):
    
        
    directus = directus_helper.Directus()
    config = Config()
    
    publish_count = 0 # Total number published
    publish_total = 0 # Total number to be published

    for translation in post.get('translations', []):
        published_post = None
        publish_total += 1
        try:
            # print(translation)
            platform = translation.get('destination', {}).get('destination_type', '')
            if platform == 'wordpress':
                published_post = await wordpress.publish_post_from_directus(post.get('id'), translation.get('id'))
            
            
            # Finally
            if published_post and published_post.get('id', None):
                # log.info(f"Published post #{post.get('id')}, translation #{translation.get('id')}")
                publish_count += 1
                # Update the translation object is made by the publish_post_from_directus function... 
            else:
                if published_post.get('error', None):
                    raise Exception(published_post.get('error'))
                raise Exception("Unknown error: published_post:" + str(published_post))
                
        except Exception as e:
            log.error(e)
            directus.comment(
                f"Error: Translation #{translation.get('id')}': " + str(e), 
                config.get("PostCollection"),
                post.get('id'), 
            )
            
    # Comment on publish results
    if publish_count>0:
        directus.comment(
            f"{publish_count} Post/s Published or Updated out of {publish_total}.", 
            config.get("PostCollection"),
            post.get('id'), 
        )
        update = directus.patch(
            f"items/{config.get('PostCollection')}/{post.get('id')}", 
            {
                "status": "published",
                
            }).json()
        if update.get("data", None):
            log.info(f"Updated post #{post.get('id')}")
        else:
            log.error(f"Failed to update post #{post.get('id')}")
