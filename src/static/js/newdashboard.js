console.log("starting new dashboard");

function handle_update(hosts){
    /*console.log(hosts);*/
    for( x in hosts){
        get_details(hosts[x], handle_update_containers);
    }
}

function handle_update_containers(host, containers){
    /*console.log(containers);*/
    for( x in containers){
        var cont_stat = containers[x]["Status"];
        var cont_name = containers[x]["Names"][0];
        cont_name = cont_name.substring(1,cont_name.length);

        //locate status span and buttons
        var span_target = "span#status-"+ host + "-" + cont_name;
        var span_stat = $(span_target);
        var start_button = $("#start-" + host + "-" + cont_name);
        var stop_button = $("#stop-" + host + "-"+  cont_name);

        //update status and buttons
        span_stat.text(cont_stat);
        if( cont_stat.split(" ")[0] == "Up" ){
            stop_button.removeClass("disabled");
            start_button.addClass("disabled");
        }else{
            start_button.removeClass("disabled");
            stop_button.addClass("disabled");
        }

    }
}

function update(){
    get_hosts(handle_update);
}

$("button.control").click(function(){
    if(!$(this).is(".disabled")){
        $(this).addClass("disabled");
        var info = this.id.split("-");
        var action = info[0];
        var host = info[1];
        var container = info[2];
        $.post("../hosts/"+host+"/containers/"+container,
            { action:action},
            function( data){
        });
    }
});

$("button.masscontrol").click(function(){
    var action = this.id;
    var instances = new Object();
    $(".dockercontainer:not(.hidden)").each(function(index, element){
        var hostname = $(element).find(".hostname").text();
        var cname = $(element).find(".cname").text();
        if( instances[hostname] == undefined){
            instances[hostname] = new Array();
        }
        instances[hostname][instances[hostname].length] = cname;
    });
    /*console.log("going to post");*/
    $.post("../massaction",
        { action:action,
          instances:JSON.stringify(instances)},
        function( data){
    });
    /*console.log("done posting");*/
});

$("#filter").keyup(function(){
    var data = $(this).val();
    /*console.log("filter is " + data);*/
    $(".dockercontainer").each(function(index, element){
        var cur_name = $(element).find(".cname").text()
        var cur_env =  $(element).find(".cenv").text()
        if(cur_name.indexOf(data) == -1 && cur_env.indexOf(data) == -1){
            $(element).addClass("hidden");
        }else{
            $(element).removeClass("hidden");
        }
    });
});
//do first update to set buttons
update();

/*now connect to the update socket to start pulling in updates*/
var updatesocket = new WebSocket(updateserver);

updatesocket.onopen = function(){
    console.log("websocket to "  + updateserver);
}


updatesocket.onmessage = function(msg){
    var data = JSON.parse(msg.data);
    if( data["message_type"] == "update" ){
        handle_update_containers(data["host"], data["containers"]);
    }else{
        console.log(data["body"]);
    }
}

updatesocket.onclose = function(){
    this.updatesocket = new WebSocket(updatesocket.url);
}
updatesocket.onerror = function(){
    this.updatesocket = new WebSocket(updatesocket.url);
}
