
const cleanChartDates = function(data) {
    try {
        data.data.datasets.map(function(a) {
            a.data.forEach(function(value, index, array) {
                let dt = new Date(value["x"]);
                array[index]["x"] = dt;
            })
        })
    } catch(error) {
        console.log(error);
    }

    try {
        data.data.labels.forEach(function(value, index, array) {
            let dt = new Date(value);
            array[index] = dt;
        })
    } catch(error) {
        console.log(error);
    }

    return data;
}


const setChartOptions = function(data) {
    data.options['scales'] = {x: {display: false}};
    return data;
}


const buildModalChart = function(url) {
    // Chart.register(Colors);

    // destroy an existing chart before creating a new one on same canvas
    let c = Chart.getChart("myChart");
    if (c != undefined) { c.destroy(); }

    var content = m("canvas", {id: "myChart", style: {height: "60vh"}});
    showModal(content);

    return m.request({
        method: "GET",
        url: url,
        withCredentials: true,
    }).then(function(result) {
        let ctx = document.getElementById("myChart").getContext("2d");
        let data = setChartOptions(cleanChartDates(result.msg));
        let mychart = new Chart(ctx, data);
    })
}
