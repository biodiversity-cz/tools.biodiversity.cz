export default function dwcInputs() {
    const selectElement = document.getElementById('exportType');
    const dwcInpoutElements = document.getElementById('dwcInputs');
    if (selectElement) {
        selectElement.addEventListener('change', function () {
            dwcInpoutElements.style.display = this.value === 'dwc' ? 'flex' : 'none';
        });
    }
}