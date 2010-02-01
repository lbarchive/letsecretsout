google.load("jquery", "1");


// Global error indicator
function init_error_indicator() {
  $("body").ajaxError(function(event, request, settings){
    var err_msg;
    switch(request.status) {
      case 404:
        err_msg = "Oops! Got 404 NOT FOUND, this should be a bug, you may notify the problem generator, the creator of I LSO.";
        break;
      case 500:
        err_msg = "It is 500! Server does not want to serve you! :-)";
        break;
      default:
        err_msg = "Unknown problem!";
      }
    humanMsg.displayMsg(err_msg, 'error');
    });
  }


// Flagging
function flag(secret_id) {
  var query_url = window.location.protocol + '//' + window.location.host + '/';
  if (secret_id == '#')
    return;
  $.getJSON(query_url + 'flag.json?id=' + secret_id + '&callback=?', function(json) {
    if (json.error == 0) {
      $("a.flag").each(function(){
        var $ele = $(this)
        if ($ele.attr('href').indexOf("('" + json.id + "')") >= 0) {
          $ele.replaceWith(json.message);
          return false;
          }
        });
      }
    else
      humanMsg.displayMsg(json.message, 'error');
    });
  }


function send_gravatar_check() {
  var query_url = window.location.protocol + '//' + window.location.host + '/';
  $.post(query_url + 'send_gravatar_check.json', {
      gravatar: $('#gravatar').val()
      }, function(json) {
    if (json.error == 0)
      humanMsg.displayMsg(json.message)
    else
      humanMsg.displayMsg(json.message, 'error');
    }, 'json');
  }


function render_gravatar() {
  var base_url = window.location.protocol + '//' + window.location.host + '/';
  var gravatar_option = $.cookie('gravatar_option');
  switch (gravatar_option) {
    case 'gravatar':
      d = '';
      break;
    case 'secret':
      d = '&d=' + base_url + 'img/avatar.png';
      break;
    case 'monsterid':
    case 'wavatar':
      d = '&d=' + gravatar_option;
      break;
    case 'off':
      return;
    default:
      d = '&d=identicon';
    }
  $('span.gravatar-hash').each(function(){
      var ele = $(this);
      ele.replaceWith('<img class="gravatar" src="http://www.gravatar.com/avatar/' + ele.text() + '?s=48' + d + '"/>');
      });
  }

// Initialize Disqus
function init_disqus() {
  var query = '';
  var i = 0;
  $('a[href*="#disqus_thread"]').each(function(){
    query += 'url' + i++ + '=' + encodeURIComponent(this.href.replace('https://', 'http://')) + '&';
    });
  if (query)
    $.getScript("http://disqus.com/forums/lso/get_num_replies.js?" + query);
  }

// Jumper
function jumper_relocate() {
  var window_top = $(window).scrollTop();
  var div_top = $('#jumper-anchor').offset().top;
  if (window_top > div_top)
    $('#jumper')
        .css('width', $('#jumper').width())
        .addClass('sticky')
  else
    $('#jumper').removeClass('sticky');
  }

google.setOnLoadCallback(function () {
  var messages = window.lso_messages;
  if (messages)
    for (i=0; i<messages.length; i++)
      humanMsg.displayMsg(messages[i][1], messages[i][0]);
  init_error_indicator();
  init_jquery_cookie_plugin();
  render_gravatar();
  init_disqus();
  // Jumper
  $(window).scroll(jumper_relocate);
  jumper_relocate();
  });

// ===================
// Third-party library

function init_jquery_cookie_plugin() {
/**
 * Cookie plugin
 *
 * Copyright (c) 2006 Klaus Hartl (stilbuero.de)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */

/**
 * Create a cookie with the given name and value and other optional parameters.
 *
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Set the value of a cookie.
 * @example $.cookie('the_cookie', 'the_value', { expires: 7, path: '/', domain: 'jquery.com', secure: true });
 * @desc Create a cookie with all available options.
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Create a session cookie.
 * @example $.cookie('the_cookie', null);
 * @desc Delete a cookie by passing null as value. Keep in mind that you have to use the same path and domain
 *       used when the cookie was set.
 *
 * @param String name The name of the cookie.
 * @param String value The value of the cookie.
 * @param Object options An object literal containing key/value pairs to provide optional cookie attributes.
 * @option Number|Date expires Either an integer specifying the expiration date from now on in days or a Date object.
 *                             If a negative value is specified (e.g. a date in the past), the cookie will be deleted.
 *                             If set to null or omitted, the cookie will be a session cookie and will not be retained
 *                             when the the browser exits.
 * @option String path The value of the path atribute of the cookie (default: path of page that created the cookie).
 * @option String domain The value of the domain attribute of the cookie (default: domain of page that created the cookie).
 * @option Boolean secure If true, the secure attribute of the cookie will be set and the cookie transmission will
 *                        require a secure protocol (like HTTPS).
 * @type undefined
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */

/**
 * Get the value of a cookie with the given name.
 *
 * @example $.cookie('the_cookie');
 * @desc Get the value of a cookie.
 *
 * @param String name The name of the cookie.
 * @return The value of the cookie.
 * @type String
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */
jQuery.cookie = function(name, value, options) {
    if (typeof value != 'undefined') { // name and value given, set cookie
        options = options || {};
        if (value === null) {
            value = '';
            options.expires = -1;
        }
        var expires = '';
        if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
            var date;
            if (typeof options.expires == 'number') {
                date = new Date();
                date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            } else {
                date = options.expires;
            }
            expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
        }
        // CAUTION: Needed to parenthesize options.path and options.domain
        // in the following expressions, otherwise they evaluate to undefined
        // in the packed version for some reason...
        var path = options.path ? '; path=' + (options.path) : '';
        var domain = options.domain ? '; domain=' + (options.domain) : '';
        var secure = options.secure ? '; secure' : '';
        document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
    } else { // only name given, get cookie
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};
} // End of init_jquery_cookie_plugin
// vim:ts=2:sw=2:et:
