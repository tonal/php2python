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
#// oEmbed API: Top-level oEmbed functionality
#// 
#// @package WordPress
#// @subpackage oEmbed
#// @since 4.4.0
#// 
#// 
#// Registers an embed handler.
#// 
#// Should probably only be used for sites that do not support oEmbed.
#// 
#// @since 2.9.0
#// 
#// @global WP_Embed $wp_embed
#// 
#// @param string   $id       An internal ID/name for the handler. Needs to be unique.
#// @param string   $regex    The regex that will be used to see if this handler should be used for a URL.
#// @param callable $callback The callback function that will be called if the regex is matched.
#// @param int      $priority Optional. Used to specify the order in which the registered handlers will
#// be tested. Default 10.
#//
def wp_embed_register_handler(id=None, regex=None, callback=None, priority=10, *args_):
    
    global wp_embed
    php_check_if_defined("wp_embed")
    wp_embed.register_handler(id, regex, callback, priority)
# end def wp_embed_register_handler
#// 
#// Unregisters a previously-registered embed handler.
#// 
#// @since 2.9.0
#// 
#// @global WP_Embed $wp_embed
#// 
#// @param string $id       The handler ID that should be removed.
#// @param int    $priority Optional. The priority of the handler to be removed. Default 10.
#//
def wp_embed_unregister_handler(id=None, priority=10, *args_):
    
    global wp_embed
    php_check_if_defined("wp_embed")
    wp_embed.unregister_handler(id, priority)
# end def wp_embed_unregister_handler
#// 
#// Creates default array of embed parameters.
#// 
#// The width defaults to the content width as specified by the theme. If the
#// theme does not specify a content width, then 500px is used.
#// 
#// The default height is 1.5 times the width, or 1000px, whichever is smaller.
#// 
#// The {@see 'embed_defaults'} filter can be used to adjust either of these values.
#// 
#// @since 2.9.0
#// 
#// @global int $content_width
#// 
#// @param string $url Optional. The URL that should be embedded. Default empty.
#// 
#// @return array {
#// Indexed array of the embed width and height in pixels.
#// 
#// @type int $0 The embed width.
#// @type int $1 The embed height.
#// }
#//
def wp_embed_defaults(url="", *args_):
    
    if (not php_empty(lambda : PHP_GLOBALS["content_width"])):
        width = int(PHP_GLOBALS["content_width"])
    # end if
    if php_empty(lambda : width):
        width = 500
    # end if
    height = php_min(ceil(width * 1.5), 1000)
    #// 
    #// Filters the default array of embed dimensions.
    #// 
    #// @since 2.9.0
    #// 
    #// @param array  $size {
    #// Indexed array of the embed width and height in pixels.
    #// 
    #// @type int $0 The embed width.
    #// @type int $1 The embed height.
    #// }
    #// @param string $url  The URL that should be embedded.
    #//
    return apply_filters("embed_defaults", compact("width", "height"), url)
# end def wp_embed_defaults
#// 
#// Attempts to fetch the embed HTML for a provided URL using oEmbed.
#// 
#// @since 2.9.0
#// 
#// @see WP_oEmbed
#// 
#// @param string $url  The URL that should be embedded.
#// @param array  $args Optional. Additional arguments and parameters for retrieving embed HTML.
#// Default empty.
#// @return string|false The embed HTML on success, false on failure.
#//
def wp_oembed_get(url=None, args="", *args_):
    
    oembed = _wp_oembed_get_object()
    return oembed.get_html(url, args)
# end def wp_oembed_get
#// 
#// Returns the initialized WP_oEmbed object.
#// 
#// @since 2.9.0
#// @access private
#// 
#// @staticvar WP_oEmbed $wp_oembed
#// 
#// @return WP_oEmbed object.
#//
def _wp_oembed_get_object(*args_):
    
    wp_oembed = None
    if php_is_null(wp_oembed):
        wp_oembed = php_new_class("WP_oEmbed", lambda : WP_oEmbed())
    # end if
    return wp_oembed
# end def _wp_oembed_get_object
#// 
#// Adds a URL format and oEmbed provider URL pair.
#// 
#// @since 2.9.0
#// 
#// @see WP_oEmbed
#// 
#// @param string  $format   The format of URL that this provider can handle. You can use asterisks
#// as wildcards.
#// @param string  $provider The URL to the oEmbed provider.
#// @param boolean $regex    Optional. Whether the `$format` parameter is in a RegEx format. Default false.
#//
def wp_oembed_add_provider(format=None, provider=None, regex=False, *args_):
    
    if did_action("plugins_loaded"):
        oembed = _wp_oembed_get_object()
        oembed.providers[format] = Array(provider, regex)
    else:
        WP_oEmbed._add_provider_early(format, provider, regex)
    # end if
# end def wp_oembed_add_provider
#// 
#// Removes an oEmbed provider.
#// 
#// @since 3.5.0
#// 
#// @see WP_oEmbed
#// 
#// @param string $format The URL format for the oEmbed provider to remove.
#// @return bool Was the provider removed successfully?
#//
def wp_oembed_remove_provider(format=None, *args_):
    
    if did_action("plugins_loaded"):
        oembed = _wp_oembed_get_object()
        if (php_isset(lambda : oembed.providers[format])):
            oembed.providers[format] = None
            return True
        # end if
    else:
        WP_oEmbed._remove_provider_early(format)
    # end if
    return False
# end def wp_oembed_remove_provider
#// 
#// Determines if default embed handlers should be loaded.
#// 
#// Checks to make sure that the embeds library hasn't already been loaded. If
#// it hasn't, then it will load the embeds library.
#// 
#// @since 2.9.0
#// 
#// @see wp_embed_register_handler()
#//
def wp_maybe_load_embeds(*args_):
    
    #// 
    #// Filters whether to load the default embed handlers.
    #// 
    #// Returning a falsey value will prevent loading the default embed handlers.
    #// 
    #// @since 2.9.0
    #// 
    #// @param bool $maybe_load_embeds Whether to load the embeds library. Default true.
    #//
    if (not apply_filters("load_default_embeds", True)):
        return
    # end if
    wp_embed_register_handler("youtube_embed_url", "#https?://(www.)?youtube\\.com/(?:v|embed)/([^/]+)#i", "wp_embed_handler_youtube")
    #// 
    #// Filters the audio embed handler callback.
    #// 
    #// @since 3.6.0
    #// 
    #// @param callable $handler Audio embed handler callback function.
    #//
    wp_embed_register_handler("audio", "#^https?://.+?\\.(" + join("|", wp_get_audio_extensions()) + ")$#i", apply_filters("wp_audio_embed_handler", "wp_embed_handler_audio"), 9999)
    #// 
    #// Filters the video embed handler callback.
    #// 
    #// @since 3.6.0
    #// 
    #// @param callable $handler Video embed handler callback function.
    #//
    wp_embed_register_handler("video", "#^https?://.+?\\.(" + join("|", wp_get_video_extensions()) + ")$#i", apply_filters("wp_video_embed_handler", "wp_embed_handler_video"), 9999)
