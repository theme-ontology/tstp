( function( window, $ ) {
    $( function() {
        var captchaEl = $( '#sample-captcha' ).visualCaptcha({
            imgPath: "VisualCaptcha/public/img/",
            captcha: {
                numberOfImages: 10,
                callbacks: {
                    loaded: function( captcha ) {
                        // Avoid adding the hashtag to the URL when clicking/selecting visualCaptcha options
                        $( '#sample-captcha a' ).on( 'click', function( event ) {
                            event.preventDefault();
                        });
                    }
                },
                routes: {
                    start: '/VisualCaptcha/public/start',
                    image: '/VisualCaptcha/public/image',
                    audio: '/VisualCaptcha/public/audio',
                },
            }
        } );
        var captcha = captchaEl.data( 'captcha' );

        // Show an alert saying if visualCaptcha is filled or not
        var _sayIsVisualCaptchaFilled = function( event ) {
            event.preventDefault();

            if ( captcha.getCaptchaData().valid ) {
                window.alert( 'visualCaptcha is filled!' );
            } else {
                window.alert( 'visualCaptcha is NOT filled!' );
            }
        };

        var statusEl = $( '#status-message' ),
            queryString = window.location.search;
        // Show success/error messages
        if ( queryString.indexOf('status=noCaptcha') !== -1 ) {
            statusEl.html('<div class="status"> <div class="icon-no"></div> <p>visualCaptcha was not started!</p> </div>');
        } else if ( queryString.indexOf('status=validImage') !== -1 ) {
            statusEl.html('<div class="status valid"> <div class="icon-yes"></div> <p>Image was valid!</p> </div>');
        } else if ( queryString.indexOf('status=failedImage') !== -1 ) {
            statusEl.html('<div class="status"> <div class="icon-no"></div> <p>Image was NOT valid!</p> </div>');
        } else if ( queryString.indexOf('status=validAudio') !== -1 ) {
            statusEl.html('<div class="status valid"> <div class="icon-yes"></div> <p>Accessibility answer was valid!</p> </div>');
        } else if ( queryString.indexOf('status=failedAudio') !== -1 ) {
            statusEl.html('<div class="status"> <div class="icon-no"></div> <p>Accessibility answer was NOT valid!</p> </div>');
        } else if ( queryString.indexOf('status=failedPost') !== -1 ) {
            statusEl.html('<div class="status"> <div class="icon-no"></div> <p>No visualCaptcha answer was given!</p> </div>');
        }

        // Bind that function to the appropriate link
        $( '#check-is-filled' ).on( 'click.app', _sayIsVisualCaptchaFilled );
    } );
}( window, jQuery ) );
