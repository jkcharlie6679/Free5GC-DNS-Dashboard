$(document).ready(function() {

    initial()

    setInterval(myTimer, 10000);

    $("#search-btn").click(function() {
        var Start_time = $("#Start_time").val();
        var End_time = $("#End_time").val();
        var Cell_ID = $("#Cell_ID_select").val();
        var url = "http://127.0.0.1:5000/history?Start_time=" + Start_time + "%2B00:00&End_time=" + End_time + "%2B00:00&Cell_ID=" + Cell_ID;

        page_history(url)
    })



    function myTimer() {
        get_resource()
    }

    function initial() {
        get_resource()
        var Start_time = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
        var End_time = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
        $("#Start_time").val(Start_time)
        $("#End_time").val(End_time)
        var url = "http://140.118.121.110:5534/history?Start_time=" + Start_time + "%2B00:00&End_time=" + End_time + "%2B00:00&Cell_ID=";

        page_history(url)
    }

    function get_resource() {
        $.get("http://140.118.121.110:5534/resource_usage", function(data, status) {
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

    function page_history(url) {
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
                $.each(data, function(index, item) {
                    index += 1;
                    dataHtml += '<tr><td>' + index + '</td>';
                    dataHtml += '<td>' + item.Start_time + '</td>';
                    dataHtml += '<td>' + item.End_time + '</td>';
                    dataHtml += '<td>' + item.DNS_ID + '</td>';
                    dataHtml += '<td>' + item.Domain_ID + '</td>';
                    dataHtml += '<td>' + item.Cell_ID + '</td>';
                    dataHtml += '<td>' + item.Device_ID + '</td>';
                    dataHtml += '<td>' + item.IMEI + '</td>';
                    dataHtml += '<td>' + item.IPv4 + '</td>';
                    dataHtml += '<td>' + item.IPv6 + '</td>';
                    dataHtml += '<td>' + item.FQDN + '</td></tr>';
                });
                $("#tbody").html(dataHtml)
            }
        })
    }

})