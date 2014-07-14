function add_containers(host, details){
    for(x in details){
        //get name for container
        var cont_name = details[x]["Names"][0];
        cont_name = cont_name.substring(1,cont_name.length);
        //get status of container
        var cont_status = details[x]["Status"].split(" ");
        var containers = $(".containers#"+host);
        var new_contain = $("<div class='container'></div>");
        new_contain.append("<span 'container_name'><h3>" + cont_name + "</h3></span>");
        var new_table = $("<table class='table table-striped table-hover'></table>");
        new_table.append("<thead><tr><th>Status</th><th>Command</th><th>Control</th></tr></thead>");
        new_table.appendTo(new_contain);
        var table_body = $("<tbody></tbody>");
        var table_row = $("<tr></tr>");
        table_row.append("<th><span 'container_detail'>" + details[x]["Status"] + "</span></th>");
        table_row.append("<th><span 'container_detail'>" + details[x]["Command"] + "</span></th>");
        var commands = $("<th></th>");
        var start_button = $("<button type='button' class='btn btn-success disabled' id='start|"+host+"|"+cont_name+"'>Start</button>");
        var stop_button = $("<button type='button' class='btn btn-danger disabled' id='stop|"+host+"|"+cont_name+"'>Stop</button>");
        start_button.appendTo(commands);
        stop_button.appendTo(commands);
        commands.appendTo(table_row);
        table_row.appendTo(table_body);
        table_body.appendTo(new_table);

        new_contain.append("</table>");
        if(cont_status[0] == "Up"){
            stop_button.removeClass("disabled");
        } else {
            start_button.removeClass("disabled");
        }
        new_contain.appendTo(containers);

        //setup button actions
        console.log("adding click action for " + host + " " + cont_name);
        start_button.click(function(){
            if(!$(this).is(".disabled")){
                $(this).addClass("disabled");
                var info = this.id.split("|");
                var action = info[0];
                var host = info[1];
                var container = info[2];
                console.log("stop button for "+action + " " +host+" "+container);
                $.post("../hosts/"+host+"/containers/"+container,
                    { action:"start"},
                    function( data){
                    console.log("got back" + data);
                    });
            }
        });

        stop_button.click(function(){
            if(!$(this).is(".disabled")){
                $(this).addClass("disabled");
                var info = this.id.split("|");
                var action = info[0];
                var host = info[1];
                var container = info[2];
                console.log("stop button for "+action + " " +host+" "+container);
                $.post("../hosts/"+host+"/containers/"+container,
                    { action:"stop"},
                    function( data){
                    console.log("got back" + data);
                    });
            }
        });

    }
}

get_hosts(function(hosts){
    console.log("dashboard: " + hosts);
    var hosts_div = $(".hosts");
    for( x in hosts ){
        var new_div = $("<div class='host_div' id='" + hosts[x] +"'></div>");
        var new_span = $("<span class='host_name'><h2>"+hosts[x]+"</h2></span>");
        var new_containers = $("<div class='containers' id='"+hosts[x]+"'></div>");
        new_span.appendTo(new_div);
        new_containers.appendTo(new_div);
        new_div.appendTo(hosts_div);
        get_details(hosts[x], add_containers);
    }
});

function updateTime(){
    console.log("updating");
}

setInterval(updateTime, 30000);
