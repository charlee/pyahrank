window.TOOLTIP = {


  baseUrl: 'http://db.178.com/wow/cn/a/item/',

  get: function(itemId, callback) {

    itemId = parseInt(itemId);
    var url = this.baseUrl + itemId + ".js";
    $.getScript(url, function(data, textStatus, jqxhr) {
      
      if (textStatus == "success") {
        var item = $178DB.data[itemId];
        callback(item);
      }

    });
  }

};




window.$178DB = {

  data: {},

  regstItem: function(item) {
    this.data[item.id] = item;
  }
};
