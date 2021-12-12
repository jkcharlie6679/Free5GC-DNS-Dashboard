$(document).ready(function () {
  initial();
  setInterval(myTimer, 300000);

  $('#cellOneBtn').click(function () {
    $('#domainId').text('Domain 1');
    $('#cellId').text('Cell 1');
    getDetail('Domain_1', 'Cell_1');
  });

  $('#cellTwoBtn').click(function () {
    $('#domainId').text('Domain 1');
    $('#cellId').text('Cell 2');
    getDetail('Domain_1', 'Cell_2');
  });

  $('#cellThreeBtn').click(function () {
    $('#domainId').text('Domain 2');
    $('#cellId').text('Cell 3');
    getDetail('Domain_2', 'Cell_3');
  });

  function myTimer() {
    getCell();
    getResource();
  }

  function initial() {
    getResource();
    getDetail('Domain_1', 'Cell_1');
    getCell();
  }

  function getCell() {
    $.get(`http://${apiEndpoint}/api/cellAmount`, function (data) {
      $('#cellOne').text(JSON.parse(data).cellOne);
      $('#cellTwo').text(JSON.parse(data).cellTwo);
      $('#cellThree').text(JSON.parse(data).cellThree);
    });
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

  function getDetail(domainId, cellId) {
    var dataHtml = '';
    $.ajax({
      url: `http://${apiEndpoint}/api/current?domainId=${domainId}&cellId=${cellId}`,
      context: document.body,
    }).done(function (body) {
      if (JSON.parse(body).amount === 0) {
        dataHtml += `<div class="iotData">
                      <div class="img">
                        <img src="./images/IoT.png" alt="IoT Device">
                      </div>
                      <div class="info">
                        <p>index: </p>
                        <p>offline</p>
                        <p>Device ID: </p>
                        <p>IMEI: </p>
                        <p>IPv4: </p>
                        <p>IPv6: </p>
                        <p>Slice ID: </p>
                        <p>FQDN: </p>
                      </div>
                    </div>`;
      } else {
        $.each(JSON.parse(body).items, function (index, value) {
          dataHtml += `<div class="iotData">
                        <div class="img">
                          <img src="./images/IoT.png" alt="IoT Device">
                          </div>
                            <div class="info">
                              <p>
                                  index: ${index + 1}
                              </p>
                              <p style="color: green">
                                  online
                              </p>
                              <p>
                                  Device ID: ${value.deviceId}
                              </p>
                              <p>
                                  IMEI: ${value.imei}
                              </p>
                              <p>
                                  IPv4: ${value.ipv4}
                              </p>
                              <p>
                                  IPv6: ${value.ipv6}
                              </p>
                              <p>
                                  Slice ID: ${value.sliceId}
                              </p>
                              <p>
                                  FQDN: ${value.fqdn}
                              </p>
                          </div>
                        </div>`;
        });
      }

      $('#list').html(dataHtml);
    });
  }
});