# end def wp_maybe_load_embeds
#// 
#// YouTube iframe embed handler callback.
#// 
#// Catches YouTube iframe embed URLs that are not parsable by oEmbed but can be translated into a URL that is.
#// 
#// @since 4.0.0
#// 
#// @global WP_Embed $wp_embed
#// 
#// @param array  $matches The RegEx matches from the provided regex when calling
#// wp_embed_register_handler().
#// @param array  $attr    Embed attributes.
#// @param string $url     The original URL that was matched by the regex.
#// @param array  $rawattr The original unmodified attributes.
#// @return string The embed HTML.
#//
def wp_embed_handler_youtube(matches=None, attr=None, url=None, rawattr=None, *args_):
    
    global wp_embed
    php_check_if_defined("wp_embed")
    embed = wp_embed.autoembed(php_sprintf("https://youtube.com/watch?v=%s", urlencode(matches[2])))
    #// 
    #// Filters the YoutTube embed output.
    #// 
    #// @since 4.0.0
    #// 
    #// @see wp_embed_handler_youtube()
    #// 
    #// @param string $embed   YouTube embed output.
    #// @param array  $attr    An array of embed attributes.
    #// @param string $url     The original URL that was matched by the regex.
    #// @param array  $rawattr The original unmodified attributes.
    #//
    return apply_filters("wp_embed_handler_youtube", embed, attr, url, rawattr)
# end def wp_embed_handler_youtube
#// 
#// Audio embed handler callback.
#// 
#// @since 3.6.0
#// 
#// @param array  $matches The RegEx matches from the provided regex when calling wp_embed_register_handler().
#// @param array  $attr Embed attributes.
#// @param string $url The original URL that was matched by the regex.
#// @param array  $rawattr The original unmodified attributes.
#// @return string The embed HTML.
#//
def wp_embed_handler_audio(matches=None, attr=None, url=None, rawattr=None, *args_):
    
    audio = php_sprintf("[audio src=\"%s\" /]", esc_url(url))
    #// 
    #// Filters the audio embed output.
    #// 
    #// @since 3.6.0
    #// 
    #// @param string $audio   Audio embed output.
    #// @param array  $attr    An array of embed attributes.
    #// @param string $url     The original URL that was matched by the regex.
    #// @param array  $rawattr The original unmodified attributes.
    #//
    return apply_filters("wp_embed_handler_audio", audio, attr, url, rawattr)
# end def wp_embed_handler_audio
#// 
#// Video embed handler callback.
#// 
#// @since 3.6.0
#// 
#// @param array  $matches The RegEx matches from the provided regex when calling wp_embed_register_handler().
#// @param array  $attr    Embed attributes.
#// @param string $url     The original URL that was matched by the regex.
#// @param array  $rawattr The original unmodified attributes.
#// @return string The embed HTML.
#//
def wp_embed_handler_video(matches=None, attr=None, url=None, rawattr=None, *args_):
    
    dimensions = ""
    if (not php_empty(lambda : rawattr["width"])) and (not php_empty(lambda : rawattr["height"])):
        dimensions += php_sprintf("width=\"%d\" ", int(rawattr["width"]))
        dimensions += php_sprintf("height=\"%d\" ", int(rawattr["height"]))
    # end if
    video = php_sprintf("[video %s src=\"%s\" /]", dimensions, esc_url(url))
    #// 
    #// Filters the video embed output.
    #// 
    #// @since 3.6.0
    #// 
    #// @param string $video   Video embed output.
    #// @param array  $attr    An array of embed attributes.
    #// @param string $url     The original URL that was matched by the regex.
    #// @param array  $rawattr The original unmodified attributes.
    #//
    return apply_filters("wp_embed_handler_video", video, attr, url, rawattr)
# end def wp_embed_handler_video
#// 
#// Registers the oEmbed REST API route.
#// 
#// @since 4.4.0
#//
def wp_oembed_register_route(*args_):
    
    controller = php_new_class("WP_oEmbed_Controller", lambda : WP_oEmbed_Controller())
    controller.register_routes()
# end def wp_oembed_register_route
#// 
#// Adds oEmbed discovery links in the website <head>.
#// 
#// @since 4.4.0
#//
def wp_oembed_add_discovery_links(*args_):
    
    output = ""
    if is_singular():
        output += "<link rel=\"alternate\" type=\"application/json+oembed\" href=\"" + esc_url(get_oembed_endpoint_url(get_permalink())) + "\" />" + "\n"
        if php_class_exists("SimpleXMLElement"):
            output += "<link rel=\"alternate\" type=\"text/xml+oembed\" href=\"" + esc_url(get_oembed_endpoint_url(get_permalink(), "xml")) + "\" />" + "\n"
        # end if
    # end if
    #// 
    #// Filters the oEmbed discovery links HTML.
    #// 
    #// @since 4.4.0
    #// 
    #// @param string $output HTML of the discovery links.
    #//
    php_print(apply_filters("oembed_discovery_links", output))
# end def wp_oembed_add_discovery_links
#// 
#// Adds the necessary JavaScript to communicate with the embedded iframes.
#// 
#// @since 4.4.0
#//
def wp_oembed_add_host_js(*args_):
    
    wp_enqueue_script("wp-embed")
# end def wp_oembed_add_host_js
#// 
#// Retrieves the URL to embed a specific post in an iframe.
#// 
#// @since 4.4.0
#// 
#// @param int|WP_Post $post Optional. Post ID or object. Defaults to the current post.
#// @return string|false The post embed URL on success, false if the post doesn't exist.
#//
def get_post_embed_url(post=None, *args_):
    
    post = get_post(post)
    if (not post):
        return False
    # end if
    embed_url = trailingslashit(get_permalink(post)) + user_trailingslashit("embed")
    path_conflict = get_page_by_path(php_str_replace(home_url(), "", embed_url), OBJECT, get_post_types(Array({"public": True})))
    if (not get_option("permalink_structure")) or path_conflict:
        embed_url = add_query_arg(Array({"embed": "true"}), get_permalink(post))
    # end if
    #// 
    #// Filters the URL to embed a specific post.
    #// 
    #// @since 4.4.0
    #// 
    #// @param string  $embed_url The post embed URL.
    #// @param WP_Post $post      The corresponding post object.
    #//
    return esc_url_raw(apply_filters("post_embed_url", embed_url, post))
