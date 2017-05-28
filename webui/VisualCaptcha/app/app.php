<?php

// Allow requests from all origins
$app->response[ 'Access-Control-Allow-Origin' ] = '*';

// Inject Session closure into app
$app->session = function() use( $app ) {
    if ( $namespace = $app->request->params( 'namespace' ) ) {
        $session = new \visualCaptcha\Session( 'visualcaptcha_' . $namespace );
    } else {
        $session = new \visualCaptcha\Session();
    }

    return $session;
};

// Demo
// -----------------------------------------------------------------------------
$app->get( '/', function() use( $app ) {
    include __DIR__ . '/views/demo.php';
} );

// Show version
// -----------------------------------------------------------------------------
$app->get( '/version', function() use( $app ) {
    echo $app->config( 'version' );
} );

// Populates captcha data into session object
// -----------------------------------------------------------------------------
// @param howmany is required, the number of images to generate
$app->get( '/start/:howmany', function( $howMany ) use( $app ) {
    $captcha = new \visualCaptcha\Captcha( $app->session );
    $captcha->generate( $howMany );

    $app->response[ 'Content-Type' ] = 'application/json';
    echo json_encode( $captcha->getFrontEndData() );
} );

// Streams captcha images from disk
// -----------------------------------------------------------------------------
// @param index is required, the index of the image you wish to get
$app->get( '/image/:index', function( $index ) use( $app ) {
    $captcha = new \visualCaptcha\Captcha( $app->session );

    if ( ! $captcha->streamImage(
            $app->response,
            $index,
            $app->request->params( 'retina' )
    ) ) {
        $app->pass();
    }
} );

// Streams captcha audio from disk
// -----------------------------------------------------------------------------
// @param type is optional and defaults to 'mp3', but can also be 'ogg'
$app->get( '/audio(/:type)', function( $type = 'mp3' ) use( $app ) {
    $captcha = new \visualCaptcha\Captcha( $app->session );

    if ( ! $captcha->streamAudio( $app->response, $type ) ) {
        $app->pass();
    }
} );


// Logout/invalidate request
// -----------------------------------------------------------------------------
$app->get( '/invalidate', function() use( $app ) {
    $_SESSION['captchaBalance'] = 0;
    $app->response[ 'Content-Type' ] = 'application/json';
    echo json_encode(True);
} );


// Try to validate the captcha
// -----------------------------------------------------------------------------
$app->post( '/try', function() use( $app ) {
    $captcha = new \visualCaptcha\Captcha( $app->session );
    $frontendData = $captcha->getFrontendData();
    $params = Array();

    // Load the namespace into url params, if set
    if ( $namespace = $app->request->params( 'namespace' ) ) {
        $params[] =  'namespace=' . $namespace;
    }

    if (!isset($_SESSION['captchaBalance']))
    {
        $_SESSION['captchaBalance'] = 0;
    }

    if ( ! $frontendData ) {
        $params[] = 'status=noCaptcha';
    } else {
        // If an image field name was submitted, try to validate it
        if ( $imageAnswer = $app->request->params( $frontendData[ 'imageFieldName' ] ) ) {
            if ( $captcha->validateImage( $imageAnswer ) ) {
                $_SESSION['captchaBalance'] += 1;
                $params[] = 'status=validImage';
            } else {
                $_SESSION['captchaBalance'] -= 1;
                $params[] = 'status=failedImage';
            }
        } else if ( $audioAnswer = $app->request->params( $frontendData[ 'audioFieldName' ] ) ) {
            if ( $captcha->validateAudio( $audioAnswer ) ) {
                $_SESSION['captchaBalance'] += 1;
                $params[] = 'status=validAudio';
            } else {
                $_SESSION['captchaBalance'] -= 1;
                $params[] = 'status=failedAudio';
            }
        } else {
            $params[] = 'status=failedPost';
        }

        $howMany = count( $captcha->getImageOptions() );
        $captcha->generate( $howMany );
    }

    $params[] = $_SESSION['captchaBalance'];

    $app->response[ 'Content-Type' ] = 'application/json';
    echo json_encode($params);
} );

// Error Handling
// -----------------------------------------------------------------------------
$app->error( function( \Exception $e ) use( $app ) {
    $app->response->setStatus( 500 );

    include __DIR__ . '/views/error.php';
} );

?>