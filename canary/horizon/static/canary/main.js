setupCanary = function( optionalBaseUrl, optionalCallback ) {
  baseUrl = (typeof optionalBaseUrl === "undefined") ? "." : optionalBaseUrl
  // optionalCallback has no parameters

  var bytes = [[1, ' B'], [1024, ' KB'], [1048576, ' MB'],
      [1073741824, ' GB']];

  // List of unit formatters: If the first item is a substring of a metric, the
  // units defined in the second item are used.
  units = [
    ['memory', bytes],
    ['cpu[', [[1, '%']]],
    ['df', bytes],
    ['swap', bytes],
  ];

  // List of currently active graphs
  var graphs = [];

  /* Fetch new data and display it in the graph
   *
   * Optional parameters:
   *  opts:
   *    thumbnail        (boolean) render minimal graph (no axis, no border)
   */
  function renderGraph(graph, opts) {
    var toTime = toTimes[graph.metric];

    var from_time = toTime - graph.timeframe * 60;

    $.get(baseUrl + '/metrics/' + graph.metric + '/',
         {resolution: graph.resolution, from_time: from_time, cf: graph.cf},
                                                                function(resp) {
      var data = [];

      var max = 0;

      $.each(resp.data, function(i, pt) {
        if(!(pt[2] == null)) {
          data.push([pt[0] * 1000, pt[2]]);
          if(pt[2] > max) {
            max = pt[2];
          }
        }
      });

      if(data.length == 0) {
        graph.el.html('<p class="graph-placeholder">No data</p>');
        return;
      }

      toTime = data[data.length - 1][0] / 1000;

      from_time = toTime - graph.timeframe * 60;

      toTimes[graph.metric] = toTime;

      for(var i = 0; i < data.length; i++) {
        if(data[i][0] < from_time * 1000) {
          data.splice(i, 1);
        }
      }

      var unit = null;
      $.each(units, function(i, u) {
        if(graph.metric.indexOf(u[0]) != -1) {
          unit = u;
        }
      });

      var level = null;
      if(unit) {
        $.each(unit[1], function(i, l) {
          if(max > l[0] || level == null) {
            level = l;
          }
        });
      }

      var yaxis = {};
      if(level) {
        $.each(data, function(i) {
          data[i][1] /= level[0];
        });

        yaxis.tickFormatter = function(v, axis) {
          return v.toFixed(2) + level[1];
        }
      }

      var popts =
        {xaxis: {mode: 'time', min: from_time * 1000},
         yaxis: yaxis,
         colors: ['#145E8D'],
         };

      if (opts && opts['thumbnail']) {
        popts.yaxis.show=false;
        popts.xaxis.show=false;

        // remove border, cleaner look (caller can add it through html instead)
        popts.grid = { borderWidth:0 }
      }

      $.plot(graph.el, [data], popts );
    });
 }

  /* Add a metric to be graphed
   *
   * Optional parameters:
   *  render_opts:
   *    target_container  (string) instead of dynamically adding new graph obj,
   *                      render to this static target
   *    thumbnail         (boolean) render a minimal feature graph
   *
   */
  function addMetric(metric, timeframe, cf, res, render_opts) {
    if($.inArray(metric, metricNames) == -1) {
      return;
    }
    if (render_opts && render_opts['target_container']) {
        var container = $(render_opts['target_container']);
    } else {
        var container = $('#canary-templates .graph-container').clone();
        container.appendTo($('#graphs'));
    }
    container.find('.metric-name').text(metric);
    var el = container.find('.graph');
    var graph = {el: el, metric: metric, timeframe: timeframe,
                 resolution: res, cf: cf};

    // replace previous click event handler
    container.find('.delete-graph').off('click').on('click', function() {
      // If delete button hidden, shouldn't do anything
      // Functions can trigger click event though to stop updating graph
      if ( $(this).is(":visible") ) {
          container.remove();
      }
      for(var i = 0; i < graphs.length; i++) {
        if(graphs[i] == graph) {
          graphs.splice(i, 1);
          clearInterval(graph.timer);
        }
      }
    });
    graphs.push(graph);
    renderGraph(graph, render_opts);
    graph.timer = setInterval(function() {
      renderGraph(graph, render_opts);
    }, res * 1000);
  }

  // Return false if form is currently invalid, and return the form data if
  // valid. Used to determine if submit button should be disabled.
  function validateMetricForm() {
    var metric = $('#metric-select').val();
    var cf = $('#cf-select').val();
    var timeframe = parseInt($('#timeframe-input').val());
    var res = parseInt($('#update-input').val());
    if(metric == '') {
      return false;
    }
    if(!(timeframe > 0)) {
      return false;
    }
    if(!(res > 0)) {
      return false;
    }
    return [metric, timeframe, cf, res];
  }

  var metricNames = [];

  // Latest data of each metric
  var toTimes = {};

  // Cumulator functions available for each metric
  var cfs = {};

  // Fetch list of metrics and populate form, toTimes, and cfs
  $.get(baseUrl + '/metrics/', function(data) {
    $.each(data.metrics.sort(), function(index, metric) {
      var name = metric[0];
      var toTime = metric[1];
      var metricCfs = metric[2];
      $('<option/>', {value: name, text: name}).appendTo($('#metric-select'));
      metricNames.push(name);
      toTimes[name] = toTime;
      cfs[name] = metricCfs.sort();
    });

    // Add initial graphs
    addMetric('load.load', 10, 'AVERAGE', 2)
    addMetric('memory.memory-used', 10, 'AVERAGE', 2);
    if (typeof optionalCallback === "function") optionalCallback();
  });

  // Validate form whenever input is changed
  $('#add-metric-form .validated').on('input change', function() {
    if(validateMetricForm()) {
      $('#metric-submit').removeAttr('disabled');
    } else {
      $('#metric-submit').attr('disabled', 'disabled');
    }
  });

  // Update update interval when timeframe is updated
  $('#timeframe-input').on('input change', function() {
    data = validateMetricForm();
    if(data) {
      $('#update-input').val(Math.ceil(data[1] * 60 / 400));
    }
  });

  // Add metric upon form submission
  $('#add-metric-form').on('submit', function() {
    var data = validateMetricForm();
    addMetric(data[0], data[1], data[2], data[3]);
    return false;
  });

  // Update cumulator function dropdown when metric is selected
  $('#metric-select').on('change', function() {
    var metric = $('#metric-select').val();
    if(metric == '') {
      $('#cf-select').attr('disabled', 'disabled');
    } else {
      $('#cf-select').removeAttr('disabled');
      $('#cf-select').html('');
      $.each(cfs[metric], function() {
        $('#cf-select').append($('<option value="' + this + '">' +
                                                       this + '</option>'));
      });
    }
  });

  // Manage Exports
  this.canaryAddMetric = addMetric;
  this.canaryMetricNames = metricNames;
}
