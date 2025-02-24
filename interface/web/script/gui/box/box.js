import { PSGUI } from '../gui.js';

class PSGUIBox extends PSGUI {
    constructor() {
        super();

        this.psMethod = "";
        this.psTable = "";
        this.psKeys = null;

        this.form = null;
    }

    getAttributes() {
        super.getAttributes();

        let value = this.getAttribute('ps-method');
        if (value != null)
            this.psMethod = value;

        value = this.getAttribute('ps-table');
        if (value != null)
            this.psTable = value;

        value = this.getAttribute('ps-keys');
        if (value != null)
            this.psKeys = value;
    }

    drawWebComponent() {
        this.form = document.createElement('form');

        let action = "/";
        if (this.psId !== null)
            action += this.psId + "/";
        action += this.psMethod + "/" + this.psTable;
        if (this.psKeys !== null)
            action += "/" + this.psKeys;
        this.form.setAttribute("action", action);
        this.form.setAttribute("method", "post");

        this.childNodes.forEach((node) => {
            let newNode = node.cloneNode(true);
            if (newNode.setAttribute)
                newNode.setAttribute("ps-method", this.psMethod);
            this.form.appendChild(newNode);
        });

        const btnCommit = document.createElement('button');
        btnCommit.setAttribute("type", "submit");
        switch (this.psMethod) {
            case "insert":
                btnCommit.textContent = "Créer";
                break;
            case "update":
                btnCommit.textContent = "Mettre à jour";
                break;
            case "delete":
                btnCommit.textContent = "Supprimer";
                break;
            default:
                btnCommit.textContent = "OK";
                break;
        }
        this.form.appendChild(btnCommit);

        const btnCancel = document.createElement('button');
        btnCancel.textContent = "Annuler";
        btnCancel.addEventListener('click', () => history.go(-1));
        this.form.appendChild(btnCancel);

        return this.form;
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

export { PSGUIBox };
