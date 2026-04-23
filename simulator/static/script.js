document.addEventListener('DOMContentLoaded', () => {
    const iaDist = document.getElementById('ia_dist');
    const sDist = document.getElementById('s_dist');
    const iaParamsContainer = document.getElementById('ia_params_container');
    const sParamsContainer = document.getElementById('s_params_container');
    const form = document.getElementById('sim-form');
    const btnText = form.querySelector('button span');
    const btnSpinner = document.getElementById('btn-spinner');
    const resultsSection = document.getElementById('results-section');
    const ganttImg = document.getElementById('gantt-img');
    const tableBody = document.querySelector('#results-table tbody');

    const distParams = {
        'exponential': [{ name: 'scale', label: 'Scale (Mean)', type: 'number', step: '0.1', default: 1.0 }],
        'normal': [
            { name: 'mean', label: 'Mean', type: 'number', step: '0.1', default: 10.0 },
            { name: 'std', label: 'Standard Deviation', type: 'number', step: '0.1', default: 2.0 }
        ],
        'uniform': [
            { name: 'low', label: 'Minimum', type: 'number', step: '0.1', default: 1.0 },
            { name: 'high', label: 'Maximum', type: 'number', step: '0.1', default: 10.0 }
        ],
        'gamma': [
            { name: 'shape', label: 'Shape', type: 'number', step: '0.1', default: 2.0 },
            { name: 'scale', label: 'Scale', type: 'number', step: '0.1', default: 1.0 }
        ]
    };

    function renderParams(distValue, container, prefix) {
        container.innerHTML = '';
        const params = distParams[distValue] || [];
        params.forEach(p => {
            const div = document.createElement('div');
            div.className = 'input-group';
            div.innerHTML = `
                <label for="${prefix}_${p.name}">${p.label}</label>
                <input type="${p.type}" id="${prefix}_${p.name}" name="${prefix}_${p.name}" step="${p.step}" value="${p.default}" required>
            `;
            container.appendChild(div);
        });
    }

    iaDist.addEventListener('change', (e) => renderParams(e.target.value, iaParamsContainer, 'ia'));
    sDist.addEventListener('change', (e) => renderParams(e.target.value, sParamsContainer, 's'));

    // Initial render
    renderParams(iaDist.value, iaParamsContainer, 'ia');
    renderParams(sDist.value, sParamsContainer, 's');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state
        btnText.style.display = 'none';
        btnSpinner.style.display = 'block';
        resultsSection.classList.add('hidden');
        document.querySelector('.submit-btn').disabled = true;

        // Collect parameters dynamically
        const requestData = {
            num_customers: document.getElementById('num_customers').value,
            num_servers: document.getElementById('num_servers').value,
            preemptive: document.getElementById('preemptive').value === 'true',
            inter_arrival_dist: iaDist.value,
            inter_arrival_params: {},
            service_dist: sDist.value,
            service_params: {}
        };

        distParams[iaDist.value].forEach(p => {
            requestData.inter_arrival_params[p.name] = document.getElementById(`ia_${p.name}`).value;
        });

        distParams[sDist.value].forEach(p => {
            requestData.service_params[p.name] = document.getElementById(`s_${p.name}`).value;
        });

        try {
            const response = await fetch('/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Render Gantt
                ganttImg.src = `data:image/png;base64,${data.gantt_chart}`;

                // Render metrics plotly
                if (data.metrics_json) {
                    const fig = JSON.parse(data.metrics_json);
                    Plotly.newPlot('metrics-plotly-container', fig.data, fig.layout, { responsive: true });
                }

                // Render Table
                tableBody.innerHTML = '';
                data.data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${row.Customer}</td>
                        <td>${row['Arrival Time'].toFixed(2)}</td>
                        <td>${row['Inter-arrival Time'].toFixed(2)}</td>
                        <td>${row['Service Time'].toFixed(2)}</td>
                        <td>${row['Service Start'].toFixed(2)}</td>
                        <td>${row['Service End'].toFixed(2)}</td>
                        <td>${row.Priority}</td>
                    `;
                    tableBody.appendChild(tr);
                });

                resultsSection.classList.remove('hidden');
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Simulation failed: ' + data.message);
            }
        } catch (err) {
            console.error(err);
            alert('Error connecting to the simulator backend.');
        } finally {
            btnText.style.display = 'block';
            btnSpinner.style.display = 'none';
            document.querySelector('.submit-btn').disabled = false;
        }
    });
});