# end def get_post_embed_url
#// 
#// Retrieves the oEmbed endpoint URL for a given permalink.
#// 
#// Pass an empty string as the first argument to get the endpoint base URL.
#// 
#// @since 4.4.0
#// 
#// @param string $permalink Optional. The permalink used for the `url` query arg. Default empty.
#// @param string $format    Optional. The requested response format. Default 'json'.
#// @return string The oEmbed endpoint URL.
#//
def get_oembed_endpoint_url(permalink="", format="json", *args_):
    
    url = rest_url("oembed/1.0/embed")
    if "" != permalink:
        url = add_query_arg(Array({"url": urlencode(permalink), "format": format if "json" != format else False}), url)
    # end if
    #// 
    #// Filters the oEmbed endpoint URL.
    #// 
    #// @since 4.4.0
    #// 
    #// @param string $url       The URL to the oEmbed endpoint.
    #// @param string $permalink The permalink used for the `url` query arg.
    #// @param string $format    The requested response format.
    #//
    return apply_filters("oembed_endpoint_url", url, permalink, format)
# end def get_oembed_endpoint_url
#// 
#// Retrieves the embed code for a specific post.
#// 
#// @since 4.4.0
#// 
#// @param int         $width  The width for the response.
#// @param int         $height The height for the response.
#// @param int|WP_Post $post   Optional. Post ID or object. Default is global `$post`.
#// @return string|false Embed code on success, false if post doesn't exist.
#//
def get_post_embed_html(width=None, height=None, post=None, *args_):
    
    post = get_post(post)
    if (not post):
        return False
    # end if
    embed_url = get_post_embed_url(post)
    output = "<blockquote class=\"wp-embedded-content\"><a href=\"" + esc_url(get_permalink(post)) + "\">" + get_the_title(post) + "</a></blockquote>\n"
    output += "<script type='text/javascript'>\n"
    output += "<!--//--><![CDATA[//><!--\n"
    if SCRIPT_DEBUG:
        output += php_file_get_contents(ABSPATH + WPINC + "/js/wp-embed.js")
    else:
        #// 
        #// If you're looking at a src version of this file, you'll see an "include"
        #// statement below. This is used by the `npm run build` process to directly
        #// include a minified version of wp-embed.js, instead of using the
        #// file_get_contents() method from above.
        #// 
        #// If you're looking at a build version of this file, you'll see a string of
        #// minified JavaScript. If you need to debug it, please turn on SCRIPT_DEBUG
        #// and edit wp-embed.js directly.
        #//
        output += "     /*! This file is auto-generated */\n        !function(d,l){\"use strict\";var e=!1,o=!1;if(l.querySelector)if(d.addEventListener)e=!0;if(d.wp=d.wp||{},!d.wp.receiveEmbedMessage)if(d.wp.receiveEmbedMessage=function(e){var t=e.data;if(t)if(t.secret||t.message||t.value)if(!/[^a-zA-Z0-9]/.test(t.secret)){var r,a,i,s,n,o=l.querySelectorAll('iframe[data-secret=\"'+t.secret+'\"]'),c=l.querySelectorAll('blockquote[data-secret=\"'+t.secret+'\"]');for(r=0;r<c.length;r++)c[r].style.display=\"none\";for(r=0;r<o.length;r++)if(a=o[r],e.source===a.contentWindow){if(a.removeAttribute(\"style\"),\"height\"===t.message){if(1e3<(i=parseInt(t.value,10)))i=1e3;else if(~~i<200)i=200;a.height=i}if(\"link\"===t.message)if(s=l.createElement(\"a\"),n=l.createElement(\"a\"),s.href=a.getAttribute(\"src\"),n.href=t.value,n.host===s.host)if(l.activeElement===a)d.top.location.href=t.value}}},e)d.addEventListener(\"message\",d.wp.receiveEmbedMessage,!1),l.addEventListener(\"DOMContentLoaded\",t,!1),d.addEventListener(\"load\",t,!1);function t(){if(!o){o=!0;var e,t,r,a,i=-1!==navigator.appVersion.indexOf(\"MSIE 10\"),s=!!navigator.userAgent.match(/Trident.*rv:11\\./),n=l.querySelectorAll(\"iframe.wp-embedded-content\");for(t=0;t<n.length;t++){if(!(r=n[t]).getAttribute(\"data-secret\"))a=Math.random().toString(36).substr(2,10),r.src+=\"#?secret=\"+a,r.setAttribute(\"data-secret\",a);if(i||s)(e=r.cloneNode(!0)).removeAttribute(\"security\"),r.parentNode.replaceChild(e,r)}}}}(window,document);"
    # end if
    output += "\n//--><!]]>"
    output += "\n</script>"
    output += php_sprintf("<iframe sandbox=\"allow-scripts\" security=\"restricted\" src=\"%1$s\" width=\"%2$d\" height=\"%3$d\" title=\"%4$s\" frameborder=\"0\" marginwidth=\"0\" marginheight=\"0\" scrolling=\"no\" class=\"wp-embedded-content\"></iframe>", esc_url(embed_url), absint(width), absint(height), esc_attr(php_sprintf(__("&#8220;%1$s&#8221; &#8212; %2$s"), get_the_title(post), get_bloginfo("name"))))
    #// 
    #// Filters the embed HTML output for a given post.
    #// 
    #// @since 4.4.0
    #// 
    #// @param string  $output The default iframe tag to display embedded content.
    #// @param WP_Post $post   Current post object.
    #// @param int     $width  Width of the response.
    #// @param int     $height Height of the response.
    #//
    return apply_filters("embed_html", output, post, width, height)
# end def get_post_embed_html
#// 
#// Retrieves the oEmbed response data for a given post.
#// 
#// @since 4.4.0
#// 
#// @param WP_Post|int $post  Post object or ID.
#// @param int         $width The requested width.
#// @return array|false Response data on success, false if post doesn't exist.
#//
def get_oembed_response_data(post=None, width=None, *args_):
    
    post = get_post(post)
    width = absint(width)
    if (not post):
        return False
    # end if
    if "publish" != get_post_status(post):
        return False
    # end if
    #// 
    #// Filters the allowed minimum and maximum widths for the oEmbed response.
    #// 
    #// @since 4.4.0
    #// 
    #// @param array $min_max_width {
    #// Minimum and maximum widths for the oEmbed response.
    #// 
    #// @type int $min Minimum width. Default 200.
    #// @type int $max Maximum width. Default 600.
    #// }
    #//
    min_max_width = apply_filters("oembed_min_max_width", Array({"min": 200, "max": 600}))
    width = php_min(php_max(min_max_width["min"], width), min_max_width["max"])
    height = php_max(ceil(width / 16 * 9), 200)
    data = Array({"version": "1.0", "provider_name": get_bloginfo("name"), "provider_url": get_home_url(), "author_name": get_bloginfo("name"), "author_url": get_home_url(), "title": get_the_title(post), "type": "link"})
    author = get_userdata(post.post_author)
    if author:
        data["author_name"] = author.display_name
        data["author_url"] = get_author_posts_url(author.ID)
    # end if
    #// 
    #// Filters the oEmbed response data.
    #// 
    #// @since 4.4.0
    #// 
    #// @param array   $data   The response data.
    #// @param WP_Post $post   The post object.
    #// @param int     $width  The requested width.
    #// @param int     $height The calculated height.
    #//
    return apply_filters("oembed_response_data", data, post, width, height)
