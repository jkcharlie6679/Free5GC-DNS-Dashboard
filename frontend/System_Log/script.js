$(document).ready(function() {
    var tab = 'Call_Flow'
    initial()
    setInterval(myTimer, 10000);

    $("#btn_DNS_Call_Flow").css("background-color", "#c6d9f0")
    $("#btn_DNS_Call_Flow").click(function() {
        tab = "Call_Flow"
        $("#btn_DNS_Call_Flow").css("background-color", "#c6d9f0")
        $("#btn_System_Log").css("background-color", "#fff")
        $("#thead").html(`<tr>
                            <th>Index</th>
                            <th>Type</th>
                            <th>Time</th>
                            <th>Payload</th>
                        </tr>`)
        var Start_time = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
        var End_time = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
        $("#Start_time").val(Start_time)
        $("#End_time").val(End_time)
        var url = "http://127.0.0.1:5000/call_flow_log?Start_time=" + Start_time + "%2B00:00&End_time=" + End_time + "%2B00:00";
        page_call_flow(url)
    })

    $("#btn_System_Log").click(function() {
        tab = "System_Log"
        $("#btn_System_Log").css("background-color", "#c6d9f0")
        $("#btn_DNS_Call_Flow").css("background-color", "#fff")
        $("#thead").html(`<tr>
                            <th>Index</th>
                            <th>Time</th>
                            <th>DNS_env_info</th>
                            <th>CPU_Usage</th>
                            <th>Memory_Usage</th>
                            <th>Disk_Usage</th>
                        </tr>`)

        var Start_time = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
        var End_time = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
        $("#Start_time").val(Start_time)
        $("#End_time").val(End_time)
        var url = "http://127.0.0.1:5000/system_log?Start_time=" + Start_time + "%2B00:00&End_time=" + End_time + "%2B00:00";
        page_system_log(url)
    })

    $("#search-btn").click(function() {
        var Start_time = $("#Start_time").val();
        var End_time = $("#End_time").val();
        if (tab == "Call_Flow") {
            url = "http://127.0.0.1:5000/call_flow_log?Start_time=" + Start_time + "%2B08:00&End_time=" + End_time + "%2B08:00";
            page_call_flow(url);
        } else if (tab == "System_Log") {
            url = "http://127.0.0.1:5000/system_log?Start_time=" + Start_time + "%2B08:00&End_time=" + End_time + "%2B08:00";
            page_system_log(url);
        }

    })

    function myTimer() {
        get_resource()
    }

    function initial() {
        get_resource()
        $("#thead").html(`<tr>
                        <th>Index</th>
                        <th>Type</th>
                        <th>Time</th>
                        <th>Payload</th>
                    </tr>`)
        var Start_time = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
        var End_time = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
        $("#Start_time").val(Start_time)
        $("#End_time").val(End_time)
        var url = "http://127.0.0.1:5000/call_flow_log?Start_time=" + Start_time + "%2B08:00&End_time=" + End_time + "%2B08:00";
        page_call_flow(url)
    }

    function get_resource() {
        $.get("http://127.0.0.1:5000/resource_usage", function(data, status) {
            $('#dns1_dns').text(JSON.parse(data)[0].DNS_ID)
            $('#dns1_cpu').text(JSON.parse(data)[0].CPU_Usage + "%")
            $('#dns1_mem').text(JSON.parse(data)[0].Memory_Usage + "%")
            $('#dns1_disk').text(JSON.parse(data)[0].Disk_Usage + "%")
            $('#dns2_dns').text(JSON.parse(data)[1].DNS_ID)
            $('#dns2_cpu').text(JSON.parse(data)[1].CPU_Usage + "%")
            $('#dns2_mem').text(JSON.parse(data)[1].Memory_Usage + "%")
            $('#dns2_disk').text(JSON.parse(data)[1].Disk_Usage + "%")
        })
    }

    function page_call_flow(url) {
        $('#page').pagination({
            dataSource: function(done) {
                $.ajax({
                    type: "GET",
                    url: url,
                    // beforesend: $("#tbody").html('Loading'),
                    success: function(response) {
                        done(JSON.parse(response).items);
                    }
                })
            },
            pageSize: 20,
            className: "custom-paginationjs",
            callback: function(data, pagination) {
                var dataHtml = '';
                var pageStart = (pagination.pageNumber - 1) * pagination.pageSize;
                var pageEnd = pageStart + pagination.pageSize;
                var pageItems = data.slice(pageStart, pageEnd);
                $.each(pageItems, function(index, item) {
                    index += 1;
                    dataHtml += '<tr><td>' + index + '</td>';
                    dataHtml += '<td>' + item.Type + '</td>';
                    dataHtml += '<td>' + item.Datetime + '</td>';
                    dataHtml += '<td>' + item.Payload + '</td></tr>';
                });
                $("#tbody").html(dataHtml)
            }
        })
    }

    function page_system_log(url) {
        $('#page').pagination({
            dataSource: function(done) {
                $.ajax({
                    type: "GET",
                    url: url,
                    success: function(response) {
                        done(JSON.parse(response).items);
                    }
                })
            },
            pageSize: 20,
            className: "custom-paginationjs",
            callback: function(data, pagination) {
                var dataHtml = '';
                var pageStart = (pagination.pageNumber - 1) * pagination.pageSize;
                var pageEnd = pageStart + pagination.pageSize;
                var pageItems = data.slice(pageStart, pageEnd);
                $.each(pageItems, function(index, item) {
                    index += 1;
                    dataHtml += '<tr><td>' + index + '</td>';
                    dataHtml += '<td>' + item.Datetime + '</td>';
                    dataHtml += '<td>' + item.DNS_env_info + '</td>';
                    dataHtml += '<td>' + item.CPU_Usage + '</td>';
                    dataHtml += '<td>' + item.Memory_Usage + '</td>';
                    dataHtml += '<td>' + item.Disk_Usage + '</td></tr>';
                });
                $("#tbody").html(dataHtml)
            }
        })
    }
})