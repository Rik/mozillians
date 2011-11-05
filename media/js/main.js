var app = {}; // Let's namespace our app's functions in here.

(function($) {
    $().ready(function() {
        $('html').removeClass('no-js').addClass('js');

        // Return the current locale (found in the body attribute
        // as a data attribute).
        app.locale = $('body').data('locale');

        // Return a localized URL.
        app.localeUrl = function(url) {
            return '/' + app.locale + '/' + url.toString();
        }

        // Apply language change once another language is selected
        $('#language').change(function() {
            $('#language-switcher').submit();
        });
        var bid_login_a = '<a href="#">' + $('#browserid-login span').text() + '</a>';
        $('#browserid-login span').replaceWith(bid_login_a);

        var bid_reg_a = '<a class="browserid-register" href="#">' + $('#browserid-register span').text() + '</a>';
        $('#browserid-register span').replaceWith(bid_reg_a);

        $('#browserid-login a').click(_bid_fn('login'));
        $('.browserid-register').click(_bid_fn('register'));
    });

    /**
     * Sets up BrowserID callback.
     * mode - login or register
     *
     * Fragile magick - forms are named browserid-login 
     * and browserid-register
     */
    var _bid_fn = function (mode) {
        return function(event) {
            var form;
            event.preventDefault();
            console.info("Okay");
            navigator.id.getVerifiedEmail(function(assertion) {
                if (assertion) {
                    form = $('form#browserid');
                    $('#id_assertion', form).attr('value', assertion.toString());
                    $('#bid_mode', form).attr('value', mode);
                    form.submit();
                }
            });
        };
    };
})(jQuery);