# end def get_oembed_response_data
#// 
#// Retrieves the oEmbed response data for a given URL.
#// 
#// @since 5.0.0
#// 
#// @param string $url  The URL that should be inspected for discovery `<link>` tags.
#// @param array  $args oEmbed remote get arguments.
#// @return object|false oEmbed response data if the URL does belong to the current site. False otherwise.
#//
def get_oembed_response_data_for_url(url=None, args=None, *args_):
    
    switched_blog = False
    if is_multisite():
        url_parts = wp_parse_args(wp_parse_url(url), Array({"host": "", "path": "/"}))
        qv = Array({"domain": url_parts["host"], "path": "/", "update_site_meta_cache": False})
        #// In case of subdirectory configs, set the path.
        if (not is_subdomain_install()):
            path = php_explode("/", php_ltrim(url_parts["path"], "/"))
            path = reset(path)
            if path:
                qv["path"] = get_network().path + path + "/"
            # end if
        # end if
        sites = get_sites(qv)
        site = reset(sites)
        if site and get_current_blog_id() != int(site.blog_id):
            switch_to_blog(site.blog_id)
            switched_blog = True
        # end if
    # end if
    post_id = url_to_postid(url)
    #// This filter is documented in wp-includes/class-wp-oembed-controller.php
    post_id = apply_filters("oembed_request_post_id", post_id, url)
    if (not post_id):
        if switched_blog:
            restore_current_blog()
        # end if
        return False
    # end if
    width = args["width"] if (php_isset(lambda : args["width"])) else 0
    data = get_oembed_response_data(post_id, width)
    if switched_blog:
        restore_current_blog()
    # end if
    return data if data else False
# end def get_oembed_response_data_for_url
#// 
#// Filters the oEmbed response data to return an iframe embed code.
#// 
#// @since 4.4.0
#// 
#// @param array   $data   The response data.
#// @param WP_Post $post   The post object.
#// @param int     $width  The requested width.
#// @param int     $height The calculated height.
#// @return array The modified response data.
#//
def get_oembed_response_data_rich(data=None, post=None, width=None, height=None, *args_):
    
    data["width"] = absint(width)
    data["height"] = absint(height)
    data["type"] = "rich"
    data["html"] = get_post_embed_html(width, height, post)
    #// Add post thumbnail to response if available.
    thumbnail_id = False
    if has_post_thumbnail(post.ID):
        thumbnail_id = get_post_thumbnail_id(post.ID)
    # end if
    if "attachment" == get_post_type(post):
        if wp_attachment_is_image(post):
            thumbnail_id = post.ID
        elif wp_attachment_is("video", post):
            thumbnail_id = get_post_thumbnail_id(post)
            data["type"] = "video"
        # end if
    # end if
    if thumbnail_id:
        thumbnail_url, thumbnail_width, thumbnail_height = wp_get_attachment_image_src(thumbnail_id, Array(width, 99999))
        data["thumbnail_url"] = thumbnail_url
        data["thumbnail_width"] = thumbnail_width
        data["thumbnail_height"] = thumbnail_height
    # end if
    return data
# end def get_oembed_response_data_rich
#// 
#// Ensures that the specified format is either 'json' or 'xml'.
#// 
#// @since 4.4.0
#// 
#// @param string $format The oEmbed response format. Accepts 'json' or 'xml'.
#// @return string The format, either 'xml' or 'json'. Default 'json'.
#//
def wp_oembed_ensure_format(format=None, *args_):
    
    if (not php_in_array(format, Array("json", "xml"), True)):
        return "json"
    # end if
    return format
# end def wp_oembed_ensure_format
#// 
#// Hooks into the REST API output to print XML instead of JSON.
#// 
#// This is only done for the oEmbed API endpoint,
#// which supports both formats.
#// 
#// @access private
#// @since 4.4.0
#// 
#// @param bool                      $served  Whether the request has already been served.
#// @param WP_HTTP_ResponseInterface $result  Result to send to the client. Usually a WP_REST_Response.
#// @param WP_REST_Request           $request Request used to generate the response.
#// @param WP_REST_Server            $server  Server instance.
#// @return true
#//
def _oembed_rest_pre_serve_request(served=None, result=None, request=None, server=None, *args_):
    
    params = request.get_params()
    if "/oembed/1.0/embed" != request.get_route() or "GET" != request.get_method():
        return served
    # end if
    if (not (php_isset(lambda : params["format"]))) or "xml" != params["format"]:
        return served
    # end if
    #// Embed links inside the request.
    data = server.response_to_data(result, False)
    if (not php_class_exists("SimpleXMLElement")):
        status_header(501)
        php_print(get_status_header_desc(501))
        php_exit()
    # end if
    result = _oembed_create_xml(data)
    #// Bail if there's no XML.
    if (not result):
        status_header(501)
        return get_status_header_desc(501)
    # end if
    if (not php_headers_sent()):
        server.send_header("Content-Type", "text/xml; charset=" + get_option("blog_charset"))
    # end if
    php_print(result)
    return True
# end def _oembed_rest_pre_serve_request
#// 
#// Creates an XML string from a given array.
#// 
#// @since 4.4.0
#// @access private
#// 
#// @param array            $data The original oEmbed response data.
#// @param SimpleXMLElement $node Optional. XML node to append the result to recursively.
#// @return string|false XML string on success, false on error.
#//
def _oembed_create_xml(data=None, node=None, *args_):
    
    if (not php_is_array(data)) or php_empty(lambda : data):
        return False
    # end if
    if None == node:
        node = php_new_class("SimpleXMLElement", lambda : SimpleXMLElement("<oembed></oembed>"))
    # end if
    for key,value in data:
        if php_is_numeric(key):
            key = "oembed"
        # end if
        if php_is_array(value):
            item = node.addchild(key)
            _oembed_create_xml(value, item)
        else:
            node.addchild(key, esc_html(value))
        # end if
    # end for
    return node.asxml()
