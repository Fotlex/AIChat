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

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token as string);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => {
    networkTracker.deregister();
    return response;
  },
  async (error) => {
    networkTracker.deregister();

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = "Bearer " + token;
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem("refresh_token");

      if (!refreshToken) {
        isRefreshing = false;
        router.push("/login");
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post("/api/v1/auth/refresh/", {
          refresh: refreshToken,
        });

        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);

        originalRequest.headers["Authorization"] = `Bearer ${data.access}`;

        processQueue(null, data.access);

        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        router.push("/login");
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default apiClient;
