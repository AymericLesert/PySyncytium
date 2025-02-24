import { createApp } from 'vue';

import Application from './vue/application.vue.js';
import PSGUIApplication from './vue/application/application.js';

export const app = createApp(Application);

// register an options object
app.component('ps-gui-application', PSGUIApplication);
