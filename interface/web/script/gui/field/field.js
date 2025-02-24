import { PSGUI } from '../gui.js';

class PSGUIField extends PSGUI {
    static formAssociated = true;

    constructor() {
        super();

        this.psLabel = "";
        this.psDefaultValue = "";
        this.psValue = "";
        this.psMethod = null;

        this.psForm = this.attachInternals();
    }

    get value() {
        return this.psValue;
    }
    set value(newValue) {
        this.psValue = newValue;

        const entries = new FormData();
        entries.append(this.psId, this.psValue);
        this.psForm.setFormValue(entries);
    }

    getAttributes() {
        super.getAttributes();

        let value = this.getAttribute('ps-label');
        if (value != null)
            this.psLabel = value;

        value = this.getAttribute('ps-value');
        if (value != null)
            this.psDefaultValue = value;

        value = this.getAttribute('ps-method');
        if (value != null)
            this.psMethod = value;
    }

    drawWebComponent() {
        const div = document.createElement('div');

        const label = document.createElement('label');
        label.setAttribute("for", this.psId);
        label.textContent = this.psLabel + " :";
        div.appendChild(label);

        const input = document.createElement('input');
        input.setAttribute("type", "string");
        input.setAttribute("id", this.psId);
        input.setAttribute("name", this.psId);
        input.setAttribute("value", this.psDefaultValue);
        input.readOnly = this.psMethod === "delete";
        div.appendChild(input);

        this.value = this.psDefaultValue;
        input.addEventListener('change', () => {
            this.value = input.value;
        });

        return div;
    }

    drawStyleComponent() {
        return super.drawStyleComponent() +
            `div label {
                display:inline-block;
                width: 140px;
                text-align: right;
                margin-right: 10px;
            }\n`;
    }
};

export { PSGUIField };
