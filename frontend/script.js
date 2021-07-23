$(document).ready(function() {

    initial()
    setInterval(myTimer, 10000);

    function myTimer() {
        get_cell()
        get_resource()
    }

    function initial() {
        get_resource()
        get_detail()
        get_cell()
    }

    function get_cell() {
        $.get("http://127.0.0.1:5000/cell_amount", function(data, status) {
            $('#cell_1').text(JSON.parse(data).Cell_1)
            $('#cell_2').text(JSON.parse(data).Cell_2)
            $('#cell_3').text(JSON.parse(data).Cell_3)
        })
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

    function get_detail() {
        var dataHtml = '';
        $.ajax({
            url: "http://127.0.0.1:5000/current?Domain_ID=" + $("#Domain_ID").val() + "&Cell_ID=" + $("#Cell_ID").val(),
            context: document.body
        }).done(function(body) {

            $.each(JSON.parse(body).items, function(index, value) {
                dataHtml += `<div class="data">
                                <div class="img">
                                    <img src="./images/UE.png" alt="IoT Device">
                                </div>
                                <div class="info">
                                    <div id="index">
                                        index: ${index + 1}
                                    </div>
                                    <div id="online">
                                        online
                                    </div>
                                    <div id="Device_ID">
                                        Device_ID: ${value.Device_ID}
                                    </div>
                                    <div id="IPv4">
                                        IPv4: ${value.IPv4}
                                    </div>
                                    <div id="IPv6">
                                        IPv6: ${value.IPv6}
                                    </div>
                                    <div id="FQDN">
                                        FQDN: ${value.FQDN}
                                    </div>
                                </div>
                            </div>`
            })
            $("#list").html(dataHtml)
        })
    }
})