# end def _oembed_create_xml
#// 
#// Filters the given oEmbed HTML to make sure iframes have a title attribute.
#// 
#// @since 5.2.0
#// 
#// @param string $result The oEmbed HTML result.
#// @param object $data   A data object result from an oEmbed provider.
#// @param string $url    The URL of the content to be embedded.
#// @return string The filtered oEmbed result.
#//
def wp_filter_oembed_iframe_title_attribute(result=None, data=None, url=None, *args_):
    
    if False == result or (not php_in_array(data.type, Array("rich", "video"))):
        return result
    # end if
    title = data.title if (not php_empty(lambda : data.title)) else ""
    pattern = "`<iframe[^>]*?title=(\\\\'|\\\\\"|['\"])([^>]*?)\\1`i"
    has_title_attr = php_preg_match(pattern, result, matches)
    if has_title_attr and (not php_empty(lambda : matches[2])):
        title = matches[2]
    # end if
    #// 
    #// Filters the title attribute of the given oEmbed HTML iframe.
    #// 
    #// @since 5.2.0
    #// 
    #// @param string $title  The title attribute.
    #// @param string $result The oEmbed HTML result.
    #// @param object $data   A data object result from an oEmbed provider.
    #// @param string $url    The URL of the content to be embedded.
    #//
    title = apply_filters("oembed_iframe_title_attribute", title, result, data, url)
    if "" == title:
        return result
    # end if
    if has_title_attr:
        #// Remove the old title, $matches[1]: quote, $matches[2]: title attribute value.
        result = php_str_replace(" title=" + matches[1] + matches[2] + matches[1], "", result)
    # end if
    return php_str_ireplace("<iframe ", php_sprintf("<iframe title=\"%s\" ", esc_attr(title)), result)
# end def wp_filter_oembed_iframe_title_attribute
#// 
#// Filters the given oEmbed HTML.
#// 
#// If the `$url` isn't on the trusted providers list,
#// we need to filter the HTML heavily for security.
#// 
#// Only filters 'rich' and 'video' response types.
#// 
#// @since 4.4.0
#// 
#// @param string $result The oEmbed HTML result.
#// @param object $data   A data object result from an oEmbed provider.
#// @param string $url    The URL of the content to be embedded.
#// @return string The filtered and sanitized oEmbed result.
#//
def wp_filter_oembed_result(result=None, data=None, url=None, *args_):
    
    if False == result or (not php_in_array(data.type, Array("rich", "video"))):
        return result
    # end if
    wp_oembed = _wp_oembed_get_object()
    #// Don't modify the HTML for trusted providers.
    if False != wp_oembed.get_provider(url, Array({"discover": False})):
        return result
    # end if
    allowed_html = Array({"a": Array({"href": True})}, {"blockquote": Array(), "iframe": Array({"src": True, "width": True, "height": True, "frameborder": True, "marginwidth": True, "marginheight": True, "scrolling": True, "title": True})})
    html = wp_kses(result, allowed_html)
    php_preg_match("|(<blockquote>.*?</blockquote>)?.*(<iframe.*?></iframe>)|ms", html, content)
    #// We require at least the iframe to exist.
    if php_empty(lambda : content[2]):
        return False
    # end if
    html = content[1] + content[2]
    php_preg_match("/ src=(['\"])(.*?)\\1/", html, results)
    if (not php_empty(lambda : results)):
        secret = wp_generate_password(10, False)
        url = esc_url(str(results[2]) + str("#?secret=") + str(secret))
        q = results[1]
        html = php_str_replace(results[0], " src=" + q + url + q + " data-secret=" + q + secret + q, html)
        html = php_str_replace("<blockquote", str("<blockquote data-secret=\"") + str(secret) + str("\""), html)
    # end if
    allowed_html["blockquote"]["data-secret"] = True
    allowed_html["iframe"]["data-secret"] = True
    html = wp_kses(html, allowed_html)
    if (not php_empty(lambda : content[1])):
        #// We have a blockquote to fall back on. Hide the iframe by default.
        html = php_str_replace("<iframe", "<iframe style=\"position: absolute; clip: rect(1px, 1px, 1px, 1px);\"", html)
        html = php_str_replace("<blockquote", "<blockquote class=\"wp-embedded-content\"", html)
    # end if
    html = php_str_ireplace("<iframe", "<iframe class=\"wp-embedded-content\" sandbox=\"allow-scripts\" security=\"restricted\"", html)
    return html
# end def wp_filter_oembed_result
#// 
#// Filters the string in the 'more' link displayed after a trimmed excerpt.
#// 
#// Replaces '[...]' (appended to automatically generated excerpts) with an
#// ellipsis and a "Continue reading" link in the embed template.
#// 
#// @since 4.4.0
#// 
#// @param string $more_string Default 'more' string.
#// @return string 'Continue reading' link prepended with an ellipsis.
#//
def wp_embed_excerpt_more(more_string=None, *args_):
    
    if (not is_embed()):
        return more_string
    # end if
    link = php_sprintf("<a href=\"%1$s\" class=\"wp-embed-more\" target=\"_top\">%2$s</a>", esc_url(get_permalink()), php_sprintf(__("Continue reading %s"), "<span class=\"screen-reader-text\">" + get_the_title() + "</span>"))
    return " &hellip; " + link
# end def wp_embed_excerpt_more
#// 
#// Displays the post excerpt for the embed template.
#// 
#// Intended to be used in 'The Loop'.
#// 
#// @since 4.4.0
#//
def the_excerpt_embed(*args_):
    
    output = get_the_excerpt()
    #// 
    #// Filters the post excerpt for the embed template.
    #// 
    #// @since 4.4.0
    #// 
    #// @param string $output The current post excerpt.
    #//
    php_print(apply_filters("the_excerpt_embed", output))
# end def the_excerpt_embed
#// 
#// Filters the post excerpt for the embed template.
#// 
#// Shows players for video and audio attachments.
#// 
#// @since 4.4.0
#// 
#// @param string $content The current post excerpt.
#// @return string The modified post excerpt.
#//
def wp_embed_excerpt_attachment(content=None, *args_):
    
    if is_attachment():
        return prepend_attachment("")
    # end if
    return content
# end def wp_embed_excerpt_attachment
#// 
#// Enqueue embed iframe default CSS and JS & fire do_action('enqueue_embed_scripts')
#// 
#// Enqueue PNG fallback CSS for embed iframe for legacy versions of IE.
#// 
#// Allows plugins to queue scripts for the embed iframe end using wp_enqueue_script().
#// Runs first in oembed_head().
#// 
#// @since 4.4.0
#//
def enqueue_embed_scripts(*args_):
    
    wp_enqueue_style("wp-embed-template-ie")
    #// 
    #// Fires when scripts and styles are enqueued for the embed iframe.
    #// 
    #// @since 4.4.0
    #//
    do_action("enqueue_embed_scripts")
