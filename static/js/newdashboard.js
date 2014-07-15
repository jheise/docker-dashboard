console.log("starting new dashboard");

function handle_update(hosts){
    console.log(hosts);
    for( x in hosts){
        get_details(hosts[x], handle_update_containers);
    }
}

function handle_update_containers(host, containers){
    console.log(containers);
    for( x in containers){
        var cont_stat = containers[x]["Status"];
        var cont_name = containers[x]["Names"][0];
        cont_name = cont_name.substring(1,cont_name.length);

        //locate status span and buttons
        //#localhost-suspicious_poincare-status
        var span_target = "span#status-"+ host + "-" + cont_name;
        console.log("looking for span "+span_target+"EOL");
        var span_stat = $(span_target);
        var start_button = $("#start-" + host + "-" + cont_name);
        var stop_button = $("#stop-" + host + "-"+  cont_name);

        //update status and buttons
        span_stat.text(cont_stat);
        console.log("going to print span id");
        console.log("span_stat is" + span_stat);
        console.log("span_stat id is " + span_stat.id);
        console.log("span_stat text is " + span_stat.text());
        console.log("prited span id");
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
    console.log("updating all docker hosts");
    get_hosts(handle_update);
}

$("button.control").click(function(){
    if(!$(this).is(".disabled")){
        $(this).addClass("disabled");
        var info = this.id.split("-");
        var action = info[0];
        var host = info[1];
        var container = info[2];
        console.log("button for "+action + " " +host+" "+container);
        $.post("../hosts/"+host+"/containers/"+container,
            { action:action},
            function( data){
            console.log("got back" + data);
        });
    }
});

update();
/*var foundcount = 0;*/
/*var spans = $("span#status-glados-defcoin");*/
/*for( x in spans){*/
/*if( spans[x].id == "status-glados-defcoin"){*/
/*foundcount++;*/
/*console.log("found the goddamn span");*/
/*console.log("span id is " + spans[x].id);*/
/*console.log("found count" + foundcount);*/
/*}*/
/**//*var testval = $(spans[x].id);*/
/**//*console.log( testval);*/
/*}*/

setInterval(update, 15000);
