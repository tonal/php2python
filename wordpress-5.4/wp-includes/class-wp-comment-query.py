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
#// Comment API: WP_Comment_Query class
#// 
#// @package WordPress
#// @subpackage Comments
#// @since 4.4.0
#// 
#// 
#// Core class used for querying comments.
#// 
#// @since 3.1.0
#// 
#// @see WP_Comment_Query::__construct() for accepted arguments.
#//
class WP_Comment_Query():
    request = Array()
    meta_query = False
    meta_query_clauses = Array()
    sql_clauses = Array({"select": "", "from": "", "where": Array(), "groupby": "", "orderby": "", "limits": ""})
    filtered_where_clause = Array()
    date_query = False
    query_vars = Array()
    query_var_defaults = Array()
    comments = Array()
    found_comments = 0
    max_num_pages = 0
    #// 
    #// Make private/protected methods readable for backward compatibility.
    #// 
    #// @since 4.0.0
    #// 
    #// @param string   $name      Method to call.
    #// @param array    $arguments Arguments to pass when calling.
    #// @return mixed|false Return value of the callback, false otherwise.
    #//
    def __call(self, name=None, arguments=None):
        
        if "get_search_sql" == name:
            return self.get_search_sql(arguments)
        # end if
        return False
    # end def __call
    #// 
    #// Constructor.
    #// 
    #// Sets up the comment query, based on the query vars passed.
    #// 
    #// @since 4.2.0
    #// @since 4.4.0 `$parent__in` and `$parent__not_in` were added.
    #// @since 4.4.0 Order by `comment__in` was added. `$update_comment_meta_cache`, `$no_found_rows`,
    #// `$hierarchical`, and `$update_comment_post_cache` were added.
    #// @since 4.5.0 Introduced the `$author_url` argument.
    #// @since 4.6.0 Introduced the `$cache_domain` argument.
    #// @since 4.9.0 Introduced the `$paged` argument.
    #// 
    #// @param string|array $query {
    #// Optional. Array or query string of comment query parameters. Default empty.
    #// 
    #// @type string       $author_email              Comment author email address. Default empty.
    #// @type string       $author_url                Comment author URL. Default empty.
    #// @type array        $author__in                Array of author IDs to include comments for. Default empty.
    #// @type array        $author__not_in            Array of author IDs to exclude comments for. Default empty.
    #// @type array        $comment__in               Array of comment IDs to include. Default empty.
    #// @type array        $comment__not_in           Array of comment IDs to exclude. Default empty.
    #// @type bool         $count                     Whether to return a comment count (true) or array of
    #// comment objects (false). Default false.
    #// @type array        $date_query                Date query clauses to limit comments by. See WP_Date_Query.
    #// Default null.
    #// @type string       $fields                    Comment fields to return. Accepts 'ids' for comment IDs
    #// only or empty for all fields. Default empty.
    #// @type int          $ID                        Currently unused.
    #// @type array        $include_unapproved        Array of IDs or email addresses of users whose unapproved
    #// comments will be returned by the query regardless of
    #// `$status`. Default empty.
    #// @type int          $karma                     Karma score to retrieve matching comments for.
    #// Default empty.
    #// @type string       $meta_key                  Include comments with a matching comment meta key.
    #// Default empty.
    #// @type string       $meta_value                Include comments with a matching comment meta value.
    #// Requires `$meta_key` to be set. Default empty.
    #// @type array        $meta_query                Meta query clauses to limit retrieved comments by.
    #// See WP_Meta_Query. Default empty.
    #// @type int          $number                    Maximum number of comments to retrieve.
    #// Default empty (no limit).
    #// @type int          $paged                     When used with $number, defines the page of results to return.
    #// When used with $offset, $offset takes precedence. Default 1.
    #// @type int          $offset                    Number of comments to offset the query. Used to build
    #// LIMIT clause. Default 0.
    #// @type bool         $no_found_rows             Whether to disable the `SQL_CALC_FOUND_ROWS` query.
    #// Default: true.
    #// @type string|array $orderby                   Comment status or array of statuses. To use 'meta_value'
    #// or 'meta_value_num', `$meta_key` must also be defined.
    #// To sort by a specific `$meta_query` clause, use that
    #// clause's array key. Accepts 'comment_agent',
    #// 'comment_approved', 'comment_author',
    #// 'comment_author_email', 'comment_author_IP',
    #// 'comment_author_url', 'comment_content', 'comment_date',
    #// 'comment_date_gmt', 'comment_ID', 'comment_karma',
    #// 'comment_parent', 'comment_post_ID', 'comment_type',
    #// 'user_id', 'comment__in', 'meta_value', 'meta_value_num',
    #// the value of $meta_key, and the array keys of
    #// `$meta_query`. Also accepts false, an empty array, or
    #// 'none' to disable `ORDER BY` clause.
    #// Default: 'comment_date_gmt'.
    #// @type string       $order                     How to order retrieved comments. Accepts 'ASC', 'DESC'.
    #// Default: 'DESC'.
    #// @type int          $parent                    Parent ID of comment to retrieve children of.
    #// Default empty.
    #// @type array        $parent__in                Array of parent IDs of comments to retrieve children for.
    #// Default empty.
    #// @type array        $parent__not_in            Array of parent IDs of comments *not* to retrieve
    #// children for. Default empty.
    #// @type array        $post_author__in           Array of author IDs to retrieve comments for.
    #// Default empty.
    #// @type array        $post_author__not_in       Array of author IDs *not* to retrieve comments for.
    #// Default empty.
    #// @type int          $post_ID                   Currently unused.
    #// @type int          $post_id                   Limit results to those affiliated with a given post ID.
    #// Default 0.
    #// @type array        $post__in                  Array of post IDs to include affiliated comments for.
    #// Default empty.
    #// @type array        $post__not_in              Array of post IDs to exclude affiliated comments for.
    #// Default empty.
    #// @type int          $post_author               Post author ID to limit results by. Default empty.
    #// @type string|array $post_status               Post status or array of post statuses to retrieve
    #// affiliated comments for. Pass 'any' to match any value.
    #// Default empty.
    #// @type string       $post_type                 Post type or array of post types to retrieve affiliated
    #// comments for. Pass 'any' to match any value. Default empty.
    #// @type string       $post_name                 Post name to retrieve affiliated comments for.
    #// Default empty.
    #// @type int          $post_parent               Post parent ID to retrieve affiliated comments for.
    #// Default empty.
    #// @type string       $search                    Search term(s) to retrieve matching comments for.
    #// Default empty.
    #// @type string|array $status                    Comment stati to limit results by. Accepts an array
    #// or space/comma-separated list of 'hold' (`comment_status=0`),
    #// 'approve' (`comment_status=1`), 'all', or a custom
    #// comment status. Default 'all'.
    #// @type string|array $type                      Include comments of a given type, or array of types.
    #// Accepts 'comment', 'pings' (includes 'pingback' and
    #// 'trackback'), or anycustom type string. Default empty.
    #// @type array        $type__in                  Include comments from a given array of comment types.
    #// Default empty.
    #// @type array        $type__not_in              Exclude comments from a given array of comment types.
    #// Default empty.
    #// @type int          $user_id                   Include comments for a specific user ID. Default empty.
    #// @type bool|string  $hierarchical              Whether to include comment descendants in the results.
    #// 'threaded' returns a tree, with each comment's children
    #// stored in a `children` property on the `WP_Comment`
    #// object. 'flat' returns a flat array of found comments plus
    #// their children. Pass `false` to leave out descendants.
    #// The parameter is ignored (forced to `false`) when
    #// `$fields` is 'ids' or 'counts'. Accepts 'threaded',
    #// 'flat', or false. Default: false.
    #// @type string       $cache_domain              Unique cache key to be produced when this query is stored in
    #// an object cache. Default is 'core'.
    #// @type bool         $update_comment_meta_cache Whether to prime the metadata cache for found comments.
    #// Default true.
    #// @type bool         $update_comment_post_cache Whether to prime the cache for comment posts.
    #// Default false.
    #// }
    #//
    def __init__(self, query=""):
        
        self.query_var_defaults = Array({"author_email": "", "author_url": "", "author__in": "", "author__not_in": "", "include_unapproved": "", "fields": "", "ID": "", "comment__in": "", "comment__not_in": "", "karma": "", "number": "", "offset": "", "no_found_rows": True, "orderby": "", "order": "DESC", "paged": 1, "parent": "", "parent__in": "", "parent__not_in": "", "post_author__in": "", "post_author__not_in": "", "post_ID": "", "post_id": 0, "post__in": "", "post__not_in": "", "post_author": "", "post_name": "", "post_parent": "", "post_status": "", "post_type": "", "status": "all", "type": "", "type__in": "", "type__not_in": "", "user_id": "", "search": "", "count": False, "meta_key": "", "meta_value": "", "meta_query": "", "date_query": None, "hierarchical": False, "cache_domain": "core", "update_comment_meta_cache": True, "update_comment_post_cache": False})
        if (not php_empty(lambda : query)):
            self.query(query)
        # end if
    # end def __init__
    #// 
    #// Parse arguments passed to the comment query with default query parameters.
    #// 
    #// @since 4.2.0 Extracted from WP_Comment_Query::query().
    #// 
    #// @param string|array $query WP_Comment_Query arguments. See WP_Comment_Query::__construct()
    #//
    def parse_query(self, query=""):
        
        if php_empty(lambda : query):
            query = self.query_vars
        # end if
        self.query_vars = wp_parse_args(query, self.query_var_defaults)
        #// 
        #// Fires after the comment query vars have been parsed.
        #// 
        #// @since 4.2.0
        #// 
        #// @param WP_Comment_Query $this The WP_Comment_Query instance (passed by reference).
        #//
        do_action_ref_array("parse_comment_query", Array(self))
    # end def parse_query
    #// 
    #// Sets up the WordPress query for retrieving comments.
    #// 
    #// @since 3.1.0
    #// @since 4.1.0 Introduced 'comment__in', 'comment__not_in', 'post_author__in',
    #// 'post_author__not_in', 'author__in', 'author__not_in', 'post__in',
    #// 'post__not_in', 'include_unapproved', 'type__in', and 'type__not_in'
    #// arguments to $query_vars.
    #// @since 4.2.0 Moved parsing to WP_Comment_Query::parse_query().
    #// 
    #// @param string|array $query Array or URL query string of parameters.
    #// @return array|int List of comments, or number of comments when 'count' is passed as a query var.
    #//
    def query(self, query=None):
        
        self.query_vars = wp_parse_args(query)
        return self.get_comments()
    # end def query
    #// 
    #// Get a list of comments matching the query vars.
    #// 
    #// @since 4.2.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #// 
    #// @return int|array List of comments or number of found comments if `$count` argument is true.
    #//
    def get_comments(self):
        
        global wpdb
        php_check_if_defined("wpdb")
        self.parse_query()
        #// Parse meta query.
        self.meta_query = php_new_class("WP_Meta_Query", lambda : WP_Meta_Query())
        self.meta_query.parse_query_vars(self.query_vars)
        #// 
        #// Fires before comments are retrieved.
        #// 
        #// @since 3.1.0
        #// 
        #// @param WP_Comment_Query $this Current instance of WP_Comment_Query (passed by reference).
        #//
        do_action_ref_array("pre_get_comments", Array(self))
        #// Reparse query vars, in case they were modified in a 'pre_get_comments' callback.
        self.meta_query.parse_query_vars(self.query_vars)
        if (not php_empty(lambda : self.meta_query.queries)):
            self.meta_query_clauses = self.meta_query.get_sql("comment", wpdb.comments, "comment_ID", self)
        # end if
        comment_data = None
        #// 
        #// Filter the comments data before the query takes place.
        #// 
        #// Return a non-null value to bypass WordPress's default comment queries.
        #// 
        #// The expected return type from this filter depends on the value passed in the request query_vars.
        #// When `$this->query_vars['count']` is set, the filter should return the comment count as an int.
        #// When `'ids' == $this->query_vars['fields']`, the filter should return an array of comment ids.
        #// Otherwise the filter should return an array of WP_Comment objects.
        #// 
        #// @since 5.3.0
        #// 
        #// @param array|int|null   $comment_data Return an array of comment data to short-circuit WP's comment query,
        #// the comment count as an integer if `$this->query_vars['count']` is set,
        #// or null to allow WP to run its normal queries.
        #// @param WP_Comment_Query $this         The WP_Comment_Query instance, passed by reference.
        #//
        comment_data = apply_filters_ref_array("comments_pre_query", Array(comment_data, self))
        if None != comment_data:
            return comment_data
        # end if
        #// 
        #// Only use the args defined in the query_var_defaults to compute the key,
        #// but ignore 'fields', which does not affect query results.
        #//
        _args = wp_array_slice_assoc(self.query_vars, php_array_keys(self.query_var_defaults))
        _args["fields"] = None
        key = php_md5(serialize(_args))
        last_changed = wp_cache_get_last_changed("comment")
        cache_key = str("get_comments:") + str(key) + str(":") + str(last_changed)
        cache_value = wp_cache_get(cache_key, "comment")
        if False == cache_value:
            comment_ids = self.get_comment_ids()
            if comment_ids:
                self.set_found_comments()
            # end if
            cache_value = Array({"comment_ids": comment_ids, "found_comments": self.found_comments})
            wp_cache_add(cache_key, cache_value, "comment")
        else:
            comment_ids = cache_value["comment_ids"]
            self.found_comments = cache_value["found_comments"]
        # end if
        if self.found_comments and self.query_vars["number"]:
            self.max_num_pages = ceil(self.found_comments / self.query_vars["number"])
        # end if
        #// If querying for a count only, there's nothing more to do.
        if self.query_vars["count"]:
            #// $comment_ids is actually a count in this case.
            return php_intval(comment_ids)
        # end if
        comment_ids = php_array_map("intval", comment_ids)
        if "ids" == self.query_vars["fields"]:
            self.comments = comment_ids
            return self.comments
        # end if
        _prime_comment_caches(comment_ids, self.query_vars["update_comment_meta_cache"])
        #// Fetch full comment objects from the primed cache.
        _comments = Array()
        for comment_id in comment_ids:
            _comment = get_comment(comment_id)
            if _comment:
                _comments[-1] = _comment
            # end if
        # end for
        #// Prime comment post caches.
        if self.query_vars["update_comment_post_cache"]:
            comment_post_ids = Array()
            for _comment in _comments:
                comment_post_ids[-1] = _comment.comment_post_ID
            # end for
            _prime_post_caches(comment_post_ids, False, False)
        # end if
        #// 
        #// Filters the comment query results.
        #// 
        #// @since 3.1.0
        #// 
        #// @param WP_Comment[]     $_comments An array of comments.
        #// @param WP_Comment_Query $this      Current instance of WP_Comment_Query (passed by reference).
        #//
        _comments = apply_filters_ref_array("the_comments", Array(_comments, self))
        #// Convert to WP_Comment instances.
        comments = php_array_map("get_comment", _comments)
        if self.query_vars["hierarchical"]:
            comments = self.fill_descendants(comments)
        # end if
        self.comments = comments
        return self.comments
    # end def get_comments
    #// 
    #// Used internally to get a list of comment IDs matching the query vars.
    #// 
    #// @since 4.4.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #// 
    #// @return int|array A single count of comment IDs if a count query. An array of comment IDs if a full query.
    #//
    def get_comment_ids(self):
        
        global wpdb
        php_check_if_defined("wpdb")
        #// Assemble clauses related to 'comment_approved'.
        approved_clauses = Array()
        #// 'status' accepts an array or a comma-separated string.
        status_clauses = Array()
        statuses = wp_parse_list(self.query_vars["status"])
        #// Empty 'status' should be interpreted as 'all'.
        if php_empty(lambda : statuses):
            statuses = Array("all")
        # end if
        #// 'any' overrides other statuses.
        if (not php_in_array("any", statuses)):
            for status in statuses:
                for case in Switch(status):
                    if case("hold"):
                        status_clauses[-1] = "comment_approved = '0'"
                        break
                    # end if
                    if case("approve"):
                        status_clauses[-1] = "comment_approved = '1'"
                        break
                    # end if
                    if case("all"):
                        pass
                    # end if
                    if case(""):
                        status_clauses[-1] = "( comment_approved = '0' OR comment_approved = '1' )"
                        break
                    # end if
                    if case():
                        status_clauses[-1] = wpdb.prepare("comment_approved = %s", status)
                        break
                    # end if
                # end for
            # end for
            if (not php_empty(lambda : status_clauses)):
                approved_clauses[-1] = "( " + php_implode(" OR ", status_clauses) + " )"
            # end if
        # end if
        #// User IDs or emails whose unapproved comments are included, regardless of $status.
        if (not php_empty(lambda : self.query_vars["include_unapproved"])):
            include_unapproved = wp_parse_list(self.query_vars["include_unapproved"])
            unapproved_ids = Array()
            unapproved_emails = Array()
            for unapproved_identifier in include_unapproved:
                #// Numeric values are assumed to be user ids.
                if php_is_numeric(unapproved_identifier):
                    approved_clauses[-1] = wpdb.prepare("( user_id = %d AND comment_approved = '0' )", unapproved_identifier)
                    pass
                else:
                    approved_clauses[-1] = wpdb.prepare("( comment_author_email = %s AND comment_approved = '0' )", unapproved_identifier)
                # end if
            # end for
        # end if
        #// Collapse comment_approved clauses into a single OR-separated clause.
        if (not php_empty(lambda : approved_clauses)):
            if 1 == php_count(approved_clauses):
                self.sql_clauses["where"]["approved"] = approved_clauses[0]
            else:
                self.sql_clauses["where"]["approved"] = "( " + php_implode(" OR ", approved_clauses) + " )"
            # end if
        # end if
        order = "ASC" if "ASC" == php_strtoupper(self.query_vars["order"]) else "DESC"
        #// Disable ORDER BY with 'none', an empty array, or boolean false.
        if php_in_array(self.query_vars["orderby"], Array("none", Array(), False), True):
            orderby = ""
        elif (not php_empty(lambda : self.query_vars["orderby"])):
            ordersby = self.query_vars["orderby"] if php_is_array(self.query_vars["orderby"]) else php_preg_split("/[,\\s]/", self.query_vars["orderby"])
            orderby_array = Array()
            found_orderby_comment_id = False
            for _key,_value in ordersby:
                if (not _value):
                    continue
                # end if
                if php_is_int(_key):
                    _orderby = _value
                    _order = order
                else:
                    _orderby = _key
                    _order = _value
                # end if
                if (not found_orderby_comment_id) and php_in_array(_orderby, Array("comment_ID", "comment__in")):
                    found_orderby_comment_id = True
                # end if
                parsed = self.parse_orderby(_orderby)
                if (not parsed):
                    continue
                # end if
                if "comment__in" == _orderby:
                    orderby_array[-1] = parsed
                    continue
                # end if
                orderby_array[-1] = parsed + " " + self.parse_order(_order)
            # end for
            #// If no valid clauses were found, order by comment_date_gmt.
            if php_empty(lambda : orderby_array):
                orderby_array[-1] = str(wpdb.comments) + str(".comment_date_gmt ") + str(order)
            # end if
            #// To ensure determinate sorting, always include a comment_ID clause.
            if (not found_orderby_comment_id):
                comment_id_order = ""
                #// Inherit order from comment_date or comment_date_gmt, if available.
                for orderby_clause in orderby_array:
                    if php_preg_match("/comment_date(?:_gmt)*\\ (ASC|DESC)/", orderby_clause, match):
                        comment_id_order = match[1]
                        break
                    # end if
                # end for
                #// If no date-related order is available, use the date from the first available clause.
                if (not comment_id_order):
                    for orderby_clause in orderby_array:
                        if False != php_strpos("ASC", orderby_clause):
                            comment_id_order = "ASC"
                        else:
                            comment_id_order = "DESC"
                        # end if
                        break
                    # end for
                # end if
                #// Default to DESC.
                if (not comment_id_order):
                    comment_id_order = "DESC"
                # end if
                orderby_array[-1] = str(wpdb.comments) + str(".comment_ID ") + str(comment_id_order)
            # end if
            orderby = php_implode(", ", orderby_array)
        else:
            orderby = str(wpdb.comments) + str(".comment_date_gmt ") + str(order)
        # end if
        number = absint(self.query_vars["number"])
        offset = absint(self.query_vars["offset"])
        paged = absint(self.query_vars["paged"])
        limits = ""
        if (not php_empty(lambda : number)):
            if offset:
                limits = "LIMIT " + offset + "," + number
            else:
                limits = "LIMIT " + number * paged - 1 + "," + number
            # end if
        # end if
        if self.query_vars["count"]:
            fields = "COUNT(*)"
        else:
            fields = str(wpdb.comments) + str(".comment_ID")
        # end if
        post_id = absint(self.query_vars["post_id"])
        if (not php_empty(lambda : post_id)):
            self.sql_clauses["where"]["post_id"] = wpdb.prepare("comment_post_ID = %d", post_id)
        # end if
        #// Parse comment IDs for an IN clause.
        if (not php_empty(lambda : self.query_vars["comment__in"])):
            self.sql_clauses["where"]["comment__in"] = str(wpdb.comments) + str(".comment_ID IN ( ") + php_implode(",", wp_parse_id_list(self.query_vars["comment__in"])) + " )"
        # end if
        #// Parse comment IDs for a NOT IN clause.
        if (not php_empty(lambda : self.query_vars["comment__not_in"])):
            self.sql_clauses["where"]["comment__not_in"] = str(wpdb.comments) + str(".comment_ID NOT IN ( ") + php_implode(",", wp_parse_id_list(self.query_vars["comment__not_in"])) + " )"
        # end if
        #// Parse comment parent IDs for an IN clause.
        if (not php_empty(lambda : self.query_vars["parent__in"])):
            self.sql_clauses["where"]["parent__in"] = "comment_parent IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["parent__in"])) + " )"
        # end if
        #// Parse comment parent IDs for a NOT IN clause.
        if (not php_empty(lambda : self.query_vars["parent__not_in"])):
            self.sql_clauses["where"]["parent__not_in"] = "comment_parent NOT IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["parent__not_in"])) + " )"
        # end if
        #// Parse comment post IDs for an IN clause.
        if (not php_empty(lambda : self.query_vars["post__in"])):
            self.sql_clauses["where"]["post__in"] = "comment_post_ID IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["post__in"])) + " )"
        # end if
        #// Parse comment post IDs for a NOT IN clause.
        if (not php_empty(lambda : self.query_vars["post__not_in"])):
            self.sql_clauses["where"]["post__not_in"] = "comment_post_ID NOT IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["post__not_in"])) + " )"
        # end if
        if "" != self.query_vars["author_email"]:
            self.sql_clauses["where"]["author_email"] = wpdb.prepare("comment_author_email = %s", self.query_vars["author_email"])
        # end if
        if "" != self.query_vars["author_url"]:
            self.sql_clauses["where"]["author_url"] = wpdb.prepare("comment_author_url = %s", self.query_vars["author_url"])
        # end if
        if "" != self.query_vars["karma"]:
            self.sql_clauses["where"]["karma"] = wpdb.prepare("comment_karma = %d", self.query_vars["karma"])
        # end if
        #// Filtering by comment_type: 'type', 'type__in', 'type__not_in'.
        raw_types = Array({"IN": php_array_merge(self.query_vars["type"], self.query_vars["type__in"]), "NOT IN": self.query_vars["type__not_in"]})
        comment_types = Array()
        for operator,_raw_types in raw_types:
            _raw_types = array_unique(_raw_types)
            for type in _raw_types:
                for case in Switch(type):
                    if case(""):
                        pass
                    # end if
                    if case("all"):
                        break
                    # end if
                    if case("comment"):
                        pass
                    # end if
                    if case("comments"):
                        comment_types[operator][-1] = "''"
                        break
                    # end if
                    if case("pings"):
                        comment_types[operator][-1] = "'pingback'"
                        comment_types[operator][-1] = "'trackback'"
                        break
                    # end if
                    if case():
                        comment_types[operator][-1] = wpdb.prepare("%s", type)
                        break
                    # end if
                # end for
            # end for
            if (not php_empty(lambda : comment_types[operator])):
                types_sql = php_implode(", ", comment_types[operator])
                self.sql_clauses["where"]["comment_type__" + php_strtolower(php_str_replace(" ", "_", operator))] = str("comment_type ") + str(operator) + str(" (") + str(types_sql) + str(")")
            # end if
        # end for
        parent = self.query_vars["parent"]
        if self.query_vars["hierarchical"] and (not parent):
            parent = 0
        # end if
        if "" != parent:
            self.sql_clauses["where"]["parent"] = wpdb.prepare("comment_parent = %d", parent)
        # end if
        if php_is_array(self.query_vars["user_id"]):
            self.sql_clauses["where"]["user_id"] = "user_id IN (" + php_implode(",", php_array_map("absint", self.query_vars["user_id"])) + ")"
        elif "" != self.query_vars["user_id"]:
            self.sql_clauses["where"]["user_id"] = wpdb.prepare("user_id = %d", self.query_vars["user_id"])
        # end if
        #// Falsy search strings are ignored.
        if php_strlen(self.query_vars["search"]):
            search_sql = self.get_search_sql(self.query_vars["search"], Array("comment_author", "comment_author_email", "comment_author_url", "comment_author_IP", "comment_content"))
            #// Strip leading 'AND'.
            self.sql_clauses["where"]["search"] = php_preg_replace("/^\\s*AND\\s*/", "", search_sql)
        # end if
        #// If any post-related query vars are passed, join the posts table.
        join_posts_table = False
        plucked = wp_array_slice_assoc(self.query_vars, Array("post_author", "post_name", "post_parent"))
        post_fields = php_array_filter(plucked)
        if (not php_empty(lambda : post_fields)):
            join_posts_table = True
            for field_name,field_value in post_fields:
                #// $field_value may be an array.
                esses = array_fill(0, php_count(field_value), "%s")
                #// phpcs:ignore WordPress.DB.PreparedSQLPlaceholders.UnfinishedPrepare
                self.sql_clauses["where"][field_name] = wpdb.prepare(str(" ") + str(wpdb.posts) + str(".") + str(field_name) + str(" IN (") + php_implode(",", esses) + ")", field_value)
            # end for
        # end if
        #// 'post_status' and 'post_type' are handled separately, due to the specialized behavior of 'any'.
        for field_name in Array("post_status", "post_type"):
            q_values = Array()
            if (not php_empty(lambda : self.query_vars[field_name])):
                q_values = self.query_vars[field_name]
                if (not php_is_array(q_values)):
                    q_values = php_explode(",", q_values)
                # end if
                #// 'any' will cause the query var to be ignored.
                if php_in_array("any", q_values, True) or php_empty(lambda : q_values):
                    continue
                # end if
                join_posts_table = True
                esses = array_fill(0, php_count(q_values), "%s")
                #// phpcs:ignore WordPress.DB.PreparedSQLPlaceholders.UnfinishedPrepare
                self.sql_clauses["where"][field_name] = wpdb.prepare(str(" ") + str(wpdb.posts) + str(".") + str(field_name) + str(" IN (") + php_implode(",", esses) + ")", q_values)
            # end if
        # end for
        #// Comment author IDs for an IN clause.
        if (not php_empty(lambda : self.query_vars["author__in"])):
            self.sql_clauses["where"]["author__in"] = "user_id IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["author__in"])) + " )"
        # end if
        #// Comment author IDs for a NOT IN clause.
        if (not php_empty(lambda : self.query_vars["author__not_in"])):
            self.sql_clauses["where"]["author__not_in"] = "user_id NOT IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["author__not_in"])) + " )"
        # end if
        #// Post author IDs for an IN clause.
        if (not php_empty(lambda : self.query_vars["post_author__in"])):
            join_posts_table = True
            self.sql_clauses["where"]["post_author__in"] = "post_author IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["post_author__in"])) + " )"
        # end if
        #// Post author IDs for a NOT IN clause.
        if (not php_empty(lambda : self.query_vars["post_author__not_in"])):
            join_posts_table = True
            self.sql_clauses["where"]["post_author__not_in"] = "post_author NOT IN ( " + php_implode(",", wp_parse_id_list(self.query_vars["post_author__not_in"])) + " )"
        # end if
        join = ""
        groupby = ""
        if join_posts_table:
            join += str("JOIN ") + str(wpdb.posts) + str(" ON ") + str(wpdb.posts) + str(".ID = ") + str(wpdb.comments) + str(".comment_post_ID")
        # end if
        if (not php_empty(lambda : self.meta_query_clauses)):
            join += self.meta_query_clauses["join"]
            #// Strip leading 'AND'.
            self.sql_clauses["where"]["meta_query"] = php_preg_replace("/^\\s*AND\\s*/", "", self.meta_query_clauses["where"])
            if (not self.query_vars["count"]):
                groupby = str(wpdb.comments) + str(".comment_ID")
            # end if
        # end if
        if (not php_empty(lambda : self.query_vars["date_query"])) and php_is_array(self.query_vars["date_query"]):
            self.date_query = php_new_class("WP_Date_Query", lambda : WP_Date_Query(self.query_vars["date_query"], "comment_date"))
            self.sql_clauses["where"]["date_query"] = php_preg_replace("/^\\s*AND\\s*/", "", self.date_query.get_sql())
        # end if
        where = php_implode(" AND ", self.sql_clauses["where"])
        pieces = Array("fields", "join", "where", "orderby", "limits", "groupby")
        #// 
        #// Filters the comment query clauses.
        #// 
        #// @since 3.1.0
        #// 
        #// @param string[]         $pieces An associative array of comment query clauses.
        #// @param WP_Comment_Query $this   Current instance of WP_Comment_Query (passed by reference).
        #//
        clauses = apply_filters_ref_array("comments_clauses", Array(compact(pieces), self))
        fields = clauses["fields"] if (php_isset(lambda : clauses["fields"])) else ""
        join = clauses["join"] if (php_isset(lambda : clauses["join"])) else ""
        where = clauses["where"] if (php_isset(lambda : clauses["where"])) else ""
        orderby = clauses["orderby"] if (php_isset(lambda : clauses["orderby"])) else ""
        limits = clauses["limits"] if (php_isset(lambda : clauses["limits"])) else ""
        groupby = clauses["groupby"] if (php_isset(lambda : clauses["groupby"])) else ""
        self.filtered_where_clause = where
        if where:
            where = "WHERE " + where
        # end if
        if groupby:
            groupby = "GROUP BY " + groupby
        # end if
        if orderby:
            orderby = str("ORDER BY ") + str(orderby)
        # end if
        found_rows = ""
        if (not self.query_vars["no_found_rows"]):
            found_rows = "SQL_CALC_FOUND_ROWS"
        # end if
        self.sql_clauses["select"] = str("SELECT ") + str(found_rows) + str(" ") + str(fields)
        self.sql_clauses["from"] = str("FROM ") + str(wpdb.comments) + str(" ") + str(join)
        self.sql_clauses["groupby"] = groupby
        self.sql_clauses["orderby"] = orderby
        self.sql_clauses["limits"] = limits
        self.request = str(self.sql_clauses["select"]) + str(" ") + str(self.sql_clauses["from"]) + str(" ") + str(where) + str(" ") + str(self.sql_clauses["groupby"]) + str(" ") + str(self.sql_clauses["orderby"]) + str(" ") + str(self.sql_clauses["limits"])
        if self.query_vars["count"]:
            return php_intval(wpdb.get_var(self.request))
        else:
            comment_ids = wpdb.get_col(self.request)
            return php_array_map("intval", comment_ids)
        # end if
    # end def get_comment_ids
    #// 
    #// Populates found_comments and max_num_pages properties for the current
    #// query if the limit clause was used.
    #// 
    #// @since 4.6.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #//
    def set_found_comments(self):
        
        global wpdb
        php_check_if_defined("wpdb")
        if self.query_vars["number"] and (not self.query_vars["no_found_rows"]):
            #// 
            #// Filters the query used to retrieve found comment count.
            #// 
            #// @since 4.4.0
            #// 
            #// @param string           $found_comments_query SQL query. Default 'SELECT FOUND_ROWS()'.
            #// @param WP_Comment_Query $comment_query        The `WP_Comment_Query` instance.
            #//
            found_comments_query = apply_filters("found_comments_query", "SELECT FOUND_ROWS()", self)
            self.found_comments = int(wpdb.get_var(found_comments_query))
        # end if
    # end def set_found_comments
    #// 
    #// Fetch descendants for located comments.
    #// 
    #// Instead of calling `get_children()` separately on each child comment, we do a single set of queries to fetch
    #// the descendant trees for all matched top-level comments.
    #// 
    #// @since 4.4.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #// 
    #// @param WP_Comment[] $comments Array of top-level comments whose descendants should be filled in.
    #// @return array
    #//
    def fill_descendants(self, comments=None):
        
        global wpdb
        php_check_if_defined("wpdb")
        levels = Array({0: wp_list_pluck(comments, "comment_ID")})
        key = php_md5(serialize(wp_array_slice_assoc(self.query_vars, php_array_keys(self.query_var_defaults))))
        last_changed = wp_cache_get_last_changed("comment")
        #// Fetch an entire level of the descendant tree at a time.
        level = 0
        exclude_keys = Array("parent", "parent__in", "parent__not_in")
        while True:
            #// Parent-child relationships may be cached. Only query for those that are not.
            child_ids = Array()
            uncached_parent_ids = Array()
            _parent_ids = levels[level]
            for parent_id in _parent_ids:
                cache_key = str("get_comment_child_ids:") + str(parent_id) + str(":") + str(key) + str(":") + str(last_changed)
                parent_child_ids = wp_cache_get(cache_key, "comment")
                if False != parent_child_ids:
                    child_ids = php_array_merge(child_ids, parent_child_ids)
                else:
                    uncached_parent_ids[-1] = parent_id
                # end if
            # end for
            if uncached_parent_ids:
                #// Fetch this level of comments.
                parent_query_args = self.query_vars
                for exclude_key in exclude_keys:
                    parent_query_args[exclude_key] = ""
                # end for
                parent_query_args["parent__in"] = uncached_parent_ids
                parent_query_args["no_found_rows"] = True
                parent_query_args["hierarchical"] = False
                parent_query_args["offset"] = 0
                parent_query_args["number"] = 0
                level_comments = get_comments(parent_query_args)
                #// Cache parent-child relationships.
                parent_map = php_array_fill_keys(uncached_parent_ids, Array())
                for level_comment in level_comments:
                    parent_map[level_comment.comment_parent][-1] = level_comment.comment_ID
                    child_ids[-1] = level_comment.comment_ID
                # end for
                for parent_id,children in parent_map:
                    cache_key = str("get_comment_child_ids:") + str(parent_id) + str(":") + str(key) + str(":") + str(last_changed)
                    wp_cache_set(cache_key, children, "comment")
                # end for
            # end if
            level += 1
            levels[level] = child_ids
            
            if child_ids:
                break
            # end if
        # end while
        #// Prime comment caches for non-top-level comments.
        descendant_ids = Array()
        i = 1
        c = php_count(levels)
        while i < c:
            
            descendant_ids = php_array_merge(descendant_ids, levels[i])
            i += 1
        # end while
        _prime_comment_caches(descendant_ids, self.query_vars["update_comment_meta_cache"])
        #// Assemble a flat array of all comments + descendants.
        all_comments = comments
        for descendant_id in descendant_ids:
            all_comments[-1] = get_comment(descendant_id)
        # end for
        #// If a threaded representation was requested, build the tree.
        if "threaded" == self.query_vars["hierarchical"]:
            threaded_comments = Array()
            ref = Array()
            for k,c in all_comments:
                _c = get_comment(c.comment_ID)
                #// If the comment isn't in the reference array, it goes in the top level of the thread.
                if (not (php_isset(lambda : ref[c.comment_parent]))):
                    threaded_comments[_c.comment_ID] = _c
                    ref[_c.comment_ID] = threaded_comments[_c.comment_ID]
                    pass
                else:
                    ref[_c.comment_parent].add_child(_c)
                    ref[_c.comment_ID] = ref[_c.comment_parent].get_child(_c.comment_ID)
                # end if
            # end for
            #// Set the 'populated_children' flag, to ensure additional database queries aren't run.
            for _ref in ref:
                _ref.populated_children(True)
            # end for
            comments = threaded_comments
        else:
            comments = all_comments
        # end if
        return comments
    # end def fill_descendants
    #// 
    #// Used internally to generate an SQL string for searching across multiple columns
    #// 
    #// @since 3.1.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #// 
    #// @param string $string
    #// @param array $cols
    #// @return string
    #//
    def get_search_sql(self, string=None, cols=None):
        
        global wpdb
        php_check_if_defined("wpdb")
        like = "%" + wpdb.esc_like(string) + "%"
        searches = Array()
        for col in cols:
            searches[-1] = wpdb.prepare(str(col) + str(" LIKE %s"), like)
        # end for
        return " AND (" + php_implode(" OR ", searches) + ")"
    # end def get_search_sql
    #// 
    #// Parse and sanitize 'orderby' keys passed to the comment query.
    #// 
    #// @since 4.2.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #// 
    #// @param string $orderby Alias for the field to order by.
    #// @return string|false Value to used in the ORDER clause. False otherwise.
    #//
    def parse_orderby(self, orderby=None):
        
        global wpdb
        php_check_if_defined("wpdb")
        allowed_keys = Array("comment_agent", "comment_approved", "comment_author", "comment_author_email", "comment_author_IP", "comment_author_url", "comment_content", "comment_date", "comment_date_gmt", "comment_ID", "comment_karma", "comment_parent", "comment_post_ID", "comment_type", "user_id")
        if (not php_empty(lambda : self.query_vars["meta_key"])):
            allowed_keys[-1] = self.query_vars["meta_key"]
            allowed_keys[-1] = "meta_value"
            allowed_keys[-1] = "meta_value_num"
        # end if
        meta_query_clauses = self.meta_query.get_clauses()
        if meta_query_clauses:
            allowed_keys = php_array_merge(allowed_keys, php_array_keys(meta_query_clauses))
        # end if
        parsed = False
        if self.query_vars["meta_key"] == orderby or "meta_value" == orderby:
            parsed = str(wpdb.commentmeta) + str(".meta_value")
        elif "meta_value_num" == orderby:
            parsed = str(wpdb.commentmeta) + str(".meta_value+0")
        elif "comment__in" == orderby:
            comment__in = php_implode(",", php_array_map("absint", self.query_vars["comment__in"]))
            parsed = str("FIELD( ") + str(wpdb.comments) + str(".comment_ID, ") + str(comment__in) + str(" )")
        elif php_in_array(orderby, allowed_keys):
            if (php_isset(lambda : meta_query_clauses[orderby])):
                meta_clause = meta_query_clauses[orderby]
                parsed = php_sprintf("CAST(%s.meta_value AS %s)", esc_sql(meta_clause["alias"]), esc_sql(meta_clause["cast"]))
            else:
                parsed = str(wpdb.comments) + str(".") + str(orderby)
            # end if
        # end if
        return parsed
    # end def parse_orderby
    #// 
    #// Parse an 'order' query variable and cast it to ASC or DESC as necessary.
    #// 
    #// @since 4.2.0
    #// 
    #// @param string $order The 'order' query variable.
    #// @return string The sanitized 'order' query variable.
    #//
    def parse_order(self, order=None):
        
        if (not php_is_string(order)) or php_empty(lambda : order):
            return "DESC"
        # end if
        if "ASC" == php_strtoupper(order):
            return "ASC"
        else:
            return "DESC"
        # end if
    # end def parse_order
# end class WP_Comment_Query
