google.load("language", "1");


function prettify_lang_name(lang) {
  var words = lang.split('_');
  var result = new Array();
  for (var i=0; i<words.length; i++) {
    var word = words[i].charAt(0).toUpperCase() + words[i].substr(1).toLowerCase();
    result.push(word);
    }
  return result.join(' ');
  }


function detect_language() {
  google.language.detect($('#subject').val(), function(result) {
    if (!result.error) {
      var language = 'unknown';
      for (l in google.language.Languages) {
        if (google.language.Languages[l] == result.language) {
          language = l;
          break;
          }
        }
      if (language != 'unknown') {
        var item = $('#language option[value=' + result.language.replace('-', '_') + ']').get(0)
        if (item)
          $('#language').get(0).selectedIndex = item.index
        else
          alert(prettify_lang_name(language) + " is not supported yet! Please ask for adding it.");
        }
      else
        alert("Google Translate couldn't be detected!");
      }
    else
      alert("Google Translate responded an error!");
    });
  }


function preview_secret() {
  var query_url = window.location.protocol + '//' + window.location.host + '/';
  $.post(query_url + 'preview.json', {
      name: $('#name').val(), 
      gravatar: $('#gravatar').val(),
      gravatar_check: $('#gravatar_check').val(),
      language: $('#language').val(),
      subject: $('#subject').val(),
      story: $('#story').val(),
      tags: $('#tags').val()
      }, function(json) {
    if (json.error == 0) {
      $("#preview").empty().hide().html('<div class="preview-header">' + json.preview_header + '</div>' + json.secret_preview);
      render_gravatar();
      $('#preview').fadeIn('slow');
      // Scroll to preview
      $('body')[0].scrollTop = $('#preview')[0].offsetTop;
      }
    else
      humanMsg.displayMsg(json.message, 'error')
    }, 'json');
  }


function init_post() {
  /*
  var langs = google.language.Languages;
  for (var lang in langs)
    $('<option value="' + langs[lang] + '">' + prettify_lang_name(lang) + '</option>').appendTo($('#language'));
  */
  $('#subject').keypress(function() {
      $('#subject-counter').text($(this).val().length);
      })
      .keypress();
  $('#story').keypress(function() {
      $('#story-counter').text($(this).val().length);
      })
      .keypress();
  }

google.setOnLoadCallback(init_post);
