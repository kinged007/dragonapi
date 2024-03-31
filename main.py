import uvicorn



if __name__ == '__main__':
                                     
    # from config.config import Settings
    import os
    from loguru import logger as log
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()
    
    # log.debug(os.environ['ssl_keyfile'])
    if os.environ.get('ssl_keyfile',"") and os.environ.get('ssl_certfile',""):
        if os.path.exists(os.environ.get('ssl_keyfile',"")) and os.path.exists(os.environ.get('ssl_certfile',"")):
            # We have SSL Certificate
            uvicorn.run('app:app', host="0.0.0.0", port=8443, 
                        ssl_keyfile=os.environ.get('ssl_keyfile',""),
                        ssl_certfile=os.environ.get('ssl_certfile',""), 
                        workers=3)
            exit(1)
    
    ## potentiall in development
    import sys
    try:
        port = int(sys.argv[sys.argv.index("--port")+1].strip()) if '--port' in sys.argv else 88
    except Exception as e:
        log.error(e)
        port = 88
        
    if "--reload" in sys.argv:
        uvicorn.run('app:app', host="0.0.0.0", port=port, reload=True)
    else:
        uvicorn.run('app:app', host="0.0.0.0", port=port, workers=3)