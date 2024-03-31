
def google_free_translate(text, target_lang, source_lang = None):
    from easygoogletranslate import EasyGoogleTranslate
    translator = EasyGoogleTranslate(
        source_language=source_lang,
        target_language=target_lang,
        timeout=10
    )
    result = translator.translate(text)
    # print(result)
    return result