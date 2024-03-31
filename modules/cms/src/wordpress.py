from typing import Union, List

from loguru import logger as log
# from rich import print

# Directus
from models.wordpress import Wordpress
from modules.cms.src import directus as directus_helper
from modules.cms.config import Config
    
async def publish_post_from_directus(post_id, translation_id=None):

    print(">>>>>>>>>>>>>>>>>>> Publishing....", post_id, translation_id)
    
    published_posts = []
    publish_count = 0 # Total number published
    publish_total = 0 # Total number to be published
    
    directus = directus_helper.Directus()
    config = Config()
    
    post_obj = directus.fetch_post(post_id)
    
    if not post_obj.get('data', None):
        return {"error": "Post not found"}
    
    post_obj = post_obj.get('data')
    
    for post_translation in post_obj.get('translations', []):

        published_post = None

        if translation_id and post_translation.get('id') != translation_id: continue
        
        destination = post_translation.get('destination')
        
        # double check its a wordpress destination
        if destination.get('destination_type') != 'wordpress': continue
        
        # Set basic variables
        language = post_translation.get('languages_code', 'en-US')
        publish_total += 1
        
        # Get destination connection variables and connect to destination platform
        destination = directus.fetch_content_destination(destination.get('id'))
        
        if not destination.get('data', {}): 
            # await directus_helper.comment(post_obj.get('id'), f"Destination object not found for translation {language}")
            raise Exception(f"Destination object not found for translation {language}")
        
        destination = destination.get('data')
        
        if not destination.get('api_endpoint', None) or not destination.get('api_key', None) or not destination.get('api_secret', None):
            # await directus_helper.comment(post_obj.get('id'), f"Destination object missing credentials for translation {language}")
            raise Exception(f"Destination object missing credentials for translation {language}")
        
        # Connect to Wordpress
        wordpress = Wordpress(destination.get('url'), destination.get('api_key'), destination.get('api_secret'))
        
        # Get existing post ID
        published_post_id = post_translation.get('published_id', None)
        
        # Get author ID (needs to be in post_obj - Wordpress credentials are not high enough to view/create users), otherwise will use default author (apiUser)
        publish_author_id = post_obj.get('author', {}).get('wordpress_author_id', None) # TODO create new field to allow for defining the author ID for the different platforms

        # Get category ID's / create if dont exist
        # Create a list of dicts with keys slug,name,description,
        publish_categories = []
        for _pg in post_obj.get('post_category', []):
            # fix table inconsistency
            _pg = _pg.get('categories_id', {})
            _pg['category_name'] = _pg.get('name', '')
            # if empty translations, set defaults
            if not _pg.get('translations',[]): _pg['translations'] = [_pg]
            # get translation item
            for _pg2 in _pg.get('translations', []):
                if _pg2.get('languages_code', language) != language: continue
                # Sets the slug incase its missing
                _pg2['slug'] = _pg2.get('slug', _pg2.get('category_name', '').lower().replace(" ","-"))
                # Update our post_categories
                publish_categories.append({
                    "slug": _pg2['slug'],
                    "name": _pg2['category_name'],
                    "description": _pg2.get('description', None),
                })

        # TODO Get tag ID's / create if dont exist
        publish_tags = []
        
        # If featured image, upload to destination platform (use fallback_featured_image if no featured_image)
        featured_image = post_translation.get('featured_image', None)
        if not featured_image and post_obj.get('fallback_featured_image'):
            featured_image = post_obj.get('fallback_featured_image')
        
        # Get Featured Image ID
        publish_image_id = post_translation.get('published_media_id', None)
        if not publish_image_id and featured_image: 
            # Upload image to wordpress
            # TODO download image from directus using directus_model.asset_url(asset_id, include_filename)
            # _image = wordpress.upload_media(featured_image, {
            #     "title": featured_image.get('title', None),
            #     "description": featured_image.get('description', None),
            # })
            # log.debug(_image)
            # if _image:
            #     publish_image_id = _image.get('id', None)
            pass
        
        # Get post content - TODO convert to wordpress blocks
        publish_content = post_translation.get('content', None)
        
        # Get post title, description
        publish_title = post_translation.get('title', None)
        publish_description = post_translation.get('description', None)

        try:
            # Publish or Update post
            if published_post_id:
                # Updating
                log.debug(f"Updating post {published_post_id}")
                publish_post = wordpress.update_post(
                    post_id=published_post_id,
                    title=publish_title,
                    content=publish_content,
                    author=publish_author_id,
                    # status="draft",
                    categories=publish_categories,
                    tags=publish_tags,
                    featured_media=publish_image_id,
                    excerpt=publish_description,
                    slug=post_translation.get('slug', None),
                    format="standard",
                )
            else:
                # Publishing new post
                log.debug("Publishing new post")
                publish_post = wordpress.publish_post(
                    title=publish_title,
                    content=publish_content,
                    author=publish_author_id,
                    status=config.get('PostStatus','draft'),
                    categories=publish_categories,
                    tags=publish_tags,
                    featured_media=publish_image_id,
                    excerpt=publish_description,
                    slug=post_translation.get('slug', None),
                    format="standard",
                )
            
            if publish_post and publish_post.get('id', None):
                # Success
                publish_count += 1
                # Standardise the post response
                published_post = {
                    "id": publish_post.get('id'),
                    "url": publish_post.get('link'),
                    "slug": publish_post.get('slug','') if publish_post.get('slug','') else publish_post.get('generated_slug', ''),
                    "platform": "wordpress",
                    "post_object": publish_post,
                }
                # print(published_post)
                published_posts.append(published_post)
                
                # Update post_translation with published_post_id and published_post_url
                update_data = {
                    "published_id": published_post.get('id'),
                    "published_url": published_post.get('url'),
                    "slug": published_post.get('slug'),
                }
                
                log.debug(update_data)
                
                update = directus.patch(
                    f"items/{config.get('PostTranslationsCollection','post_translations')}/{translation_id}", 
                    update_data).json()
                # print(update)
                if update and update.get('data', None):
                    log.info(f"Published translation #{translation_id}:'{language}'")

                
                if translation_id:
                    # Only publishing one translation, moving on to next post
                    return published_post
                
                # More posts to publish, moving on to next translation
                continue
            
        except Exception as e:
            # await directus_helper.comment(post_obj.get('id'), f"Error publishing translation #{translation_id}:'{language}': " + str(e))
            raise Exception(f"Translation '{language}': " + str(e))
        
        # else: 
        #     # Failed to Update/Publish post
        #     log.error(f"Failed to publish post {post_id} translation {language}")
        #     return {"error": f"Failed to publish post {post_id} translation {language}"}
            
        # Publish post
        
        
    return {
        "total_to_publish": publish_total,
        "total_published": publish_count,
        "published_posts": published_posts,
    }