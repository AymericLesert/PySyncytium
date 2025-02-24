import { PSGUI } from './gui/gui.js';
import { PSGUIField } from './gui/field/field.js';
import { PSGUIBox } from './gui/box/box.js';
import { PSGUIApplication } from './gui/application/application.js';
import { PSGUITable } from './gui/table/table.js';
import { PSGUITableRecord } from './gui/table/record.js';

customElements.define('ps-gui', PSGUI);
customElements.define('ps-gui-field', PSGUIField);
customElements.define('ps-gui-box', PSGUIBox);
customElements.define('ps-gui-application', PSGUIApplication);
customElements.define('ps-gui-table', PSGUITable);
customElements.define('ps-gui-table-record', PSGUITableRecord);
