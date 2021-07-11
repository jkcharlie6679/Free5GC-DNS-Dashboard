$(document).ready(function(){
    $("#btn_DNS_Call_Flow").css("background-color", "#c6d9f0")
    $("#btn_DNS_Call_Flow").click(function(){
        $("#btn_DNS_Call_Flow").css("background-color", "#c6d9f0")
        $("#btn_System_Log").css("background-color", "#fff")

    })
    $("#btn_System_Log").click(function(){
        $("#btn_System_Log").css("background-color", "#c6d9f0")
        $("#btn_DNS_Call_Flow").css("background-color", "#fff")

    })
})