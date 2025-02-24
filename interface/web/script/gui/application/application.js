import { PSGUI } from '../gui.js';

class PSGUIApplication extends PSGUI {
    constructor() {
        super();
        this.psName = "";
    }

    getAttributes() {
        super.getAttributes();

        let value = this.getAttribute('ps-name');
        if (value != null)
            this.psName = value;
    }

    drawWebComponent() {
        const liElement = document.createElement('li');
        const aElement = document.createElement('a');
        aElement.href = "/" + this.psId + "/index.html";
        aElement.textContent = this.psName;
        liElement.appendChild(aElement);

        return liElement;
    }

    drawStyleComponent() {
        return super.drawStyleComponent() +
            `a { 
                color: #FF00FF
             }\n`;
    }
};

export { PSGUIApplication };
