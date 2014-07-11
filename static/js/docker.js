function get_hosts(callback){
    $.get("../hosts",function(data){
        console.log("get_hosts:data is " + data);
        var hosts = $.parseJSON(data);
        callback(hosts);
    });
}

function get_details(host,callback){
    $.get("../hosts/" + host,function(data){
        console.log("get_details:data is " + data);
        var host_detail = $.parseJSON(data);
        callback(host_detail);
    });
}
