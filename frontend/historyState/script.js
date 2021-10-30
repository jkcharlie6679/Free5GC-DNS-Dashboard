$(document).ready(function () {
  initial();

  setInterval(myTimer, 300000);

  $("#searchBtn").click(function () {
    let startTime = $("#startTime").val();
    let endTime = $("#endTime").val();
    let cellId = $("#cellIdSelect").val();
    let iotId = $("#iotIdSelect").val();
    let urlParameter = "";
    if (cellId === "" && iotId != "") {
      urlParameter = `&iotId=${iotId}`;
    } else if (cellId != "" && iotId === "") {
      urlParameter = `&cellId=${cellId}`;
    } else if (cellId != "" && iotId != "") {
      urlParameter = `&cellId=${cellId}&iotId=${iotId}`;
    }

    pageHistory(
      `http://140.118.121.110/api/history?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00${urlParameter}`
    );
  });

  function myTimer() {
    getResource();
    getDeviceId();
  }

  function initial() {
    getResource();
    let startTime = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
    let endTime = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
    $("#startTime").val(startTime);
    $("#endTime").val(endTime);
    pageHistory(`http://140.118.121.110/api/history?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00`);
    getDeviceId();
  }

  function getDeviceId() {
    $.get("http://140.118.121.110/api/deviceId", function (data) {
      let dataHtml = `<option value="">Select IoT ID</option>`;
      for (i = 0; i < JSON.parse(data).deviceId.length; i++) {
        dataHtml += `<option value="${JSON.parse(data).deviceId[i]}">${JSON.parse(data).deviceId[i]}</option>`;
      }
      $("#iotIdSelect").html(dataHtml);
    });
  }

  function getResource() {
    $.get("http://140.118.121.110/api/resourceUsage", function (data) {
      $("#dnsIdOne").text(JSON.parse(data)[0].dnsId);
      $("#dnsCpuOne").text(JSON.parse(data)[0].cpuUsage + "%");
      $("#dnsMemoryOne").text(JSON.parse(data)[0].memoryUsage + "%");
      $("#dnsDiskOne").text(JSON.parse(data)[0].diskUsage + "%");
      $("#dnsIdTwo").text(JSON.parse(data)[1].dnsId);
      $("#dnsCpuTwo").text(JSON.parse(data)[1].cpuUsage + "%");
      $("#dnsMemoryTwo").text(JSON.parse(data)[1].memoryUsage + "%");
      $("#dnsDiskTwo").text(JSON.parse(data)[1].diskUsage + "%");
    });
  }

  function buildData(data) {
    let arrayData = [];

    let arrayTitle = Object.keys(data[0]);

    arrayData.push(arrayTitle);

    Array.prototype.forEach.call(data, (d) => {
      let items = [];
      Array.prototype.forEach.call(arrayTitle, (title) => {
        let item = d[title] || "None";
        items.push(item);
      });
      arrayData.push(items);
    });

    let csvContent = "";
    Array.prototype.forEach.call(arrayData, (d) => {
      let dataString = d.join(",") + "\n";
      csvContent += dataString;
    });

    let fileName = "Dashboard_History" + new Date().getTime() + ".csv";

    $("#download").attr("href", "data:text/csv;charset=utf-8,%EF%BB%BF" + encodeURI(csvContent));
    $("#download").attr("download", fileName);
  }

  function pageHistory(url) {
    $("#page").pagination({
      dataSource: function (done) {
        $.ajax({
          type: "GET",
          url: url,
          success: function (response) {
            if (JSON.parse(response).amount === 0) {
              done([0]);
            } else {
              done(JSON.parse(response).items);
              $("#download").css("display", "block");
              buildData(JSON.parse(response).items);
            }
          },
        });
      },
      pageSize: 20,
      className: "custom-paginationjs",
      callback: function (data, pagination) {
        let dataHtml = "";

        if (data[0] === 0) {
          dataHtml += `<tr><td colspan="14">No data</td></tr>`;
        } else {
          $.each(data, function (index, item) {
            index += 1;
            dataHtml += `
                                    <tr>
                                        <td>${index}</td>
                                        <td>${item.startTime}</td>
                                        <td>${item.endTime}</td>
                                        <td>${item.previous}</td>
                                        <td>${item.next}</td>
                                        <td>${item.dnsId}</td>
                                        <td>${item.domainId}</td>
                                        <td>${item.cellId}</td>
                                        <td>${item.deviceId}</td>
                                        <td>${item.imei}</td>
                                        <td>${item.ipv4}</td>
                                        <td>${item.ipv6}</td>
                                        <td>${item.sliceId}</td>
                                        <td>${item.fqdn}</td>
                                    </tr>`;
          });
        }
        $("#tbody").html(dataHtml);
      },
    });
  }
});
