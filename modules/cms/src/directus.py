
from modules.directus import Directus
from modules.cms.config import Config

class Directus(Directus):
    
    config = None
    
    def __init__(self):
        self.config = Config()
        super().__init__()
        
    def fetch_content_destination(self, id: str):
        
        if id:
            try:
                if "content_destination":
                    project = self.get(f"items/content_destination/{id}", params={
                        "fields": [
                            "*"
                        ]
                    }).json()
                    if project.get("data", None):
                        project = project.get("data")
                        return {"data" : project}
                    if project.get("error", None):
                        raise Exception(project.get("errors"))

            except Exception as e:
                return {"error":str(e)}
            
        return {}
    
    def filter_publishable_posts(self, post_id: str = None):
        """
        Fetches all the suitable post/s  from Directus
        """
        if not self.config.get('PostCollection'): raise Exception("Post Collection not set")
        
        endpoint = f"items/{self.config.get('PostCollection')}/{post_id}" if post_id else f"items/{self.config.get('PostCollection')}"
        try:
            posts = self.get(endpoint, params={
                "filter[translations][destination][status][_eq]":  "active",
                "filter[status][_eq]":  "scheduled",
                "fields": [
                    "id",
                    "translations.id",
                    "translations.destination.destination_type",
                ]
            }).json()
            if posts.get("data", None):
                return posts.get("data", None)
            if posts.get("error", None):
                raise Exception(posts.get("errors"))

        except Exception as e:
            return {"error":str(e)}
            
        return {}
                    
    
    def fetch_post(self, post_id: str):
        """
        Fetches all the post data from Directus
        """
        if post_id:
            try:
                if self.config.get("PostCollection"):
                    project = self.get(f"items/{self.config.get('PostCollection')}/{post_id}", params={
                        "fields": [
                            # "*",
                            "id",
                            "author.first_name,author.last_name,author.description,author.email", 
                            "fallback_featured_image", 
                            "fallback_featured_image.id",
                            "fallback_featured_image.filename_download",
                            "fallback_featured_image.width",
                            "fallback_featured_image.height",
                            "fallback_featured_image.description",
                            "fallback_featured_image.type",
                            "fallback_featured_image.title",
                            "publish_date",
                            "status",
                            "translations.id",
                            # "translations.published_post_id", # TODO: This is the ID of the post in the destination CMS
                            # "translations.published_post_url", # TODO: This is the URL of the post in the destination CMS
                            "translations.languages_code",
                            "translations.content",
                            "translations.description",
                            "translations.featured_image", 
                            "translations.featured_image.id",
                            "translations.featured_image.filename_download",
                            "translations.featured_image.width",
                            "translations.featured_image.height",
                            "translations.featured_image.description",
                            "translations.featured_image.type",
                            "translations.featured_image.title",
                            "translations.languages_code",
                            "translations.title",
                            "translations.slug",
                            "translations.published_id",
                            "translations.published_media_id",
                            "translations.destination.id", 
                            "translations.destination.destination_type", 
                            "translations.destination.language", 
                            "translations.destination.status", 
                            
                            # "translations.*.*",
                            "post_category.categories_id.name",
                            "post_category.categories_id.translations.category_name",
                            "post_category.categories_id.translations.languages_code",
                            "post_category.categories_id.translations.slug",
                        ],
                        "filter[translations][destination][status][_eq]":  "active",
                        "filter[status][_eq]":  "scheduled",
                        
                    }).json()
                    if project.get("data", None):
                        project = project.get("data")
                        return {"data" : project}
                    if project.get("error", None):
                        raise Exception(project.get("errors"))

            except Exception as e:
                return {"error":str(e)}
            
        return {}

    # TODO: Move these functions into the class model
    def fetch_project(self, project_id: str):
        
        if project_id:
            try:
                
                if self.config.get("ProjectsCollection"):
                    project = self.get(f"items/{self.config.get('ProjectsCollection')}/{project_id}", params={
                        "fields": [
                            "name",
                            "start_date",
                            "end_date",
                            "description",
                            "resources",
                            "objectives",
                            "execution_strategy",
                            "milestones",
                            "tasks",
                            "risk_management_plan",
                            "performance_metrics",
                            "quality_assurance",
                            "budget",
                            "communication_plan",
                            "key_stakeholders",
                            "department.department_id.name",
                            "project_lead.directus_users_id.first_name",
                            "project_lead.directus_users_id.last_name",
                            "users_involved.directus_users_id.first_name",
                            "users_involved.directus_users_id.last_name",
                        ]
                    }).json()
                    if project.get("data", None):
                        project = project.get("data")
                        return {"data" : project}
                    if project.get("error", None):
                        raise Exception(project.get("errors"))

            except Exception as e:
                return {"error":str(e)}
            
        return {}

    def update_project(self, project_id:str, data:dict ):
        
        if project_id:
            try:
                
                if self.config.get("ProjectsCollection"):
                    
                    update = self.patch(f"items/{self.config.get('ProjectsCollection')}/{project_id}", data=data).json()
                    
                    # print(data, update)
                    
                    if update.get("data", None):
                        # Success
                        return {"data" : update}
                    
                    raise Exception(str(update))

            except Exception as e:
                return {"error":str(e)}
            
        return {}

