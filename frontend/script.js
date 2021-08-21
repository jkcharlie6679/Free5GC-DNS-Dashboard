$(document).ready(function () {
    initial();
    setInterval(myTimer, 10000);

    $("#cell_1_btn").click(function () {
        $("#Domain_ID").text("Domain 1");
        $("#Cell_ID").text("Cell 1");
        get_detail("Domain_1", "Cell_1");
    });

    $("#cell_2_btn").click(function () {
        $("#Domain_ID").text("Domain 1");
        $("#Cell_ID").text("Cell 2");
        get_detail("Domain_1", "Cell_2");
    });

    $("#cell_3_btn").click(function () {
        $("#Domain_ID").text("Domain 2");
        $("#Cell_ID").text("Cell 3");
        get_detail("Domain_2", "Cell_3");
    });

    function myTimer() {
        get_cell();
        get_resource();
    }

    function initial() {
        get_resource();
        get_detail("Domain_1", "Cell_1");
        get_cell();
    }

    function get_cell() {
        $.get(
            "http://140.118.121.110:5534/cell_amount",
            function (data, status) {
                $("#cell_1").text(JSON.parse(data).Cell_1);
                $("#cell_2").text(JSON.parse(data).Cell_2);
                $("#cell_3").text(JSON.parse(data).Cell_3);
            }
        );
    }

    function get_resource() {
        $.get(
            "http://140.118.121.110:5534/resource_usage",
            function (data, status) {
                $("#dns1_dns").text(JSON.parse(data)[0].DNS_ID);
                $("#dns1_cpu").text(JSON.parse(data)[0].CPU_Usage + "%");
                $("#dns1_mem").text(JSON.parse(data)[0].Memory_Usage + "%");
                $("#dns1_disk").text(JSON.parse(data)[0].Disk_Usage + "%");
                $("#dns2_dns").text(JSON.parse(data)[1].DNS_ID);
                $("#dns2_cpu").text(JSON.parse(data)[1].CPU_Usage + "%");
                $("#dns2_mem").text(JSON.parse(data)[1].Memory_Usage + "%");
                $("#dns2_disk").text(JSON.parse(data)[1].Disk_Usage + "%");
            }
        );
    }

    function get_detail(domain_id, cell_id) {
        var dataHtml = "";
        $.ajax({
            url:
                "http://140.118.121.110:5534/current?Domain_ID=" +
                domain_id +
                "&Cell_ID=" +
                cell_id,
            context: document.body,
        }).done(function (body) {
            $.each(JSON.parse(body).items, function (index, value) {
                dataHtml += `<div class="data">
                                <div class="img">
                                    <img src="./images/UE.png" alt="IoT Device">
                                </div>
                                <div class="info">
                                    <p id="index">
                                        index: ${index + 1}
                                    </p>
                                    <p id="online">
                                        online
                                    </p>
                                    <p id="Device_ID">
                                        Device_ID: ${value.Device_ID}
                                    </p>
                                    <p id="IPv4">
                                        IPv4: ${value.IPv4}
                                    </p>
                                    <p id="IPv6">
                                        IPv6: ${value.IPv6}
                                    </p>
                                    <p id="FQDN">
                                        FQDN: ${value.FQDN}
                                    </p>
                                </div>
                            </div>`;
            });
            $("#list").html(dataHtml);
        });
    }
});
