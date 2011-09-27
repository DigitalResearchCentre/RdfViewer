var cur_line_diff = null;

function get_info(str){
  var lst = str.split('-');
  var part_map = {
    'IN': 'Inferno',
    'PU': 'Purgatorio',
    'PA': 'Paradiso'
  }
  return {
    'wit': lst[3],
    'part': part_map[lst[0]],
    'canto': lst[1].substr(1),
    'line':lst[2]
  }
}

function create_line_diff(info){
  var line_diff = $('<div class="line_diff"></div>');
  var close = $('<input type="button" value="close"/>');
  close.click(function(){
    line_diff.remove();
  });
  var diff_table = $('<table></table>');
  line_diff.append(diff_table);
  $.get('/line', {
    'part': info['part'],
    'canto': info['canto'],
    'line': info['line']
  }, function(data){
    var alignment = data['alignment']
    for (var i in alignment){
      var wit = alignment[i]['witness'];
      var row = $('<tr><td><span class="wit">'+wit+': </span></td></tr>');
      var tokens = alignment[i]['tokens'];
      for (var j in tokens){
        var cell = $('<td></td>')
        if (tokens[j] != null){
          token = $(tokens[j]['t']);
          $(token).find('rdg').each(function(){
            $(this).find(':first')
            .before('<span>'+$(this).attr('type')+': </span>');
          });
          cell.append(token);
        }
        row.append(cell);
      }
      diff_table.append(row);
    }
    line_diff.append(close);
  }, 'json');
  return line_diff;
}

function apply_format(){
  var line_type = $(this).attr('n') % 3;
  if (line_type != 1){
    $(this).addClass('intend'); 
  }

  if (line_type == 0){
    $(this).find(':first').before(
      '<span class="linenum">'+$(this).attr('n')+'</span>');
  }
  $(this).find('rdg').each(function(){
    if ($(this).attr('type') == 'lit'){
      $(this).css('display', 'inline-block');
    }
  });
  $(this).click(function(){
    var id = $(this).attr('id');
    if (cur_line_diff != id){
      cur_line_diff = id;
      $('.line_diff').remove();
      var line_diff = create_line_diff(get_info(id));
      $(this).append(line_diff);
    }
  });
}

function update_navigator(){
  $.get('', function(data){
    nav.cantos.empty();
    for (var i = 0; i < data.cantos.length; i++) {
      canto = data.cantos[i];
      var selected = '';
      if (data.canto.uri === canto.uri){
        selected = 'selected="selected"'
      }
      nav.cantos.append('<option value="'+canto.uri+'"'+selected+'>'+
                        canto.label+'</option>');
    };
  }, 'json');
}

function RdfViewer(){
  this.work = $('#work');
  this.part = $('#part');
  this.canto = $('#canto');
  this.line = $('#line');
  this.doc = $('#doc');
  this.go = $('#go');
  this.cur_page = $('#cur_page');
  this.transcript = $('#transcript');
  var _this = this;
  this.part.change(function(){_this.updateNavigator()});
  this.canto.change(function(){_this.updateNavigator()});
}


RdfViewer.prototype = {
  getNavData: function(){
    var nav_data = {};
    function update_nav_data(viewer, array){
      for (var i = 0; i < array.length; i++) {
        var val = viewer[array[i]].val();
        if (val) {
          nav_data[array[i]] = val;
        }
      }
    };
    var _this = this;
    update_nav_data(this, ['part', 'canto', 'line', 'doc']);
    return nav_data;
  },

  updateNavigator: function(){
    this.go.attr('disabled', 'disabled');
    var post_data = this.getNavData();
    post_data['format'] = 'json';
    var _this = this;
    $.get('/'+this.work.val(), post_data, function(data){
      function loadOption(select, d){
        select.empty();
        var items = d['items']
        for (var i = 0; i < items.length; i++) {
          var option = $('<option></option>').
            attr('value', items[i].uri).text(items[i].label)
          if (items[i].uri == d['selected']){
            option.attr('selected', 'selected');
          }
          select.append(option);
        }
      }
      for (var key in data){
        loadOption(_this[key], data[key]);
      }
      _this.go.removeAttr('disabled');
    }, 'json');
  },

  updateContent: function(data_dict){
    var _this = this;
    $.get('/page', data_dict, function(data){
      var transcript = data['transcript'];
      var image = data['image'][0];
      _this.cur_page.val(data['page']);
      _this.transcript.html(transcript);
      _this.transcript.find('l').each(apply_format);
      if (image){
        $('#image>iframe').attr('src', image).show();
      }else{
        $('#image>iframe').hide();
      }
    }, 'json');
  }
}

$(document).ready(function(){
  var viewer = new RdfViewer();
  viewer.updateContent(viewer.getNavData());
  $('#go').click(function(){
    viewer.updateContent(viewer.getNavData());
  });
  $('#prev').click(function(){
    viewer.updateContent({'page': viewer.cur_page.val(), 'func': 'prev'});
  })
  $('#next').click(function(){
    viewer.updateContent({'page': viewer.cur_page.val(), 'func': 'next'});
  })

});