# end def enqueue_embed_scripts
#// 
#// Prints the CSS in the embed iframe header.
#// 
#// @since 4.4.0
#//
def print_embed_styles(*args_):
    
    type_attr = "" if current_theme_supports("html5", "style") else " type=\"text/css\""
    php_print(" <style")
    php_print(type_attr)
    php_print(">\n  ")
    if SCRIPT_DEBUG:
        readfile(ABSPATH + WPINC + "/css/wp-embed-template.css")
    else:
        pass
        php_print("         /*! This file is auto-generated */\n            body,html{padding:0;margin:0}body{font-family:sans-serif}.screen-reader-text{border:0;clip:rect(1px,1px,1px,1px);-webkit-clip-path:inset(50%);clip-path:inset(50%);height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute;width:1px;word-wrap:normal!important}.dashicons{display:inline-block;width:20px;height:20px;background-color:transparent;background-repeat:no-repeat;background-size:20px;background-position:center;transition:background .1s ease-in;position:relative;top:5px}.dashicons-no{background-image:url(\"data:image/svg+xml;charset=utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2020%2020%27%3E%3Cpath%20d%3D%27M15.55%2013.7l-2.19%202.06-3.42-3.65-3.64%203.43-2.06-2.18%203.64-3.43-3.42-3.64%202.18-2.06%203.43%203.64%203.64-3.42%202.05%202.18-3.64%203.43z%27%20fill%3D%27%23fff%27%2F%3E%3C%2Fsvg%3E\")}.dashicons-admin-comments{background-image:url(\"data:image/svg+xml;charset=utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2020%2020%27%3E%3Cpath%20d%3D%27M5%202h9q.82%200%201.41.59T16%204v7q0%20.82-.59%201.41T14%2013h-2l-5%205v-5H5q-.82%200-1.41-.59T3%2011V4q0-.82.59-1.41T5%202z%27%20fill%3D%27%2382878c%27%2F%3E%3C%2Fsvg%3E\")}.wp-embed-comments a:hover .dashicons-admin-comments{background-image:url(\"data:image/svg+xml;charset=utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2020%2020%27%3E%3Cpath%20d%3D%27M5%202h9q.82%200%201.41.59T16%204v7q0%20.82-.59%201.41T14%2013h-2l-5%205v-5H5q-.82%200-1.41-.59T3%2011V4q0-.82.59-1.41T5%202z%27%20fill%3D%27%230073aa%27%2F%3E%3C%2Fsvg%3E\")}.dashicons-share{background-image:url(\"data:image/svg+xml;charset=utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2020%2020%27%3E%3Cpath%20d%3D%27M14.5%2012q1.24%200%202.12.88T17.5%2015t-.88%202.12-2.12.88-2.12-.88T11.5%2015q0-.34.09-.69l-4.38-2.3Q6.32%2013%205%2013q-1.24%200-2.12-.88T2%2010t.88-2.12T5%207q1.3%200%202.21.99l4.38-2.3q-.09-.35-.09-.69%200-1.24.88-2.12T14.5%202t2.12.88T17.5%205t-.88%202.12T14.5%208q-1.3%200-2.21-.99l-4.38%202.3Q8%209.66%208%2010t-.09.69l4.38%202.3q.89-.99%202.21-.99z%27%20fill%3D%27%2382878c%27%2F%3E%3C%2Fsvg%3E\");display:none}.js .dashicons-share{display:inline-block}.wp-embed-share-dialog-open:hover .dashicons-share{background-image:url(\"data:image/svg+xml;charset=utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2020%2020%27%3E%3Cpath%20d%3D%27M14.5%2012q1.24%200%202.12.88T17.5%2015t-.88%202.12-2.12.88-2.12-.88T11.5%2015q0-.34.09-.69l-4.38-2.3Q6.32%2013%205%2013q-1.24%200-2.12-.88T2%2010t.88-2.12T5%207q1.3%200%202.21.99l4.38-2.3q-.09-.35-.09-.69%200-1.24.88-2.12T14.5%202t2.12.88T17.5%205t-.88%202.12T14.5%208q-1.3%200-2.21-.99l-4.38%202.3Q8%209.66%208%2010t-.09.69l4.38%202.3q.89-.99%202.21-.99z%27%20fill%3D%27%230073aa%27%2F%3E%3C%2Fsvg%3E\")}.wp-embed{padding:25px;font-size:14px;font-weight:400;font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Oxygen-Sans,Ubuntu,Cantarell,\"Helvetica Neue\",sans-serif;line-height:1.5;color:#82878c;background:#fff;border:1px solid #e5e5e5;box-shadow:0 1px 1px rgba(0,0,0,.05);overflow:auto;zoom:1}.wp-embed a{color:#82878c;text-decoration:none}.wp-embed a:hover{text-decoration:underline}.wp-embed-featured-image{margin-bottom:20px}.wp-embed-featured-image img{width:100%;height:auto;border:none}.wp-embed-featured-image.square{float:left;max-width:160px;margin-right:20px}.wp-embed p{margin:0}p.wp-embed-heading{margin:0 0 15px;font-weight:600;font-size:22px;line-height:1.3}.wp-embed-heading a{color:#32373c}.wp-embed .wp-embed-more{color:#b4b9be}.wp-embed-footer{display:table;width:100%;margin-top:30px}.wp-embed-site-icon{position:absolute;top:50%;left:0;transform:translateY(-50%);height:25px;width:25px;border:0}.wp-embed-site-title{font-weight:600;line-height:1.78571428}.wp-embed-site-title a{position:relative;display:inline-block;padding-left:35px}.wp-embed-meta,.wp-embed-site-title{display:table-cell}.wp-embed-meta{text-align:right;white-space:nowrap;vertical-align:middle}.wp-embed-comments,.wp-embed-share{display:inline}.wp-embed-meta a:hover{text-decoration:none;color:#0073aa}.wp-embed-comments a{line-height:1.78571428;display:inline-block}.wp-embed-comments+.wp-embed-share{margin-left:10px}.wp-embed-share-dialog{position:absolute;top:0;left:0;right:0;bottom:0;background-color:#222;background-color:rgba(10,10,10,.9);color:#fff;opacity:1;transition:opacity .25s ease-in-out}.wp-embed-share-dialog.hidden{opacity:0;visibility:hidden}.wp-embed-share-dialog-close,.wp-embed-share-dialog-open{margin:-8px 0 0;padding:0;background:0 0;border:none;cursor:pointer;outline:0}.wp-embed-share-dialog-close .dashicons,.wp-embed-share-dialog-open .dashicons{padding:4px}.wp-embed-share-dialog-open .dashicons{top:8px}.wp-embed-share-dialog-close:focus .dashicons,.wp-embed-share-dialog-open:focus .dashicons{box-shadow:0 0 0 1px #5b9dd9,0 0 2px 1px rgba(30,140,190,.8);border-radius:100%}.wp-embed-share-dialog-close{position:absolute;top:20px;right:20px;font-size:22px}.wp-embed-share-dialog-close:hover{text-decoration:none}.wp-embed-share-dialog-close .dashicons{height:24px;width:24px;background-size:24px}.wp-embed-share-dialog-content{height:100%;transform-style:preserve-3d;overflow:hidden}.wp-embed-share-dialog-text{margin-top:25px;padding:20px}.wp-embed-share-tabs{margin:0 0 20px;padding:0;list-style:none}.wp-embed-share-tab-button{display:inline-block}.wp-embed-share-tab-button button{margin:0;padding:0;border:none;background:0 0;font-size:16px;line-height:1.3;color:#aaa;cursor:pointer;transition:color .1s ease-in}.wp-embed-share-tab-button [aria-selected=true]{color:#fff}.wp-embed-share-tab-button button:hover{color:#fff}.wp-embed-share-tab-button+.wp-embed-share-tab-button{margin:0 0 0 10px;padding:0 0 0 11px;border-left:1px solid #aaa}.wp-embed-share-tab[aria-hidden=true]{display:none}p.wp-embed-share-description{margin:0;font-size:14px;line-height:1;font-style:italic;color:#aaa}.wp-embed-share-input{box-sizing:border-box;width:100%;border:none;height:28px;margin:0 0 10px 0;padding:0 5px;font-size:14px;font-weight:400;font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Oxygen-Sans,Ubuntu,Cantarell,\"Helvetica Neue\",sans-serif;line-height:1.5;resize:none;cursor:text}textarea.wp-embed-share-input{height:72px}html[dir=rtl] .wp-embed-featured-image.square{float:right;margin-right:0;margin-left:20px}html[dir=rtl] .wp-embed-site-title a{padding-left:0;padding-right:35px}html[dir=rtl] .wp-embed-site-icon{margin-right:0;margin-left:10px;left:auto;right:0}html[dir=rtl] .wp-embed-meta{text-align:left}html[dir=rtl] .wp-embed-share{margin-left:0;margin-right:10px}html[dir=rtl] .wp-embed-share-dialog-close{right:auto;left:20px}html[dir=rtl] .wp-embed-share-tab-button+.wp-embed-share-tab-button{margin:0 10px 0 0;padding:0 11px 0 0;border-left:none;border-right:1px solid #aaa}\n        ")
    # end if
    php_print(" </style>\n  ")
