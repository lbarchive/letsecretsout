// Deleting
function delete_secret(secret_id) {
  var query_url = window.location.protocol + '//' + window.location.host + '/';
  if (secret_id == '#')
    return;
  $.getJSON(query_url + 'admin/delete.json?id=' + secret_id + '&callback=?', function(json) {
    if (json.error == 0) {
      $("a.delete").each(function(){
        var $ele = $(this)
        if ($ele.attr('href').indexOf("('" + json.id + "')") >= 0) {
          $ele.replaceWith(json.message);
          $('#messages').empty();
          return false;
          }
        });
      }
    else
      $('#messages').empty().html('<div class="error">' + json.message + '</div>').hide().fadeIn('fast');
    });
  }
