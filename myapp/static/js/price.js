function loadPrices(criteria) {

  var apiBase = '/api/' + criteria.realm + '/' + criteria.faction + '/';

  if (typeof(criteria.item_ids) != "undefined") {

    $.get(apiBase + "item_list/" + criteria.item_ids.join(','), function(res) {

      if (!res.error) {
        renderItems(res.items);
      }

    });

  } else {

    var params = {};
    if (criteria.cls) params.cls = criteria.cls;
    if (criteria.keyword) params.k = criteria.keyword;
    if (criteria.quality) params.q = criteria.quality;
    if (criteria.sort) params.s = criteria.sort;
    if (criteria.page) params.p = criteria.page;

    if (!$.isEmptyObject(params)) {

      var qss = [];
      for (var k in params) {
        qss.push(k + "=" + encodeURIComponent(params[k]));
      }

      var qs = qss.join('&');
      var api = apiBase + 'prices_search' + (qs ? ('?' + qs) : '');
      
      $.get(api, function(res) {
        if (!res.error) {
          renderItems(res.items);
        }
      });

    }

  }

}


function renderItems(items) {

  $("#items-table tbody").empty();
  $.each(items, function(idx, item) {
    var row = $("<tr>");
    $("<td>").html(item.id).appendTo(row);
    $("<td>").append(
      $("<a>").addClass("itemlink").attr({
        href: "http://db.178.com/wow/cn/item/" + item.id + ".html",
        itemId: item.id,
        target: '_blank'
      }).addClass("q" + item.quality).html(item.name)
    ).appendTo(row);
    $("<td>").append(prettyPrice(item.average)).addClass('numbers').appendTo(row);
    $("<td>").append(prettyPrice(item.min_price)).addClass('numbers').appendTo(row);
    $("<td>").append(prettyPrice(item.sellPrice)).addClass('numbers').appendTo(row);
    $("<td>").html(item.quantity).addClass('numbers').appendTo(row);
    $("<td>").html(item.lastUpdate).appendTo(row);

    $("#items-table tbody").append(row);
  });

}


function prettyPrice(price) {

  price = parseInt(price);

  var g = Math.floor(price / 10000),
      s = Math.floor((price % 10000) / 100),
      c = Math.floor(price % 100);

  var ret = $('<span>');;
  if (g) $("<span>").addClass("money_g").html(g).appendTo(ret);
  if (s) $("<span>").addClass("money_s").html(s).appendTo(ret);
  $("<span>").addClass("money_c").html(c).appendTo(ret);;

  return ret;
}


