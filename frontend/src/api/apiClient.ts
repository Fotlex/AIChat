import axios from "axios";
import router from "@/router";

export const networkTracker = {
  activeRequests: 0,
  idleListeners: [] as (() => void)[],

  register() {
    this.activeRequests++;
  },

  deregister() {
    this.activeRequests = Math.max(0, this.activeRequests - 1);
    if (this.activeRequests === 0) {
      const listeners = [...this.idleListeners];
      this.idleListeners = [];
      listeners.forEach((cb) => cb());
    }
  },

  onIdle(cb: () => void) {
    if (this.activeRequests === 0) {
      cb();
    } else {
      this.idleListeners.push(cb);
    }
  },
};

const apiClient = axios.create({
  baseURL: "/api/v1/",
});

apiClient.interceptors.request.use((config) => {
  networkTracker.register();

  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    networkTracker.deregister();
    return response;
  },
  (error) => {
    networkTracker.deregister();

    if (error.response && error.response.status === 401) {
      localStorage.removeItem("access_token");
      router.push("/login");
    }
    return Promise.reject(error);
  },
);

export default apiClient;
