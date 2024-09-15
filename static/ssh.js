/*jslint browser:true */

console.log('main.js loaded');

var wssh = {};

document.addEventListener('DOMContentLoaded', function() {
  var style = {},
      default_fonts,
      fields = ['hostname', 'port', 'username'],
      form_keys = fields.concat(['password', 'totp']),
      opts_keys = ['bgcolor', 'title', 'encoding', 'command', 'term', 'fontsize', 'fontcolor', 'cursor'],
      url_form_data = {},
      url_opts_data = {};

  function decode_uri_component(uri) {
    try {
      return decodeURIComponent(uri);
    } catch(e) {
      console.error(e);
    }
    return '';
  }

  function decode_password(encoded) {
    try {
      return window.atob(encoded);
    } catch (e) {
       console.error(e);
    }
    return null;
  }

  function parse_url_data(string, form_keys, opts_keys, form_map, opts_map) {
    var i, pair, key, val,
        arr = string.split('&');

    for (i = 0; i < arr.length; i++) {
      pair = arr[i].split('=');
      key = pair[0].trim().toLowerCase();
      val = pair.slice(1).join('=').trim();

      if (form_keys.indexOf(key) >= 0) {
        form_map[key] = val;
      } else if (opts_keys.indexOf(key) >= 0) {
        opts_map[key] = val;
      }
    }

    if (form_map.password) {
      form_map.password = decode_password(form_map.password);
    }
  }

  function parse_xterm_style() {
    var styleElem = document.querySelector('.xterm-helpers style');
    if (styleElem) {
      var text = styleElem.textContent;
      var arr = text.split('xterm-normal-char{width:');
      style.width = parseFloat(arr[1]);
      arr = text.split('div{height:');
      style.height = parseFloat(arr[1]);
    }
  }

  function get_cell_size(term) {
    style.width = term._core._renderService._renderer.dimensions.actualCellWidth;
    style.height = term._core._renderService._renderer.dimensions.actualCellHeight;
  }

  function current_geometry(term) {
    if (!style.width || !style.height) {
      try {
        get_cell_size(term);
      } catch (TypeError) {
        parse_xterm_style();
      }
    }

    var cols = parseInt(window.innerWidth / style.width, 10) - 1;
    var rows = parseInt(window.innerHeight / style.height, 10);
    return {'cols': cols, 'rows': rows};
  }

  function resize_terminal(term) {
    var geometry = current_geometry(term);
    term.on_resize(geometry.cols, geometry.rows);
  }

  function set_background_color(term, color) {
    term.setOption('theme', {
      background: color
    });
  }

  function set_font_color(term, color) {
    term.setOption('theme', {
      foreground: color
    });
  }

  function reset_font_family(term) {
    if (!term.font_family_updated) {
      console.log('Already using default font family');
      return;
    }

    if (default_fonts) {
      term.setOption('fontFamily', default_fonts);
      term.font_family_updated = false;
      console.log('Using default font family ' + default_fonts);
    }
  }

  function format_geometry(cols, rows) {
    return JSON.stringify({'cols': cols, 'rows': rows});
  }

  function read_as_text_with_decoder(file, callback, decoder) {
    var reader = new window.FileReader();

    if (decoder === undefined) {
      decoder = new window.TextDecoder('utf-8', {'fatal': true});
    }

    reader.onload = function() {
      var text;
      try {
        text = decoder.decode(reader.result);
      } catch (TypeError) {
        console.log('Decoding error happened.');
      } finally {
        if (callback) {
          callback(text);
        }
      }
    };

    reader.onerror = function(e) {
      console.error(e);
    };
    var blob = new Blob([file], { type: 'plain/text' });
    reader.readAsArrayBuffer(blob);
  }

  function read_as_text_with_encoding(file, callback, encoding) {
    var reader = new window.FileReader();

    if (encoding === undefined) {
      encoding = 'utf-8';
    }

    reader.onload = function() {
      if (callback) {
        callback(reader.result);
      }
    };

    reader.onerror = function(e) {
      console.error(e);
    };

    reader.readAsText(file, encoding);
  }

  function read_file_as_text(file, callback, decoder) {
    if (!window.TextDecoder) {
      read_as_text_with_encoding(file, callback, decoder);
    } else {
      read_as_text_with_decoder(file, callback, decoder);
    }
  }

  function reset_wssh() {
    for (var name in wssh) {
      if (wssh.hasOwnProperty(name) && name !== 'connect') {
        delete wssh[name];
      }
    }
  }

  function connect() {
    var msg = {id: 1, status: 'ok', encoding: 'utf-8'};

    var url = `ws://localhost:8000/ws/${msg.id}`,
        sock = new window.WebSocket(url),
        encoding = 'utf-8',
        decoder = window.TextDecoder ? new window.TextDecoder(encoding) : encoding,
        terminal = document.getElementById('terminal'),
        termOptions = {
          cursorBlink: true,
          theme: {
            background: url_opts_data.bgcolor || 'black',
            foreground: url_opts_data.fontcolor || 'white',
            cursor: url_opts_data.cursor || url_opts_data.fontcolor || 'white'
          }
        };

    if (url_opts_data.fontsize) {
      var fontsize = window.parseInt(url_opts_data.fontsize);
      if (fontsize && fontsize > 0) {
        termOptions.fontSize = fontsize;
      }
    }

    var term = new Terminal(termOptions);

    term.fitAddon = new window.FitAddon.FitAddon();
    term.loadAddon(term.fitAddon);

    console.log(url);
    if (!msg.encoding) {
      console.log('Unable to detect the default encoding of your server');
      msg.encoding = encoding;
    } else {
      console.log('The default encoding of your server is ' + msg.encoding);
    }

    function term_write(text) {
      if (term) {
        term.write(text);
        if (!term.resized) {
          resize_terminal(term);
          term.resized = true;
        }
      }
    }

    function set_encoding(new_encoding) {
      if (!new_encoding) {
        console.log('An encoding is required');
        return;
      }

      if (!window.TextDecoder) {
        decoder = new_encoding;
        encoding = decoder;
        console.log('Set encoding to ' + encoding);
      } else {
        try {
          decoder = new window.TextDecoder(new_encoding);
          encoding = decoder.encoding;
          console.log('Set encoding to ' + encoding);
        } catch (RangeError) {
          console.log('Unknown encoding ' + new_encoding);
          return false;
        }
      }
    }

    wssh.set_encoding = set_encoding;

    if (url_opts_data.encoding) {
      if (set_encoding(url_opts_data.encoding) === false) {
        set_encoding(msg.encoding);
      }
    } else {
      set_encoding(msg.encoding);
    }

    wssh.geometry = function() {
      var geometry = current_geometry(term);
      console.log('Current window geometry: ' + JSON.stringify(geometry));
    };

    wssh.send = function(data) {
      if (!sock) {
        console.log('Websocket was already closed');
        return;
      }

      if (typeof data !== 'string') {
        console.log('Only string is allowed');
        return;
      }

      try {
        JSON.parse(data);
        sock.send(data);
      } catch (SyntaxError) {
        data = data.trim() + '\r';
        sock.send(JSON.stringify({'data': data}));
      }
    };

    wssh.reset_encoding = function() {
      if (encoding === msg.encoding) {
        console.log('Already reset to ' + msg.encoding);
      } else {
        set_encoding(msg.encoding);
      }
    };

    wssh.resize = function(cols, rows) {
      if (!term) {
        console.log('Terminal was already destroyed');
        return;
      }

      var valid_args = cols > 0 && rows > 0;
      if (!valid_args) {
        console.log('Invalid arguments for resizing terminal');
      } else {
        term.on_resize(cols, rows);
      }
    };

    wssh.set_bgcolor = function(color) {
      set_background_color(term, color);
    };

    wssh.set_fontcolor = function(color) {
      set_font_color(term, color);
    };

    wssh.custom_font = function() {
      update_font_family(term);
    };

    wssh.default_font = function() {
      reset_font_family(term);
    };

    term.on_resize = function(cols, rows) {
      if (cols !== this.cols || rows !== this.rows) {
        console.log('Resizing terminal to geometry: ' + format_geometry(cols, rows));
        this.resize(cols, rows);
        sock.send(JSON.stringify({'resize': [cols, rows]}));
      }
    };

    term.onData(function(data) {
      console.log(data);
      sock.send(JSON.stringify({'data': data}));
    });

    sock.onopen = function() {
      term.open(terminal);
      update_font_family(term);
      term.focus();
      if (url_opts_data.command) {
        setTimeout(function() {
          sock.send(JSON.stringify({'data': url_opts_data.command + '\r'}));
        }, 500);
      }
    };

    sock.onmessage = function(msg) {
      read_file_as_text(msg.data, term_write, decoder);
    };

    sock.onerror = function(e) {
      console.error(e);
    };

    sock.onclose = function(e) {
      term.dispose();
      term = undefined;
      sock = undefined;
      reset_wssh();
    };

    window.addEventListener('resize', function() {
      if (term) {
        resize_terminal(term);
      }
    });
  }

  wssh.connect = connect;

  function cross_origin_connect(event) {
    console.log(event.origin);
    var prop = 'connect',
        args;

    try {
      args = JSON.parse(event.data);
    } catch (SyntaxError) {
      args = event.data.split('|');
    }

    if (!Array.isArray(args)) {
      args = [args];
    }

    try {
      wssh[prop].apply(wssh, args);
    } finally {
    }
  }

  window.addEventListener('message', cross_origin_connect, false);

  parse_url_data(
    decode_uri_component(window.location.search.substring(1)) + '&' + decode_uri_component(window.location.hash.substring(1)),
    form_keys, opts_keys, url_form_data, url_opts_data
  );

  connect();
});