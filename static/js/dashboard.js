get_hosts(function(hosts){
    console.log("dashboard: " + hosts);
    var hosts_div = $(".hosts");
    for( x in hosts ){
        var new_div = $("<div class='host_div' id='" + hosts[x] +"'></div>");
        var new_span = $("<span class='host_name'>"+hosts[x]+"</span>");
        var new_containers = $("<div class='containers' id='"+hosts[x]+"'></div>");
        new_span.appendTo(new_div);
        new_containers.appendTo(new_div);
        new_div.appendTo(hosts_div);
        get_details(hosts[x], function(details){
            console.log("dashboar: " + details);
            for(x in details){
                console.log("details[x]"+x);
                var containers = $(".containers#"+hosts[x]);
                var new_contain = $("<div class='container'></div>");
                new_contain.append("<span 'container_detail'>" + details[x]["Names"][0] + "</span>");
                new_contain.append("<span 'container_detail'>" + details[x]["Status"] + "</span>");
                new_contain.append("<span 'container_detail'>" + details[x]["Command"] + "</span>");
                new_contain.appendTo(containers);
            }
        });
    }
});
