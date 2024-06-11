document.addEventListener('DOMContentLoaded', () => {
    const measureButton = document.getElementById('measure-button');
    const resultDiv = document.getElementById('result');
    const treeImagesDiv = document.getElementById('tree-images');

    measureButton.addEventListener('click', async () => {
        const javaCode = document.getElementById('code-input').value;
        
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ java_code: javaCode })
        });

        const result = await response.json();
        //document.getElementById('receivedCode').textContent = result.java_code;
        //document.getElementById('output').textContent = result.output;
        document.getElementById('modifying-code').value = javaCode;
        document.getElementById('modified-code').value = result.fixed_code;
        const originalExecutionTime = result.execution_time;
        const modifiedExecutionTime = result.fixed_execution_time;
        const originalMemoryUsage = result.memory_usage;
        const modifiedMemoryUsage = result.fixed_memory_usage;
        const originalCarbonEmissions = result.carbon_emissions;
        const modifiedCarbonEmissions = result.fixed_carbon_emissions;

        // Update the comparison table
        updateComparisonTable({
            originalExecutionTime,
            modifiedExecutionTime,
            originalMemoryUsage,
            modifiedMemoryUsage,
            originalCarbonEmissions,
            modifiedCarbonEmissions
        });

        // Placeholder for actual carbon emission calculation logic
        // For this example, let's assume we calculate emissions based on the length of the code
        const emission = calculateCarbonEmission(codeInput);
        // Display the result
        resultDiv.textContent = `Carbon Emission: ${emission.toFixed(2)} g CO2`;
        // Update tree images based on the emission value
        updateTreeImages(emission);

    });

    function calculateCarbonEmission(code) {
        // Simple placeholder calculation (to be replaced with actual logic)

        return 3;
    }

    function updateTreeImages(emission) {
        treeImagesDiv.innerHTML = ''; // Clear previous images

        let treeCount = 0;
        if (emission < 1) {
            treeCount = 1;
        } else if (emission < 3) {
            treeCount = 2;
        } else {
            treeCount = 3;
        }

        for (let i = 0; i < treeCount; i++) {
            const img = document.createElement('img');
            img.src = '/code/static/images/tree.png';
            img.alt = 'Tree';
            img.style.width = '100px';
            img.style.height = '100px';
            img.style.marginRight = '10px';
            treeImagesDiv.appendChild(img);
        }
    }

    function updateComparisonTable(data) {
        document.getElementById('original-execution-time').textContent = `${data.originalExecutionTime} ms`;
        document.getElementById('modified-execution-time').textContent = `${data.modifiedExecutionTime} ms`;
        document.getElementById('improvement-execution-time').textContent = `${((data.originalExecutionTime - data.modifiedExecutionTime) / data.originalExecutionTime * 100).toFixed(2)} %`;

        document.getElementById('original-memory-usage').textContent = `${data.originalMemoryUsage} MB`;
        document.getElementById('modified-memory-usage').textContent = `${data.modifiedMemoryUsage} MB`;
        document.getElementById('improvement-memory-usage').textContent = `${((data.originalMemoryUsage - data.modifiedMemoryUsage) / data.originalMemoryUsage * 100).toFixed(2)} %`;

        document.getElementById('original-carbon-emissions').textContent = `${data.originalCarbonEmissions} g CO2`;
        document.getElementById('modified-carbon-emissions').textContent = `${data.modifiedCarbonEmissions} g CO2`;
        document.getElementById('improvement-carbon-emissions').textContent = `${((data.originalCarbonEmissions - data.modifiedCarbonEmissions) / data.originalCarbonEmissions * 100).toFixed(2)} %`;
    }
});