# end def print_embed_styles
#// 
#// Prints the JavaScript in the embed iframe header.
#// 
#// @since 4.4.0
#//
def print_embed_scripts(*args_):
    
    type_attr = "" if current_theme_supports("html5", "script") else " type=\"text/javascript\""
    php_print(" <script")
    php_print(type_attr)
    php_print(">\n  ")
    if SCRIPT_DEBUG:
        readfile(ABSPATH + WPINC + "/js/wp-embed-template.js")
    else:
        pass
        php_print("         /*! This file is auto-generated */\n            !function(u,c){\"use strict\";var r,t,e,i=c.querySelector&&u.addEventListener,b=!1;function f(e,t){u.parent.postMessage({message:e,value:t,secret:r},\"*\")}function n(){if(!b){b=!0;var e,t=c.querySelector(\".wp-embed-share-dialog\"),r=c.querySelector(\".wp-embed-share-dialog-open\"),i=c.querySelector(\".wp-embed-share-dialog-close\"),n=c.querySelectorAll(\".wp-embed-share-input\"),a=c.querySelectorAll(\".wp-embed-share-tab-button button\"),o=c.querySelector(\".wp-embed-featured-image img\");if(n)for(e=0;e<n.length;e++)n[e].addEventListener(\"click\",function(e){e.target.select()});if(r&&r.addEventListener(\"click\",function(){t.className=t.className.replace(\"hidden\",\"\"),c.querySelector('.wp-embed-share-tab-button [aria-selected=\"true\"]').focus()}),i&&i.addEventListener(\"click\",function(){l()}),a)for(e=0;e<a.length;e++)a[e].addEventListener(\"click\",s),a[e].addEventListener(\"keydown\",d);c.addEventListener(\"keydown\",function(e){27===e.keyCode&&-1===t.className.indexOf(\"hidden\")?l():9===e.keyCode&&function(e){var t=c.querySelector('.wp-embed-share-tab-button [aria-selected=\"true\"]');i!==e.target||e.shiftKey?t===e.target&&e.shiftKey&&(i.focus(),e.preventDefault()):(t.focus(),e.preventDefault())}(e)},!1),u.self!==u.top&&(f(\"height\",Math.ceil(c.body.getBoundingClientRect().height)),o&&o.addEventListener(\"load\",function(){f(\"height\",Math.ceil(c.body.getBoundingClientRect().height))}),c.addEventListener(\"click\",function(e){var t,r=e.target;(t=r.hasAttribute(\"href\")?r.getAttribute(\"href\"):r.parentElement.getAttribute(\"href\"))&&(f(\"link\",t),e.preventDefault())}))}function l(){t.className+=\" hidden\",c.querySelector(\".wp-embed-share-dialog-open\").focus()}function s(e){var t=c.querySelector('.wp-embed-share-tab-button [aria-selected=\"true\"]');t.setAttribute(\"aria-selected\",\"false\"),c.querySelector(\"#\"+t.getAttribute(\"aria-controls\")).setAttribute(\"aria-hidden\",\"true\"),e.target.setAttribute(\"aria-selected\",\"true\"),c.querySelector(\"#\"+e.target.getAttribute(\"aria-controls\")).setAttribute(\"aria-hidden\",\"false\")}function d(e){var t,r,i=e.target,n=i.parentElement.previousElementSibling,a=i.parentElement.nextElementSibling;if(37===e.keyCode)t=n;else{if(39!==e.keyCode)return!1;t=a}\"rtl\"===c.documentElement.getAttribute(\"dir\")&&(t=t===n?a:n),t&&(r=t.firstElementChild,i.setAttribute(\"tabindex\",\"-1\"),i.setAttribute(\"aria-selected\",!1),c.querySelector(\"#\"+i.getAttribute(\"aria-controls\")).setAttribute(\"aria-hidden\",\"true\"),r.setAttribute(\"tabindex\",\"0\"),r.setAttribute(\"aria-selected\",\"true\"),r.focus(),c.querySelector(\"#\"+r.getAttribute(\"aria-controls\")).setAttribute(\"aria-hidden\",\"false\"))}}i&&(!function e(){u.self===u.top||r||(r=u.location.hash.replace(/.*secret=([\\d\\w]{10}).*/,\"$1\"),clearTimeout(t),t=setTimeout(function(){e()},100))}(),c.documentElement.className=c.documentElement.className.replace(/\\bno-js\\b/,\"\")+\" js\",c.addEventListener(\"DOMContentLoaded\",n,!1),u.addEventListener(\"load\",n,!1),u.addEventListener(\"resize\",function(){u.self!==u.top&&(clearTimeout(e),e=setTimeout(function(){f(\"height\",Math.ceil(c.body.getBoundingClientRect().height))},100))},!1))}(window,document);\n       ")
    # end if
    php_print(" </script>\n ")
