#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// Install plugin network administration panel.
#// 
#// @package WordPress
#// @subpackage Multisite
#// @since 3.1.0
#//
if (php_isset(lambda : PHP_REQUEST["tab"])) and "plugin-information" == PHP_REQUEST["tab"]:
    php_define("IFRAME_REQUEST", True)
# end if
#// Load WordPress Administration Bootstrap
php_include_file(__DIR__ + "/admin.php", once=True)
php_include_file(ABSPATH + "wp-admin/plugin-install.php", once=False)
