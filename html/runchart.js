
const cacheBuster = Math.random().toString(36).slice(2);
const url = `https://gist.githubusercontent.com/zhongkairen/584db1c30251ffee502796950b03f782/raw/run_history.csv?${cacheBuster}`;
const chartData = {
    timestamps: [],
    runNumbers: [],
    durations: [],
    versions: [],
    colors: [],
    statuses: [],
    types: []
};
const timeZone = 'Europe/Helsinki';
fetch(url)
    .then(response => response.text())
    .then(data => {
        parseData(data);
        // Update the chart with the fetched data
        currentCursor = Math.max(0, chartData.timestamps.length - itemsPerPage);
        updateChart(currentCursor);
    })
    .catch(error => console.error('Error fetching data:', error));

function formatTimestamp(datetime, style) {
    if (style === 'local')
        return datetime.toLocaleString('en-CA', {
            timeZone: timeZone,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
        }).replace(',', '');

    if (style === 'local-short')
        return datetime.toLocaleString('en-US', {
            timeZone: 'Europe/Helsinki',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        }).replace(',', '');

    if (style === 'utc')
        return datetime.toISOString();
    return datetime.toLocaleTimeString();
}

// Function to parse the data
function parseData(raw) {
    const lines = raw.trim().split('\n');
    lines.reverse(); // Reverse the order of the lines so that the latest runs are shown on the right
    lines.forEach(line => {
        // '2024-10-18T21:43:46Z,46,workflow_dispatch,success,31s,v0.2.0'
        const [timestamp, runNumber, runType, status, duration, version] = line.trim().split(',');
        const durationNum = parseFloat(duration) || 0;

        const color = (() => {
            if (status !== 'success') {
                return 'rgba(255, 99, 132, 0.5)'; // Red for failed runs
            } else if (runType === 'workflow_dispatch') {
                return 'rgba(54, 162, 235, 0.5)'; // Blue for manual runs
            }
            return 'rgba(75, 192, 192, 0.5)'; // Teal for successful scheduled runs
        })();

        // Add status if status is not success
        const statusText = (status === 'success' ? '✅' : '⚠️') + status;

        chartData.timestamps.push(new Date(timestamp));
        chartData.runNumbers.push(runNumber);
        chartData.durations.push(durationNum);
        chartData.versions.push(version); // Collect versions
        chartData.types.push(runType);
        chartData.colors.push(color);
        chartData.statuses.push(statusText);
    });
}
// Pagination variables
let currentCursor = 0;
const itemsPerPage = 24; // Number of items to display per page

function updateChart(cursor) {
    const totalItems = chartData.timestamps.length;
    const start = cursor;
    const end = start + itemsPerPage;

    // Update the chart data
    myChart.data.labels = chartData.timestamps.slice(start, end).map(timestamp => formatTimestamp(timestamp, 'local-short'));
    myChart.data.datasets[0].data = chartData.durations.slice(start, end);

    // Update the background colors for the current page
    myChart.data.datasets[0].backgroundColor = chartData.colors.slice(start, end);
    myChart.data.datasets[0].borderColor = chartData.colors.slice(start, end).map(color => color.replace(/0\.5/, '1')); // Full opacity for borders

    myChart.update();

    // Update button states
    document.getElementById('prevBtn').disabled = start === 0;
    document.getElementById('nextBtn').disabled = end >= totalItems;
}

// Create the chart
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar', // Change this to 'line' or 'bar' as needed
    data: {
        labels: [], // Initially empty; will be filled on chart update
        datasets: [{
            label: `Duration (seconds) - Time (${timeZone})`,
            data: [],
            backgroundColor: chartData.colors,
            borderColor: chartData.colors.map(color => color.replace(/0\.5/, '1')), // Full opacity for borders
            borderWidth: 1,
            hoverBackgroundColor: 'rgba(255, 206, 86, 0.2)',
            hoverBorderColor: 'rgba(255, 206, 86, 1)'
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                ticks: {
                    color: function (context) {
                        const index = currentCursor + context.index;
                        const timestamp = chartData.timestamps[index];
                        const isWeekend = timestamp.getDay() === 0 || timestamp.getDay() === 6;
                        return isWeekend ? 'red' : Chart.defaults.color;
                    }
                }
            },
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (tooltipItem) {
                        const index = currentCursor + tooltipItem.dataIndex;
                        const runNumber = chartData.runNumbers[index];
                        const status = chartData.statuses[index];
                        const type = chartData.types[index];
                        return [`Run number: ${runNumber}`, `Duration: ${tooltipItem.raw} seconds`, `Type: ${type}`, `Status: ${status}`];
                    }
                    ,
                    title: function (tooltipItem) {
                        const index = currentCursor + tooltipItem[0].dataIndex;
                        const timestamp = chartData.timestamps[index]; // Show date/time on hover
                        return formatTimestamp(timestamp, 'local');
                    }
                }
            }
        }
    }
});

// Initial chart update
updateChart(currentCursor);

// Pagination button event listeners
document.getElementById('prevBtn').addEventListener('click', function () {
    if (currentCursor > 0) {
        currentCursor -= itemsPerPage;
        if (currentCursor < 0) {
            currentCursor = 0;
        }
        updateChart(currentCursor);
    }
});

document.getElementById('nextBtn').addEventListener('click', function () {
    if (currentCursor + itemsPerPage < chartData.timestamps.length) {
        currentCursor += itemsPerPage;
        if (currentCursor >= chartData.timestamps.length - itemsPerPage) {
            currentCursor = chartData.timestamps.length - itemsPerPage;
        }
        updateChart(currentCursor);
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft') {
        // Simulate clicking the Previous button
        document.getElementById('prevBtn').click();
    } else if (event.key === 'ArrowRight') {
        // Simulate clicking the Next button
        document.getElementById('nextBtn').click();
    }
});
