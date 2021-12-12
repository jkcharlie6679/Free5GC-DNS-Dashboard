$(document).ready(function () {
  var tab = 'callFlow';
  initial();
  setInterval(myTimer, 300000);

  $('#callFlowBtn').css('background-color', '#c6d9f0');
  $('#callFlowBtn').click(function () {
    $('#download').css('display', 'none');
    tab = 'callFlow';
    $('#callFlowBtn').css('background-color', '#c6d9f0');
    $('#systemLogBtn').css('background-color', '#fff');
    $('#thead').html(
      `<tr>
        <th>Index</th>
        <th>Type</th>
        <th>Time</th>
        <th>Payload</th>
      </tr>`
    );
    let startTime = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
    let endTime = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
    $('#startTime').val(startTime);
    $('#endTime').val(endTime);
    callFlowPage(`http://${apiEndpoint}/api/callFlowLog?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00`);
  });

  $('#systemLogBtn').click(function () {
    $('#download').css('display', 'none');
    tab = 'systemLog';
    $('#systemLogBtn').css('background-color', '#c6d9f0');
    $('#callFlowBtn').css('background-color', '#fff');
    $('#thead').html(
      `<tr>
        <th>Index</th>
        <th>Time</th>
        <th>DNS_ID</th>
        <th>DNS_env_info</th>
        <th>CPU_Usage</th>
        <th>Memory_Usage</th>
        <th>Disk_Usage</th>
      </tr>`
    );

    let startTime = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
    let endTime = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
    $('#startTime').val(startTime);
    $('#endTime').val(endTime);
    systemLogpage(`http://${apiEndpoint}/api/systemLog?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00`);
  });

  $('#searchBtn').click(function () {
    let startTime = $('#startTime').val();
    let endTime = $('#endTime').val();
    if (tab == 'callFlow') {
      callFlowPage(`http://${apiEndpoint}/api/callFlowLog?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00`);
    } else if (tab == 'systemLog') {
      systemLogpage(`http://${apiEndpoint}/api/systemLog?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00`);
    }
  });

  function myTimer() {
    getResource();
  }

  function initial() {
    getResource();
    $('#thead').html(
      `<tr>
        <th>Index</th>
        <th>Type</th>
        <th>Time</th>
        <th>Payload</th>
      </tr>`
    );
    let startTime = new Date(Date.now() - 16 * 3600000).toISOString().substr(0, 16);
    let endTime = new Date(Date.now() + 8 * 3600000).toISOString().substr(0, 16);
    $('#startTime').val(startTime);
    $('#endTime').val(endTime);
    callFlowPage(`http://${apiEndpoint}/api/callFlowLog?startTime=${startTime}%2B08:00&endTime=${endTime}%2B08:00`);
  }

  function getResource() {
    $.get(`http://${apiEndpoint}/api/resourceUsage`, function (data) {
      $('#dnsIdOne').text(JSON.parse(data)[0].dnsId);
      $('#dnsCpuOne').text(JSON.parse(data)[0].cpuUsage + '%');
      $('#dnsMemoryOne').text(JSON.parse(data)[0].memoryUsage + '%');
      $('#dnsDiskOne').text(JSON.parse(data)[0].diskUsage + '%');
      $('#dnsIdTwo').text(JSON.parse(data)[1].dnsId);
      $('#dnsCpuTwo').text(JSON.parse(data)[1].cpuUsage + '%');
      $('#dnsMemoryTwo').text(JSON.parse(data)[1].memoryUsage + '%');
      $('#dnsDiskTwo').text(JSON.parse(data)[1].diskUsage + '%');
    });
  }

  function callFlowPage(url) {
    $('#page').pagination({
      dataSource: function (done) {
        $.ajax({
          type: 'GET',
          url: url,
          success: function (response) {
            if (JSON.parse(response).amount === 0) {
              done([0]);
            } else {
              done(JSON.parse(response).items);
              $('#download').css('display', 'block');
              buildData('CallFlow', JSON.parse(response).items);
            }
          },
        });
      },
      pageSize: 20,
      className: 'custom-paginationjs',
      callback: function (data, pagination) {
        let dataHtml = '';
        if (data[0] === 0) {
          dataHtml += `<tr><td colspan="4">No data</td></tr>`;
        } else {
          $.each(data, function (index, item) {
            index += 1;
            dataHtml += `<tr>
              <td>${index}</td>
              <td>${item.type}</td>
              <td>${item.datetime}</td>
              <td>${item.payload}</td>
            </tr>`;
          });
        }
        $('#tbody').html(dataHtml);
      },
    });
  }
  function buildData(type, data) {
    let arrayData = [];

    let arrayTitle = Object.keys(data[0]);

    arrayData.push(arrayTitle);

    Array.prototype.forEach.call(data, (d) => {
      let items = [];
      Array.prototype.forEach.call(arrayTitle, (title) => {
        let item = d[title] || 'None';
        items.push(item);
      });
      arrayData.push(items);
    });

    let csvContent = '';
    Array.prototype.forEach.call(arrayData, (d) => {
      let dataString = d.join(',') + '\n';
      csvContent += dataString;
    });

    let fileName = 'Dashboard_' + type + new Date().getTime() + '.csv';

    $('#download').attr('href', 'data:text/csv;charset=utf-8,%EF%BB%BF' + encodeURI(csvContent));
    $('#download').attr('download', fileName);
  }

  function systemLogpage(url) {
    $('#page').pagination({
      dataSource: function (done) {
        $.ajax({
          type: 'GET',
          url: url,
          success: function (response) {
            if (JSON.parse(response).amount === 0) {
              done([0]);
            } else {
              done(JSON.parse(response).items);
              $('#download').css('display', 'block');
              buildData('SystemLog', JSON.parse(response).items);
            }
          },
        });
      },
      pageSize: 20,
      className: 'custom-paginationjs',
      callback: function (data, pagination) {
        let dataHtml = '';
        if (data[0] === 0) {
          dataHtml += `<tr><td colspan="7">No data</td></tr>`;
        } else {
          $.each(data, function (index, item) {
            index += 1;
            dataHtml += `<tr>
              <td>${index}</td>
              <td>${item.datetime}</td>
              <td>${item.dnsId}</td>
              <td>${item.dnsEnvInfo}</td>
              <td>${item.cpuUsage}</td>
              <td>${item.memoryUsage}</td>
              <td>${item.diskUsage}</td>
            </tr>`;
          });
        }
        $('#tbody').html(dataHtml);
      },
    });
  }
});
