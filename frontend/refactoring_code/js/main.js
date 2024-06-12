document.addEventListener('DOMContentLoaded', () => {
    const measureButton = document.getElementById('measure-button');
    const treeImagesDiv = document.getElementById('tree-images');
    const errorMessageDiv = document.getElementById('error-message');

    // CodeMirror 인스턴스 초기화
    const codeInput = CodeMirror.fromTextArea(document.getElementById('code-input'), {
        lineNumbers: true,
        mode: 'text/x-java',
        
        matchBrackets: true,
        autoCloseBrackets: true
    });

    const modifyingCode = CodeMirror.fromTextArea(document.getElementById('modifying-code'), {
        lineNumbers: true,
        mode: 'text/x-java',
        
        readOnly: true,
        matchBrackets: true,
        autoCloseBrackets: true
    });

    const modifiedCode = CodeMirror.fromTextArea(document.getElementById('modified-code'), {
        lineNumbers: true,
        mode: 'text/x-java',
        
        readOnly: true,
        matchBrackets: true,
        autoCloseBrackets: true
    });

    measureButton.addEventListener('click', async () => {
        const javaCode = codeInput.getValue();
        
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ java_code: javaCode })
        });

        const result = await response.json();

        if (result.error_code) {
            // error_code가 있으면 오류 메시지를 표시
            errorMessageDiv.textContent = "Please enter valid code. Check the Modified Code Section.";
            errorMessageDiv.style.display = 'block';
            modifiedCode.setValue(result.fixed_code);
            return;
        } else {
            // error_code가 없으면 오류 메시지를 숨김
            errorMessageDiv.style.display = 'none';
            modifiedCode.setValue(result.fixed_code);
            modifyingCode.setValue(javaCode);
            const originalExecutionTime = result.execution_time;
            const modifiedExecutionTime = result.fixed_execution_time;
            const originalMemoryUsage = result.memory_usage;
            const modifiedMemoryUsage = result.fixed_memory_usage;
            const originalCarbonEmissions = result.carbon_emissions;
             modifiedCarbonEmissions = result.fixed_carbon_emissions;

            // Update the comparison table
            updateComparisonTable({
                originalExecutionTime,
                modifiedExecutionTime,
                originalMemoryUsage,
                modifiedMemoryUsage,
                originalCarbonEmissions,
                modifiedCarbonEmissions
            });
        }

    
        


        

        // Placeholder for actual carbon emission calculation logic
        // For this example, let's assume we calculate emissions based on the length of the code
        /*const emission = result.carbon_emissions;
        // Display the result
        resultDiv.textContent = `Carbon Emission: ${emission.toFixed(2)} g CO2`;
        // Update tree images based on the emission value
        updateTreeImages(emission);*/

    });


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