# end def print_embed_scripts
#// 
#// Prepare the oembed HTML to be displayed in an RSS feed.
#// 
#// @since 4.4.0
#// @access private
#// 
#// @param string $content The content to filter.
#// @return string The filtered content.
#//
def _oembed_filter_feed_content(content=None, *args_):
    
    return php_str_replace("<iframe class=\"wp-embedded-content\" sandbox=\"allow-scripts\" security=\"restricted\" style=\"position: absolute; clip: rect(1px, 1px, 1px, 1px);\"", "<iframe class=\"wp-embedded-content\" sandbox=\"allow-scripts\" security=\"restricted\"", content)
# end def _oembed_filter_feed_content
#// 
#// Prints the necessary markup for the embed comments button.
#// 
#// @since 4.4.0
#//
def print_embed_comments_button(*args_):
    
    if is_404() or (not get_comments_number() or comments_open()):
        return
    # end if
    php_print(" <div class=\"wp-embed-comments\">\n     <a href=\"")
    comments_link()
    php_print("\" target=\"_top\">\n            <span class=\"dashicons dashicons-admin-comments\"></span>\n            ")
    printf(_n("%s <span class=\"screen-reader-text\">Comment</span>", "%s <span class=\"screen-reader-text\">Comments</span>", get_comments_number()), number_format_i18n(get_comments_number()))
    php_print("     </a>\n  </div>\n    ")
# end def print_embed_comments_button
#// 
#// Prints the necessary markup for the embed sharing button.
#// 
#// @since 4.4.0
#//
def print_embed_sharing_button(*args_):
    
    if is_404():
        return
    # end if
    php_print(" <div class=\"wp-embed-share\">\n        <button type=\"button\" class=\"wp-embed-share-dialog-open\" aria-label=\"")
    esc_attr_e("Open sharing dialog")
    php_print("""\">
    <span class=\"dashicons dashicons-share\"></span>
    </button>
    </div>
    """)
# end def print_embed_sharing_button
#// 
#// Prints the necessary markup for the embed sharing dialog.
#// 
#// @since 4.4.0
#//
def print_embed_sharing_dialog(*args_):
    
    if is_404():
        return
    # end if
    php_print(" <div class=\"wp-embed-share-dialog hidden\" role=\"dialog\" aria-label=\"")
    esc_attr_e("Sharing options")
    php_print("""\">
    <div class=\"wp-embed-share-dialog-content\">
    <div class=\"wp-embed-share-dialog-text\">
    <ul class=\"wp-embed-share-tabs\" role=\"tablist\">
    <li class=\"wp-embed-share-tab-button wp-embed-share-tab-button-wordpress\" role=\"presentation\">
    <button type=\"button\" role=\"tab\" aria-controls=\"wp-embed-share-tab-wordpress\" aria-selected=\"true\" tabindex=\"0\">""")
    esc_html_e("WordPress Embed")
    php_print("""</button>
    </li>
    <li class=\"wp-embed-share-tab-button wp-embed-share-tab-button-html\" role=\"presentation\">
    <button type=\"button\" role=\"tab\" aria-controls=\"wp-embed-share-tab-html\" aria-selected=\"false\" tabindex=\"-1\">""")
    esc_html_e("HTML Embed")
    php_print("""</button>
    </li>
    </ul>
    <div id=\"wp-embed-share-tab-wordpress\" class=\"wp-embed-share-tab\" role=\"tabpanel\" aria-hidden=\"false\">
    <input type=\"text\" value=\"""")
    the_permalink()
    php_print("""\" class=\"wp-embed-share-input\" aria-describedby=\"wp-embed-share-description-wordpress\" tabindex=\"0\" readonly/>
    <p class=\"wp-embed-share-description\" id=\"wp-embed-share-description-wordpress\">
    """)
    _e("Copy and paste this URL into your WordPress site to embed")
    php_print("""                   </p>
    </div>
    <div id=\"wp-embed-share-tab-html\" class=\"wp-embed-share-tab\" role=\"tabpanel\" aria-hidden=\"true\">
    <textarea class=\"wp-embed-share-input\" aria-describedby=\"wp-embed-share-description-html\" tabindex=\"0\" readonly>""")
    php_print(esc_textarea(get_post_embed_html(600, 400)))
    php_print("""</textarea>
    <p class=\"wp-embed-share-description\" id=\"wp-embed-share-description-html\">
    """)
    _e("Copy and paste this code into your site to embed")
    php_print("""                   </p>
    </div>
    </div>
    <button type=\"button\" class=\"wp-embed-share-dialog-close\" aria-label=\"""")
    esc_attr_e("Close sharing dialog")
    php_print("""\">
    <span class=\"dashicons dashicons-no\"></span>
    </button>
    </div>
    </div>
    """)
# end def print_embed_sharing_dialog
#// 
#// Prints the necessary markup for the site title in an embed template.
#// 
#// @since 4.5.0
#//
def the_embed_site_title(*args_):
    
    site_title = php_sprintf("<a href=\"%s\" target=\"_top\"><img src=\"%s\" srcset=\"%s 2x\" width=\"32\" height=\"32\" alt=\"\" class=\"wp-embed-site-icon\"/><span>%s</span></a>", esc_url(home_url()), esc_url(get_site_icon_url(32, admin_url("images/w-logo-blue.png"))), esc_url(get_site_icon_url(64, admin_url("images/w-logo-blue.png"))), esc_html(get_bloginfo("name")))
    site_title = "<div class=\"wp-embed-site-title\">" + site_title + "</div>"
    #// 
    #// Filters the site title HTML in the embed footer.
    #// 
    #// @since 4.4.0
    #// 
    #// @param string $site_title The site title HTML.
    #//
    php_print(apply_filters("embed_site_title_html", site_title))
# end def the_embed_site_title
#// 
#// Filters the oEmbed result before any HTTP requests are made.
#// 
#// If the URL belongs to the current site, the result is fetched directly instead of
#// going through the oEmbed discovery process.
#// 
#// @since 4.5.3
#// 
#// @param null|string $result The UNSANITIZED (and potentially unsafe) HTML that should be used to embed. Default null.
#// @param string      $url    The URL that should be inspected for discovery `<link>` tags.
#// @param array       $args   oEmbed remote get arguments.
#// @return null|string The UNSANITIZED (and potentially unsafe) HTML that should be used to embed.
#// Null if the URL does not belong to the current site.
#//
def wp_filter_pre_oembed_result(result=None, url=None, args=None, *args_):
    
    data = get_oembed_response_data_for_url(url, args)
    if data:
        return _wp_oembed_get_object().data2html(data, url)
    # end if
    return result
# end def wp_filter_pre_oembed_result
