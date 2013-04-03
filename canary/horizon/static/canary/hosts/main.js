setupCanary = function() {
  var bytes = [[1, ' B'], [1024, ' KB'], [1048576, ' MB'],
      [1073741824, ' GB']];

  // List of unit formatters: If the first item is a substring of a metric, the
  // units defined in the second item are used.
  units = [
    ['memory', bytes],
    ['cpu', [[1, '%']]],
    ['df', bytes],
    ['swap', bytes],
  ];

  // List of currently active graphs
  var graphs = [];

  // Fetch new data and display it in the graph
  function renderGraph(graph) {
    var to_time = to_times[graph.metric];

    var from_time = to_time - graph.timeframe * 60;

    $.get('./metrics/' + graph.metric + '/',
         {resolution: graph.resolution, from_time: from_time, cf: graph.cf},
                                                                function(resp) {
      var data = []

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

      to_time = data[data.length - 1][0] / 1000;

      from_time = to_time - graph.timeframe * 60;

      to_times[graph.metric] = to_time;

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

      $.plot(graph.el, [data],
        {xaxis: {mode: 'time', min: from_time * 1000},
         yaxis: yaxis,
         colors: ['#145E8D']});
    });
  }

  // Add a metric to be graphed
  function addMetric(metric, timeframe, cf) {
    var container = $('#canary-templates .graph-container').clone();
    container.appendTo($('#graphs'));
    container.find('.metric-name').text(metric);
    var el = container.find('.graph');
    var res = Math.ceil(timeframe * 60 / 400);
    var graph = {el: el, metric: metric, timeframe: timeframe,
                 resolution: res, cf: cf};
    container.find('.delete-graph').on('click', function() {
      container.remove();
      for(var i = 0; i < graphs.length; i++) {
        if(graphs[i] == graph) {
          graphs.splice(i, 1);
          clearInterval(graph.timer);
        }
      }
    });
    graphs.push(graph);
    renderGraph(graph);
    graph.timer = setInterval(function() {
      renderGraph(graph);
    }, res * 1000);
  }

  // Return false if form is currently invalid, and return the form data if
  // valid. Used to determine if submit button should be disabled.
  function validateMetricForm() {
    var metric = $('#metric-select').val();
    var cf = $('#cf-select').val();
    var timeframe = parseInt($('#timeframe-input').val());
    if(metric == '') {
      return false;
    }
    if(!(timeframe > 0)) {
      return false;
    }
    return [metric, timeframe, cf];
  }

  // Latest data of each metric
  var to_times = {};

  // Cumulator functions available for each metric
  var cfs = {};

  // Fetch list of metrics and populate form, to_times, and cfs
  $.get('./metrics/', function(data) {
    $.each(data.metrics.sort(), function(index, metric) {
      var name = metric[0];
      var to_time = metric[1];
      var metric_cfs = metric[2];
      $('<option/>', {value: name, text: name})
                                             .appendTo($('#metric-select'));
      to_times[name] = to_time;
      cfs[name] = metric_cfs.sort();
    });

    // Add initial graphs
    addMetric('load.load', 10, 'AVERAGE')
    addMetric('memory.memory-used', 10, 'AVERAGE');
  });

  // Validate form whenever input is changed
  $('#add-metric-form .validated').on('input change', function() {
    if(validateMetricForm()) {
      $('#metric-submit').removeAttr('disabled');
    } else {
      $('#metric-submit').attr('disabled', 'disabled');
    }
  });

  // Add metric upon form submission
  $('#add-metric-form').on('submit', function() {
    var data = validateMetricForm();
    addMetric(data[0], data[1], data[2]);
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
}
