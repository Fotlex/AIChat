import "@/assets/styles/global.css";

import { createApp } from "vue";
import App from "./App.vue";

import router from "./router";
import { setupRoutePrefetcher } from "./router/prefetcher";
import { createPinia } from "pinia";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

setupRoutePrefetcher(router);

app.mount("#app");
