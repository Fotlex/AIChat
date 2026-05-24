import type { Router } from "vue-router";
import { networkTracker } from "@/api/apiClient";

const scheduleIdle =
  window.requestIdleCallback ||
  ((cb) => {
    const start = Date.now();
    return setTimeout(() => {
      cb({
        didTimeout: false,
        timeRemaining: () => Math.max(0, 50 - (Date.now() - start)),
      });
    }, 1);
  });

export function setupRoutePrefetcher(router: Router) {
  const getLazyRoutes = () => {
    return router
      .getRoutes()
      .filter((route) => typeof route.components?.default === "function")
      .map((route) => ({
        name: String(route.name),
        load: route.components!.default as () => Promise<any>,
      }));
  };

  let queue: ReturnType<typeof getLazyRoutes> = [];
  let currentIndex = 0;
  let isPaused = false;
  let isFetching = false;
  let nextFrameId: number | null = null;

  const prefetchStep = () => {
    if (isPaused || isFetching || currentIndex >= queue.length) return;

    const currentRouteName = String(router.currentRoute.value.name);
    const item = queue[currentIndex]!;

    if (item.name === currentRouteName) {
      currentIndex++;
      prefetchStep();
      return;
    }

    isFetching = true;

    scheduleIdle((deadline) => {
      if (isPaused) {
        isFetching = false;
        return;
      }

      if (deadline.timeRemaining() > 0 && networkTracker.activeRequests === 0) {
        item.load().finally(() => {
          isFetching = false;
          currentIndex++;
          prefetchStep();
        });
      } else {
        isFetching = false;
        waitForIdleAndResume();
      }
    });
  };

  const waitForIdleAndResume = () => {
    if (isPaused) return;

    networkTracker.onIdle(() => {
      prefetchStep();
    });
  };

  const startPrefetch = () => {
    isPaused = false;
    waitForIdleAndResume();
  };

  const pausePrefetch = () => {
    isPaused = true;
    if (nextFrameId !== null) {
      cancelAnimationFrame(nextFrameId);
      nextFrameId = null;
    }
  };

  queue = getLazyRoutes();
  startPrefetch();

  router.beforeEach((_to, _from, next) => {
    pausePrefetch();
    next();
  });

  router.afterEach(() => {
    nextFrameId = requestAnimationFrame(() => {
      nextFrameId = requestAnimationFrame(() => {
        nextFrameId = null;
        startPrefetch();
      });
    });
  });
}
