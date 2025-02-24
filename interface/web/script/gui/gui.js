class PSGUI extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({ mode: 'open' });

        this.psId = null;
    }

    getAttributes() {
        let value = this.getAttribute('ps-id');
        if (value != null)
            this.psId = value;
    }

    drawWebComponent() {
        return null;
    }

    drawStyleComponent() {
        return "";
    }

    connectedCallback() {
        this.getAttributes();

        let styleComponent = this.drawStyleComponent();
        if (styleComponent !== null) {
            const style = document.createElement("style");
            style.textContent = this.drawStyleComponent();
            this.shadowRoot.appendChild(style);
        }

        const element = this.drawWebComponent();
        if (element !== null)
            this.shadowRoot.appendChild(element);
    }
}

export { PSGUI };