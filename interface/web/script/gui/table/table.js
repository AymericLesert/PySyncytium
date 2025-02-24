import { PSGUI } from '../gui.js';

class PSGUITable extends PSGUI {
    constructor() {
        super();

        this.psColumns = [];
        this.psKeys = [];
    }

    getAttributes() {
        super.getAttributes();

        let value = this.getAttribute('ps-columns');
        if (value != null)
            this.psColumns = value.split(",");

        value = this.getAttribute('ps-keys');
        if (value != null)
            this.psKeys = value.split(",");
    }

    drawWebComponent() {
        const div = document.createElement('div');
        const table = document.createElement('table');
        const tr = document.createElement('tr');
        for (let column of this.psColumns) {
            const th = document.createElement('th');
            th.textContent = column;
            tr.appendChild(th);
        }
        const thUpdate = document.createElement('th');
        tr.appendChild(thUpdate);
        const thDelete = document.createElement('th');
        tr.appendChild(thDelete);
        table.appendChild(tr);

        this.childNodes.forEach((node) => {
            let newLine = node.cloneNode(true);
            if (newLine.localName === "ps-gui-table-record") {
                let tr = document.createElement('tr');
                for (let column of this.psColumns) {
                    const td = document.createElement('td');
                    td.textContent = newLine.getAttribute("ps-col-" + column);
                    tr.appendChild(td);
                }
                let keys = [];
                for (let column of this.psKeys) {
                    keys.push(newLine.getAttribute("ps-col-" + column));
                }
                const tdUpdate = document.createElement('td');
                let ahref = document.createElement('a');
                ahref.href = "../update/" + this.psId + "/" + keys.join(",");
                ahref.textContent = "Mettre à jour";
                tdUpdate.appendChild(ahref);
                tr.appendChild(tdUpdate);
                const tdDelete = document.createElement('td');
                ahref = document.createElement('a');
                ahref.href = "../delete/" + this.psId + "/" + keys.join(",");
                ahref.textContent = "Supprimer";
                tdDelete.appendChild(ahref);
                tr.appendChild(tdDelete);
                table.appendChild(tr);
            }
            });
        div.appendChild(table);

        const btnAdd = document.createElement('button');
        btnAdd.setAttribute("type", "submit");
        btnAdd.textContent = "Ajouter";
        btnAdd.addEventListener('click', () => {
            console.log('Ajout : ' + '../insert/' + this.psId);
            window.location.href = '../insert/' + this.psId;
        });
        div.appendChild(btnAdd);

        const btnReturn = document.createElement('button');
        btnReturn.textContent = "Retour";
        btnReturn.addEventListener('click', () => {
            console.log('Retour');
            history.go(-1);
        });
        div.appendChild(btnReturn);

        return div;
    }

    drawStyleComponent() {
        return super.drawStyleComponent();
    }
};

export { PSGUITable };
