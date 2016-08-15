(function(){
    switchLanguage();
})();


/**** Automatic Language Translation ****/
function switchLanguage() {

    var userLang = navigator.language || navigator.userLanguage;
    var language = 'en';
    if(userLang == 'fr') language = 'fr';
    if(userLang == 'es') language = 'es';

    /* If user has selected a language, we apply it */
    if ($.cookie('app-language')) {
        var language = $.cookie('app-language'); 
    }
    /* We get current language on page load */
    $("[data-translate]").jqTranslate('js/plugins/translator/translate', {
        forceLang: language
    });

    /* Change language on click in a select input for example */
    $('#switch-lang').on('change', function(e) {
        e.preventDefault();
        language = $(this).val();
        $("[data-translate]").jqTranslate('js/plugins/translator/translate', {
            forceLang: language
        });

        /* We save language inside a cookie */
        $.cookie('app-language', language);
        $.cookie('app-language', language, { path: '/' });
    });
  
}